import streamlit as st
import re
from difflib import SequenceMatcher

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="SellSmart AI",
    page_icon="💸",
    layout="centered"
)

# -----------------------------------
# SIDEBAR NAVIGATION (WORKS 100%)
# -----------------------------------
with st.sidebar:
    st.markdown("### 📄 Policies")
    st.page_link("pages/Terms.py", label="Terms of Service")
    st.page_link("pages/Privacy.py", label="Privacy Policy")
    st.page_link("pages/AUP.py", label="Acceptable Use")
    st.page_link("pages/Refunds.py", label="Refund Policy")

# -----------------------------------
# GLOBAL UI STYLING
# -----------------------------------
st.markdown("""
<style>

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

textarea {
    border-radius: 12px !important;
    border: 1px solid #3a3a3a !important;
    background-color: #111 !important;
    color: #e5e5e5 !important;
    padding: 12px !important;
    font-size: 15px !important;
}

.card {
    background-color: #0f0f0f;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 0 25px rgba(0, 255, 150, 0.15);
    margin-top: 20px;
    margin-bottom: 20px;
}

div.stButton > button {
    background: linear-gradient(90deg, #00ff9a, #00c26e);
    color: black;
    border-radius: 12px;
    padding: 12px 20px;
    font-size: 17px;
    font-weight: 600;
    border: none;
    width: 100%;
    transition: 0.2s ease-in-out;
}

div.stButton > button:hover {
    transform: scale(1.02);
    box-shadow: 0 0 20px rgba(0, 255, 150, 0.4);
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# HEADER WITH GLOW
# -----------------------------------
st.markdown("""
<style>
.logo-container {
    display: flex;
    justify-content: center;
    margin-top: 15px;
    margin-bottom: 5px;
}
.subtitle-glow {
    text-align: center;
    font-size: 20px;
    margin-top: 5px;
    color: #e5e7eb;
    text-shadow:
        0 0 6px rgba(0, 255, 150, 0.55),
        0 0 12px rgba(0, 255, 150, 0.35),
        0 0 18px rgba(0, 255, 150, 0.25);
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
st.image("image_1778389857310.jpeg", width=380)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<h3 class='subtitle-glow'>Create perfect Vinted listings in seconds</h3>", unsafe_allow_html=True)

# -----------------------------------
# FREE / PREMIUM SYSTEM
# -----------------------------------
STRIPE_LINK = "https://buy.stripe.com/eVqdR92ZvbSe5Ir8MXg3600"

if "uses" not in st.session_state:
    st.session_state["uses"] = 0

if "premium" not in st.session_state:
    st.session_state["premium"] = False

def check_paywall():
    if st.session_state["premium"]:
        return True

    if st.session_state["uses"] < 3:
        left = 3 - st.session_state["uses"]
        st.info(f"Free uses left today: {left}")
        return True

    st.error("You've reached your free limit (3 listings/day). Upgrade to Premium for unlimited use.")
    st.markdown(f"[💎 Upgrade to Premium]({STRIPE_LINK})")
    return False

# -----------------------------------
# ENGINE (YOUR FULL v3.3 ENGINE)
# -----------------------------------
# (ENGINE CODE OMITTED HERE FOR BREVITY — KEEP YOUR FULL ENGINE EXACTLY AS I GAVE IT)

# -----------------------------------
# INPUT CARD
# -----------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)

user_text = st.text_area(
    "Paste your messy item description:",
    height=150,
    placeholder="e.g. blue nike hoodie size L, worn a few times, small mark on sleeve"
)

generate = st.button("Generate Listing 💸", use_container_width=True)

# -----------------------------------
# GENERATE LISTING
# -----------------------------------
if generate:
    if check_paywall():
        st.session_state["uses"] += 1

        details = extract_details(user_text)
        title, description, tags = generate_listing(details)
        price = price_recommendation(
            details["brand"],
            details["condition"],
            has_flaws=bool(details["flaws"])
        )

        st.success("Listing generated successfully!")

        st.markdown("### 🏷️ Title")
        st.code(title)

        st.markdown("### 📝 Description")
        st.code(description)

        st.markdown("### 💷 Price Recommendation")
        st.code(price)

        st.markdown("### 🔖 Tags")
        st.code(tags)

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# FOOTER (NON-CLICKABLE)
# -----------------------------------
st.markdown("""
<hr style='margin-top:40px; margin-bottom:10px;'>

<div style='text-align:center; font-size:14px; color:#9ca3af;'>
    SellSmart AI © 2026 • Policies available in sidebar
</div>
""", unsafe_allow_html=True)
