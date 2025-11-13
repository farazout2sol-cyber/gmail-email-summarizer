import streamlit as st
import webbrowser
import os

# ==============================
# 🌤 PAGE SETUP
# ==============================
st.set_page_config(
    page_title="AI Email Summarizer | Smart Gmail Assistant",
    page_icon="📧",
    layout="wide"
)

# ==============================
# 🎨 STYLING + SMOOTH ANIMATION JS
# ==============================
st.markdown("""
<style>
/* --- RESET DEFAULT HEADER --- */
header[data-testid="stHeader"] { display: none; }

/* --- GLOBAL THEME --- */
html, body, [class*="stAppViewContainer"] {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
    scroll-behavior: smooth;
}

/* --- NAVBAR --- */
.navbar {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    backdrop-filter: blur(14px);
    background: rgba(255, 255, 255, 0.9);
    border-bottom: 1px solid rgba(0,0,0,0.05);
    color: #1a1a1a;
    padding: 0.7rem 3rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 9999;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    animation: fadeDown 0.8s ease;
}

.nav-left {
    font-size: 1.2rem;
    color: #4c54ff;
    font-weight: 700;
}

.nav-center a {
    color: #1a1a1a;
    text-decoration: none;
    margin: 0 1rem;
    font-weight: 600;
    font-size: 0.95rem;
    transition: all 0.3s ease;
    padding: 0.5rem 0.8rem;
    border-radius: 6px;
}
.nav-center a:hover, .nav-center a.active {
    background-color: rgba(76,84,255,0.1);
    color: #4c54ff;
    transform: translateY(-2px);
}

/* --- LOGIN / SIGNUP BUTTONS --- */
.nav-right button {
    border: none;
    background: linear-gradient(90deg, #4c54ff, #8b7fff);
    color: white;
    padding: 0.45rem 1rem;
    border-radius: 8px;
    margin-left: 0.8rem;
    cursor: pointer;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.3s ease;
}
.nav-right button:hover {
    background: linear-gradient(90deg, #5b63ff, #9d8fff);
    transform: translateY(-2px);
}

/* --- HERO SECTION --- */
.hero {
    padding: 8rem 2rem 4rem 2rem;
    text-align: center;
    max-width: 1100px;
    margin: auto;
    border-radius: 20px;
    animation: fadeIn 1s ease-in;
}
.hero h1 {
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
    color: #111;
}
.hero p {
    color: #444;
    font-size: 1.2rem;
    max-width: 750px;
    margin: auto;
    line-height: 1.6;
}
.hero img {
    margin-top: 2rem;
    transition: transform 0.4s ease;
}
.hero img:hover { transform: scale(1.08); }

/* --- SECTION STYLING --- */
.section {
    padding: 5rem 2rem 4rem 2rem;
    max-width: 1150px;
    margin: auto;
    text-align: center;
}
.section h2 {
    font-size: 2.3rem;
    font-weight: 700;
    margin-bottom: 2rem;
    color: #222;
}

/* --- FEATURE CARD --- */
.feature-card {
    background: #f9f9fb;
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 0 20px rgba(0,0,0,0.05);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    height: 100%;
}
.feature-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 0 30px rgba(76,84,255,0.15);
}

/* --- ABOUT SECTION --- */
.about {
    background: #f5f6ff;
    border-radius: 20px;
    padding: 5rem 2rem;
    margin: 5rem auto;
    max-width: 1100px;
}

/* --- TESTIMONIALS --- */
.testimonial {
    background: #f9f9fb;
    border-radius: 15px;
    padding: 2rem;
    font-style: italic;
    color: #333;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    min-height: 180px;
}
.testimonial span {
    display: block;
    margin-top: 1rem;
    font-weight: 600;
    color: #4c54ff;
}

/* --- FOOTER --- */
.footer {
    background: #fafafa;
    text-align: center;
    padding: 2rem 1rem;
    font-size: 0.9rem;
    color: #666;
    border-top: 1px solid rgba(0,0,0,0.05);
    margin-top: 5rem;
}

/* --- ANIMATIONS --- */
@keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fadeDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
</style>

<!-- 🔥 SMOOTH SCROLLING JS -->
<script>
document.addEventListener("DOMContentLoaded", function() {
  const links = document.querySelectorAll('.nav-center a');
  links.forEach(link => {
    link.addEventListener("click", function(e) {
      e.preventDefault();
      const id = this.getAttribute("href").substring(1);
      const target = document.getElementById(id);
      if (target) {
        window.scrollTo({ top: target.offsetTop - 60, behavior: "smooth" });
      }
    });
  });
});
</script>
""", unsafe_allow_html=True)

# ==============================
# 🧭 NAVBAR
# ==============================
st.markdown("""
<div class="navbar">
  <div class="nav-left"><b>📧 AI Email Summarizer</b></div>
  <div class="nav-center">
    <a href="#home">Home</a>
    <a href="#features">Features</a>
    <a href="#about">About</a>
    <a href="#how-it-works">How It Works</a>
    <a href="#testimonials">Testimonials</a>
    <a href="#contact">Contact</a>
</div>
""", unsafe_allow_html=True)

# ==============================
# 🏠 HERO SECTION
# ==============================
st.markdown('<div id="home" class="hero">', unsafe_allow_html=True)
st.markdown("## ✨ Smart. Fast. Organized.")
st.markdown("<h1>Turn Your Inbox into an Intelligent Assistant</h1>", unsafe_allow_html=True)
st.write("""
AI Email Summarizer helps you **cut through email overload**.  
Let Gemini-powered intelligence read, summarize, and organize your Gmail —  
so you can focus on action, not clutter.
""")

# ✅ Combined Launch System (from your second version)
if st.button("🚀 Launch Summarizer App", key="launch", use_container_width=True):
    app_path = os.path.abspath("app2.py")
    if os.path.exists(app_path):
        # os.system("start /B streamlit run app2.py")  # for Windows
        st.success("🚀 Opening Summarizer App in a new tab...")
        webbrowser.open_new_tab("http://localhost:8502")
    else:
        st.error("❌ app2.py not found. Please make sure it’s in the same folder.")

st.image("https://cdn-icons-png.flaticon.com/512/906/906349.png", width=120)
st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# ⚙️ FEATURES
# ==============================
st.markdown('<div id="features" class="section">', unsafe_allow_html=True)
st.header("Powerful Features")
features = [
    ("📥 Gmail Integration", "Connect securely with Gmail via OAuth for real-time message processing."),
    ("🧠 Gemini AI Summarization", "Uses Google's **Gemini AI** to generate concise, actionable summaries."),
    ("📊 Organized Insights", "Automatically groups messages by priority, sender, and topic."),
    ("💾 Smart Backup", "Saves summaries in Google Sheets or JSON for future use."),
    ("📤 Daily Digest Reports", "Receive AI-generated daily summaries in your inbox."),
    ("🔒 Privacy by Design", "Your emails remain private — never shared or stored externally.")
]
cols = st.columns(3)
for i, (title, desc) in enumerate(features):
    with cols[i % 3]:
        st.markdown(f"""<div class="feature-card"><h3>{title}</h3><p>{desc}</p></div>""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# ℹ️ ABOUT
# ==============================
st.markdown('<div id="about" class="about">', unsafe_allow_html=True)
st.header("About AI Email Summarizer")
st.write("""
**AI Email Summarizer** is your smart inbox companion for productivity professionals.  
Using **Gemini AI**, it reads and summarizes your emails while preserving privacy —  
letting you take quick, informed decisions without reading long threads.
""")
st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# ⚙️ HOW IT WORKS
# ==============================
st.markdown('<div id="how-it-works" class="section">', unsafe_allow_html=True)
st.header("How It Works ⚙️")
steps = [
    ("1️⃣ Connect", "Authenticate securely with Gmail using Google OAuth."),
    ("2️⃣ Fetch", "Emails are fetched safely with full privacy."),
    ("3️⃣ Summarize", "Gemini AI processes each email for meaning and key points."),
    ("4️⃣ Deliver", "Results are displayed instantly or sent to your inbox daily.")
]
cols = st.columns(4)
for i, (step, desc) in enumerate(steps):
    with cols[i]:
        st.markdown(f"""<div class="feature-card"><h3>{step}</h3><p>{desc}</p></div>""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# 💬 TESTIMONIALS
# ==============================
st.markdown('<div id="testimonials" class="section">', unsafe_allow_html=True)
st.header("What Users Say 💬")
reviews = [
    ("“Finally, an AI that actually saves me time. My inbox feels lighter!”", "— Sarah Khan, Product Manager"),
    ("“Gemini summaries are accurate and concise. I get the point instantly.”", "— Ahmed Raza, Marketing Lead"),
    ("“Seamless integration with Gmail. Absolute productivity booster.”", "— Emma Li, Freelancer")
]
cols = st.columns(3)
for i, (quote, name) in enumerate(reviews):
    with cols[i]:
        st.markdown(f"""<div class="testimonial">{quote}<span>{name}</span></div>""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# 📬 CONTACT + FOOTER
# ==============================
st.markdown('<div id="contact" class="section">', unsafe_allow_html=True)
st.header("Get in Touch 💬")
with st.form("contact_form"):
    name = st.text_input("Your Name", placeholder="Enter your full name")
    email = st.text_input("Your Email", placeholder="example@email.com")
    message = st.text_area("Your Message", placeholder="Type your message here...")
    submit = st.form_submit_button("📨 Send Message")
    if submit:
        if name and email and message:
            st.success(f"✅ Thanks {name}! Your message has been received.")
        else:
            st.error("⚠️ Please fill out all fields before submitting.")
st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# 🔚 FOOTER
# ==============================
st.markdown("""
<div class="footer">
    © 2025  | Powered by Gemini • Gmail API • LangGraph • Streamlit
</div>
""", unsafe_allow_html=True)
