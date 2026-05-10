import streamlit as st
import re
from difflib import SequenceMatcher

# -----------------------------------
# SELL SMART AI – v2.0
# Free: 3 listings/day
# Premium: Unlimited
# -----------------------------------

STRIPE_LINK = "https://buy.stripe.com/eVqdR92ZvbSe5Ir8MXg3600"

# Track usage
if "uses" not in st.session_state:
    st.session_state["uses"] = 0

if "premium" not in st.session_state:
    st.session_state["premium"] = False

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="SellSmart AI",
    page_icon="💸",
    layout="centered"
)

# -----------------------------------
# HEADER WITH GLOW LOGO + GLOW SUBTITLE
# -----------------------------------

st.markdown("""
<style>

.logo-container {
    display: flex;
    justify-content: center;
    margin-top: 15px;
    margin-bottom: 5px;
}

.logo-glow {
    width: 380px;
    border-radius: 14px;
    box-shadow:
        0 0 35px rgba(0, 255, 150, 0.75),
        0 0 75px rgba(0, 255, 150, 0.55),
        0 0 120px rgba(0, 255, 150, 0.45);
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

# LOGO
st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
st.image("image_1778389857310.jpeg", width=380)
st.markdown("</div>", unsafe_allow_html=True)

# SUBTITLE
st.markdown("<h3 class='subtitle-glow'>Create perfect Vinted listings in seconds</h3>", unsafe_allow_html=True)
st.write("")

# -----------------------------------
# PAYWALL CHECK
# -----------------------------------
def check_paywall():
    if st.session_state["premium"]:
        return True

    if st.session_state["uses"] < 3:
        left = 3 - st.session_state["uses"]
        st.info(f"Free uses left today: {left}")
        return True

    st.error("You’ve reached your free limit (3 listings/day). Upgrade to Premium for unlimited use.")
    st.markdown(f"[💎 Upgrade to Premium]({STRIPE_LINK})")
    return False

# -----------------------------------
# BRAND DETECTION
# -----------------------------------
BRANDS = [
    "nike","adidas","puma","reebok","asics","under armour","gymshark","champion","fila","new balance",
    "converse","vans","salomon","north face","patagonia","columbia","supreme","palace","stussy",
    "carhartt","dickies","bape","off-white","essentials","trapstar","hoodrich","siksilk","represent",
    "corteiz","armani","hugo boss","calvin klein","ck","tommy hilfiger","ralph lauren","lacoste",
    "burberry","stone island","moncler","diesel","guess","levi","versace","kenzo","allsaints",
    "ted baker","gucci","prada","louis vuitton","balenciaga","dior","ysl","fendi","valentino",
    "celine","loewe","givenchy","hermes","bottega veneta","zara","h&m","cos","weekday","mango",
    "pull&bear","bershka","stradivarius","river island","new look","primark","asos","plt","shein",
    "oh polly","house of cb","clarks","birkenstock","crocs","timberland","yeezy","jordan","ugg"
]

def fuzzy_ratio(a, b):
    return SequenceMatcher(None, a, b).ratio()

def best_match_brand(text):
    text = text.lower()
    words = text.split()
    best = "Unknown"
    score = 0

    for brand in BRANDS:
        if brand in text:
            return brand.title()

        for w in words:
            r = fuzzy_ratio(w, brand)
            if r > score and r > 0.78:
                score = r
                best = brand

    return best.title()

# -----------------------------------
# PRICE ESTIMATOR
# -----------------------------------
def estimate_price(brand, item):
    brand = brand.lower()
    base_low, base_high = 4, 8

    high_brands = ["nike","adidas","north face","stone island","moncler","jordan","yeezy","ralph lauren"]
    budget_brands = ["primark","shein","new look","george","matalan"]

    if any(b in brand for b in high_brands):
        base_low, base_high = 12, 25
    elif any(b in brand for b in budget_brands):
        base_low, base_high = 3, 7

    if item in ["hoodie","jacket","coat","jeans","tracksuit"]:
        base_low += 3
        base_high += 5

    return f"£{base_low:.0f}.00 - £{base_high:.0f}.00"

# -----------------------------------
# INPUT
# -----------------------------------
user_text = st.text_area(
    "Paste your messy item description:",
    height=150,
    placeholder="e.g. blue primark shorts size 10 worn a few times"
)

generate = st.button("Generate Listing 💸", use_container_width=True)

# -----------------------------------
# GENERATOR
# -----------------------------------
if generate:
    if check_paywall():
        st.session_state["uses"] += 1

        text = user_text.lower().strip()
        words = text.split()

        # Detect brand
        brand = best_match_brand(text)

        # Detect colour
        colours = [
            "black","white","grey","gray","blue","navy","red","green","yellow","pink","purple",
            "brown","beige","cream","orange","burgundy","khaki","tan","teal"
        ]
        colour = next((w for w in words if w in colours), "")

        # Detect item type
        items = [
            "shorts","shirt","tshirt","t-shirt","hoodie","jacket","coat","jeans","trousers",
            "leggings","skirt","dress","top","jumper","sweater","cargo","joggers","tracksuit"
        ]
        item = next((w for w in words if w in items), "item")

        # Detect condition
        condition_label = "Good used condition"
        if "new" in text or "with tags" in text:
            condition_label = "Brand new / with tags"
        elif "like new" in text or "worn once" in text:
            condition_label = "Excellent condition"
        elif "worn" in text or "used" in text:
            condition_label = "Used but still in good wearable condition"

        # Build title
        title = " ".join([
            brand if brand != "Unknown" else "",
            colour.capitalize() if colour else "",
            item.capitalize()
        ]).strip()

        # Build description
        description = (
            f"{title}.\n\n"
            f"{condition_label}. No major flaws unless stated. "
            "Perfect for everyday wear and easy to style.\n\n"
            "From a smoke-free home. Fast dispatch."
        )

        # Tags
        tags = [t for t in [brand, colour, item, "fashion", "vinted", "sellsmart"] if t]

        # Price
        price = estimate_price(brand, item)

        # Output
        st.success("Listing generated successfully!")

        st.markdown("### 🏷️ Title")
        st.code(title)

        st.markdown("### 📝 Description")
        st.code(description)

        st.markdown("### 🔖 Tags")
        st.code(", ".join(tags))

        st.markdown("### 💷 Suggested Price")
        st.code(price)

        st.info("Tip: long‑press to copy on mobile, or right‑click → copy on desktop.")
st.markdown("""
<hr style='margin-top:40px; margin-bottom:10px;'>

<div style='text-align:center; font-size:14px; color:#9ca3af;'>
    SellSmart AI © 2026<br>
    <a href='#' onclick="window.open('/terms', '_blank')">Terms of Service</a> •
    <a href='#' onclick="window.open('/privacy', '_blank')">Privacy Policy</a> •
    <a href='#' onclick="window.open('/aup', '_blank')">Acceptable Use</a> •
    <a href='#' onclick="window.open('/refunds', '_blank')">Refund Policy</a>
</div>
""", unsafe_allow_html=True)
