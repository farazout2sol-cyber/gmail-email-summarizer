import os
import json
import base64
import tempfile
from datetime import datetime
from typing import TypedDict, List

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from st_aggrid import AgGrid, GridOptionsBuilder

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from email.mime.text import MIMEText

from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI

# ===============================
# 🌙 Modern Dark Theme
# ===============================
st.set_page_config(page_title="📧 AI Email Summarizer + Sender", page_icon="🤖", layout="wide")
st.markdown("""
<style>
html, body, [class*="stAppViewContainer"] { background-color: #1c1f28; color: #f8f9fb; font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;}
[data-testid="stHeader"] { background: #252934; border-bottom: 1px solid rgba(128,128,128,0.25);}
section[data-testid="stSidebar"] { background-color: #252934; border-right: 1px solid rgba(128,128,128,0.25);}
div.stButton > button { background: linear-gradient(90deg, #5b63ff, #8b7fff); color: white; border: none; border-radius: 10px; padding: 0.7rem 1.4rem; font-weight: 600; transition: all 0.3s ease;}
div.stButton > button:hover { background: linear-gradient(90deg, #8b7fff, #5b63ff); box-shadow: 0 0 12px rgba(125,130,255,0.5); transform: scale(1.03);}
.stContainer { background: #252934; border: 1px solid rgba(128,128,128,0.25); border-radius: 16px; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.15);}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ===============================
# 📦 Load Environment & Secrets
# ===============================
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Optional for other Google APIs

# ===============================
# 🧠 Gemini Model Setup
# ===============================
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
SYSTEM_PROMPT = """
You are an intelligent assistant that summarizes email content clearly.
1. Read the email carefully.
2. Write a short 1–2 line summary.
3. Assign a priority: High, Medium, or Low.
Format:
Summary: <summary>
Priority: <priority>
"""

# ===============================
# 🔐 Gmail Login (using Streamlit Secrets)
# ===============================
def gmail_login():
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid"
    ]

    import tempfile
    import json

    # Use secret.toml [em] or fallback to local Em.json
    if "em" in st.secrets:
        client_secrets = st.secrets["em"]
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as f:
            json.dump(client_secrets, f)
            client_secrets_path = f.name
    else:
        client_secrets_path = "Em.json"

    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
    creds = flow.run_local_server(port=0)

    # Save token to a temp file
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as token_file:
        token_file.write(creds.to_json())
        token_path = token_file.name

    # Fetch user email
    user_info_service = build("oauth2", "v2", credentials=creds)
    user_info = user_info_service.userinfo().get().execute()
    email = user_info.get("email")

    return email, token_path

# ===============================
# 🔒 Login Page
# ===============================
if "user_email" not in st.session_state:
    st.title("🔐 Login to Continue")
    st.write("Please sign in with your Gmail account to summarize your latest emails.")
    if st.button("Sign in with Google", use_container_width=True):
        try:
            email, token_path = gmail_login()
            st.session_state["user_email"] = email
            st.session_state["token_path"] = token_path
            st.success(f"✅ Logged in as {email}")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Login failed: {e}")
    st.stop()

st.sidebar.markdown(f"👤 **Logged in as:** {st.session_state['user_email']}")

# ===============================
# 🧩 LangGraph State
# ===============================
class EmailState(TypedDict):
    emails: List[str]
    optimized_emails: List[str]

# ===============================
# 📥 Fetch Emails Node
# ===============================
def fetch_emails_node(state: EmailState):
    token_path = st.session_state.get("token_path")
    creds = Credentials.from_authorized_user_file(token_path, ["https://www.googleapis.com/auth/gmail.readonly"])
    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(userId="me", maxResults=5).execute()
    messages = results.get("messages", [])
    emails = []

    for msg in messages:
        msg_detail = service.users().messages().get(userId="me", id=msg["id"]).execute()
        snippet = msg_detail.get("snippet", "")
        emails.append(snippet)

    state["emails"] = emails
    return state

# ===============================
# 🧠 Summarize Emails Node
# ===============================
def optimize_emails_node(state: EmailState):
    summaries = []
    for email in state["emails"]:
        prompt = f"{SYSTEM_PROMPT}\n\nEmail:\n{email}"
        response = model.invoke(prompt)

        # Convert AttrDict -> string
        text = ""
        if hasattr(response, "content"):
            content_attr = response.content
            if isinstance(content_attr, list) and len(content_attr) > 0:
                text = getattr(content_attr[0], "text", str(content_attr[0]))
            else:
                text = str(content_attr)
        else:
            text = str(response)

        summaries.append(text)

    state["optimized_emails"] = summaries
    return state

# ===============================
# 💾 Save to Google Sheets + JSON Backup
# ===============================
def save_to_sheets_node(state: EmailState):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Load credentials from Streamlit secrets
    import tempfile
    if "gsheet" in st.secrets:
        creds_dict = st.secrets["gsheet"]
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as f:
            json.dump(creds_dict, f)
            gsheet_path = f.name
        creds = ServiceAccountCredentials.from_json_keyfile_name(gsheet_path, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("gsheet_credentials.json", scope)

    client = gspread.authorize(creds)

    try:
        sheet = client.open("Email Summaries").sheet1
    except Exception:
        sheet = None

    data_to_save = []
    for item in state["optimized_emails"]:
        summary, priority = "", "Unknown"
        for line in item.splitlines():
            if line.lower().startswith("summary:"):
                summary = line.replace("Summary:", "").strip()
            elif line.lower().startswith("priority:"):
                priority = line.replace("Priority:", "").strip()
        data_to_save.append({"Summary": summary, "Priority": priority})
        if sheet:
            try:
                sheet.append_row([summary, priority])
            except Exception:
                pass

    os.makedirs("backups", exist_ok=True)
    filename = f"backups/email_summaries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, indent=2, ensure_ascii=False)

    st.session_state["latest_backup"] = filename
    return state

# ===============================
# ✉️ Email Sender
# ===============================
class EmailSender:
    def __init__(self, token_path=None):
        if token_path is None:
            token_path = st.session_state.get("token_path")
        self.SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
        self.creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        self.service = build("gmail", "v1", credentials=self.creds)

    def send_summary_email(self, to_email: str, summaries: list[dict]):
        body_lines = ["📬 Here are your summarized emails:\n"]
        for i, s in enumerate(summaries, start=1):
            s_lower = {k.lower(): v for k, v in s.items()}
            summary_text = s_lower.get("summary", "N/A")
            priority_text = s_lower.get("priority", "Unknown")
            body_lines.append(f"📨 Email {i}")
            body_lines.append(f"Summary: {summary_text}")
            body_lines.append(f"Priority: {priority_text}\n")
        body = "\n".join(body_lines)
        message = MIMEText(body, "plain")
        message["to"] = to_email
        message["subject"] = "📧 Your Summarized Emails"
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        self.service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        return {"status": "success", "recipient": to_email, "count": len(summaries)}

# ===============================
# 🚀 LangGraph Workflow
# ===============================
graph = StateGraph(EmailState)
graph.add_node("FetchEmails", fetch_emails_node)
graph.add_node("OptimizeEmails", optimize_emails_node)
graph.add_node("SaveToSheets", save_to_sheets_node)
graph.add_edge(START, "FetchEmails")
graph.add_edge("FetchEmails", "OptimizeEmails")
graph.add_edge("OptimizeEmails", "SaveToSheets")
graph.add_edge("SaveToSheets", END)
app_graph = graph.compile()

# ===============================
# 🧭 Main UI
# ===============================
with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    st.info("Use the buttons below to fetch, summarize, and send your Gmail summaries.")
    fetch_clicked = st.button("🚀 Fetch & Summarize My Gmail", use_container_width=True)

if fetch_clicked:
    with st.spinner("Processing your last 5 emails... 🧠"):
        state = app_graph.invoke({})
    st.session_state["summary_data"] = []

    st.subheader("📥 Last 5 Gmail Messages (Fetched)")
    email_table = pd.DataFrame({"No.": range(1, len(state["emails"]) + 1), "Email Snippet": state["emails"]})
    gb = GridOptionsBuilder.from_dataframe(email_table)
    gb.configure_default_column(wrapText=True, autoHeight=True, resizable=True)
    AgGrid(email_table, gridOptions=gb.build(), theme="material", height=250)

    summaries = []
    for text in state["optimized_emails"]:
        summary, priority = "", "Unknown"
        for line in text.splitlines():
            if line.lower().startswith("summary:"):
                summary = line.replace("Summary:", "").strip()
            elif line.lower().startswith("priority:"):
                priority = line.replace("Priority:", "").strip()
        summaries.append({"No.": len(summaries) + 1, "Summary": summary, "Priority": priority})
    st.session_state["summary_data"] = summaries

    st.subheader("🧠 Summarized Results")
    summary_df = pd.DataFrame(summaries)
    gb2 = GridOptionsBuilder.from_dataframe(summary_df)
    gb2.configure_default_column(wrapText=True, autoHeight=True)
    AgGrid(summary_df, gridOptions=gb2.build(), theme="balham", height=250)

    if st.session_state.get("latest_backup"):
        st.success(f"💾 Saved to: {st.session_state['latest_backup']}")

# Send Summaries
if st.session_state.get("summary_data"):
    st.markdown("---")
    st.subheader("📤 Send Summarized Report")
    user_email = st.text_input("Enter your email address:", placeholder="e.g. yourname@gmail.com", value=st.session_state["user_email"])
    if st.button("📨 Send to My Inbox", use_container_width=True):
        try:
            sender = EmailSender()
            result = sender.send_summary_email(user_email, st.session_state["summary_data"])
            st.success(f"✅ Sent to {result['recipient']} ({result['count']} summaries)")
        except Exception as e:
            st.error(f"❌ Failed to send: {e}")

st.caption("✨ Developed by Faraz Uddin Zafar | Powered by Gemini + Gmail API + LangGraph + Streamlit + AgGrid")
