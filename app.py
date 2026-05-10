import streamlit as st
import re
from difflib import SequenceMatcher

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="SellSmart AI",
    page_icon="💸",
    layout="centered"
)

# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 📄 Policies")
    st.page_link("pages/Terms.py", label="Terms of Service")
    st.page_link("pages/Privacy.py", label="Privacy Policy")
    st.page_link("pages/AUP.py", label="Acceptable Use")
    st.page_link("pages/Refunds.py", label="Refund Policy")

# ---------------------------------------------------------
# PREMIUM GLASS UI STYLING
# ---------------------------------------------------------
st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: #0d0d0d !important;
}

/* Frosted Glass Card */
.glass-card {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 18px;
    padding: 28px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 0 25px rgba(0, 255, 150, 0.12);
    margin-top: 20px;
}

/* Pulse Button */
div.stButton > button {
    background: linear-gradient(90deg, #00ff9a, #00c26e);
    color: black;
    border-radius: 14px;
    padding: 14px 20px;
    font-size: 18px;
    font-weight: 600;
    border: none;
    width: 100%;
    animation: pulse 2.2s infinite ease-in-out;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0px rgba(0,255,150,0.4); }
    50% { box-shadow: 0 0 18px rgba(0,255,150,0.7); }
    100% { box-shadow: 0 0 0px rgba(0,255,150,0.4); }
}

/* Textarea */
textarea {
    background: rgba(255,255,255,0.06) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #e5e5e5 !important;
    padding: 12px !important;
    font-size: 15px !important;
}

/* Header Glow */
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

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.image("image_1778389857310.jpeg", width=380)
st.markdown("<h3 class='subtitle-glow'>Smarter listings. More sales. Less effort.</h3>", unsafe_allow_html=True)

# ---------------------------------------------------------
# PAYWALL SYSTEM
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# v4 ENGINE — SMARTER, CLEANER, MORE ACCURATE
# ---------------------------------------------------------

def extract_details(text):
    text = text.lower()

    brands = ["nike", "adidas", "ralph lauren", "polo", "north face", "zara", "hollister", "tommy hilfiger"]
    brand = next((b for b in brands if b in text), "Unknown")

    colours = ["red", "blue", "black", "white", "green", "grey", "pink", "yellow", "purple"]
    colour = next((c for c in colours if c in text), "Unknown")

    conditions = {
        "new": ["new", "unused", "with tags"],
        "excellent": ["excellent", "like new"],
        "good": ["good", "worn a few times"],
        "fair": ["fair", "used", "worn"],
    }
    condition = "Good"
    for label, words in conditions.items():
        if any(w in text for w in words):
            condition = label.capitalize()

    flaws = ""
    flaw_keywords = ["mark", "stain", "rip", "hole", "faded"]
    for f in flaw_keywords:
        if f in text:
            flaws = f"Has a minor {f}."

    size_match = re.search(r"\b(xs|s|m|l|xl|xxl)\b", text)
    size = size_match.group(0).upper() if size_match else "Unknown"

    return {
        "brand": brand,
        "colour": colour,
        "condition": condition,
        "size": size,
        "flaws": flaws
    }

def generate_listing(details):
    title = f"{details['brand'].title()} {details['colour'].title()} Polo Shirt - {details['size']}"

    description = (
        f"{details['brand'].title()} polo shirt in a clean {details['colour']} colourway. "
        f"Condition: {details['condition']}. "
    )

    if details["flaws"]:
        description += f"{details['flaws']} "

    description += "Fast dispatch. Trusted seller."

    tags = f"#{details['brand'].replace(' ', '')} #{details['colour']} #polo #menswear #fashion"

    return title, description, tags

def price_recommendation(brand, condition, has_flaws=False):
    base_prices = {
        "nike": 12,
        "adidas": 12,
        "ralph lauren": 18,
        "polo": 18,
        "north face": 20,
        "zara": 10,
        "hollister": 10,
        "tommy hilfiger": 16,
        "unknown": 8
    }

    price = base_prices.get(brand, 10)

    if condition == "Excellent":
        price += 4
    elif condition == "Good":
        price += 2
    elif condition == "Fair":
        price -= 2

    if has_flaws:
        price -= 2

    return f"£{max(price, 4)}"

# ---------------------------------------------------------
# INPUT CARD
# ---------------------------------------------------------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

user_text = st.text_area(
    "Paste your item description:",
    height=150,
    placeholder="e.g. red ralph lauren polo worn a few years"
)

generate = st.button("Generate Listing 💸", use_container_width=True)

# ---------------------------------------------------------
# GENERATE LISTING
# ---------------------------------------------------------
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

        st.success("Listing generated!")

        st.markdown("### 🏷️ Title")
        st.code(title)

        st.markdown("### 📝 Description")
        st.code(description)

        st.markdown("### 💷 Price Recommendation")
        st.code(price)

        st.markdown("### 🔖 Tags")
        st.code(tags)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("""
<hr style='margin-top:40px; margin-bottom:10px;'>
<div style='text-align:center; font-size:14px; color:#9ca3af;'>
    SellSmart AI © 2026 • Policies available in sidebar
</div>
""", unsafe_allow_html=True)
