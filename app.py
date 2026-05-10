import streamlit as st
import re
from difflib import SequenceMatcher

# -----------------------------------
# SELL SMART AI – PREMIUM APP
# Free plan: 3 listings/day
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

# Premium UI styling
st.markdown("""
<style>
body {background-color: #f0f2f6;}
.big-title {font-size: 40px; font-weight: 800; text-align: center; color: #2b2b2b;}
.sub {font-size: 20px; text-align: center; color: #666;}
.box {background: white; padding: 25px; border-radius: 14px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);}
.output-box {background: #fafafa; padding: 20px; border-radius: 12px; border: 1px solid #ddd;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='big-title'>SellSmart AI</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>Create perfect Vinted listings in seconds</div>", unsafe_allow_html=True)
st.write("")

# -----------------------------------
# PAYWALL CHECK
# -----------------------------------
def check_paywall():
    if st.session_state["premium"]:
        return True

    if st.session_state["uses"] < 3:
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
            if r > score and r > 0.75:
                score = r
                best = brand

    return best.title()

# -----------------------------------
# INPUT BOX
# -----------------------------------
st.markdown("<div class='box'>", unsafe_allow_html=True)
user_text = st.text_area("Paste your messy item description:", height=180)

if st.button("Generate Listing 💸"):
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

        # Build title
        title = f"{brand} {colour.capitalize()} {item.capitalize()}".strip()

        # Build description
        description = (
            f"{brand} {item} in {colour} colour. "
            "Great condition with no major flaws. "
            "Perfect for everyday wear and super comfortable. "
            "Fast dispatch and smoke-free home."
        )

        # Tags
        tags = [brand, colour, item, "fashion", "vinted", "sellsmart"]

        # Price suggestion
        price = "£4.00 - £8.00"

        # Output
        st.success("Listing generated successfully!")
        st.markdown("<div class='output-box'>", unsafe_allow_html=True)
        st.markdown(f"### 🏷️ Title\n{title}")
        st.markdown(f"### 📝 Description\n{description}")
        st.markdown(f"### 🔖 Tags\n{', '.join(tags)}")
        st.markdown(f"### 💷 Suggested Price\n{price}")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
