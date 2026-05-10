import streamlit as st
import time
import re
from difflib import SequenceMatcher

# -----------------------------
# SELL SMART AI – PREMIUM APP
# Free plan: 3 listings/day
# Premium: Unlimited
# -----------------------------

STRIPE_LINK = "https://buy.stripe.com/eVqdR92ZvbSe5Ir8MXg3600"

# Track usage in session
if "uses" not in st.session_state:
    st.session_state["uses"] = 0

if "premium" not in st.session_state:
    st.session_state["premium"] = False

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="SellSmart AI",
    page_icon="💸",
    layout="centered"
)

st.markdown("""
<style>
body {background-color: #f5f5f5;}
.big-title {font-size: 36px; font-weight: 700; text-align: center;}
.sub {font-size: 18px; text-align: center; color: #555;}
.box {background: white; padding: 20px; border-radius: 12px; box-shadow: 0 0 10px rgba(0,0,0,0.1);}
.button {font-size: 20px; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='big-title'>SellSmart AI</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>Create perfect Vinted listings in seconds</div>", unsafe_allow_html=True)
st.write("")

# -----------------------------
# PAYWALL CHECK
# -----------------------------
def check_paywall():
    if st.session_state["premium"]:
        return True

    if st.session_state["uses"] < 3:
        return True

    st.error("You’ve reached your free limit (3 listings/day). Upgrade to Premium for unlimited use.")
    st.markdown(f"[💎 Upgrade to Premium]({STRIPE_LINK})")
    return False

# -----------------------------
# V3.3 WORKER FUNCTIONS
# -----------------------------

BRANDS = {
    "sportswear": ["nike","adidas","puma","reebok","asics","under armour","gymshark","champion","fila","new balance","converse","vans","salomon","the north face","north face","patagonia","columbia","umbro","lotto","kappa"],
    "streetwear": ["supreme","palace","stussy","carhartt","dickies","obey","bape","a bathing ape","off-white","essentials","trapstar","hoodrich","siksilk","11 degrees","represent","corteiz","huf","billionaire boys club"],
    "designer": ["armani","emporio armani","giorgio armani","hugo boss","boss","calvin klein","ck","tommy hilfiger","ralph lauren","polo ralph lauren","lacoste","burberry","stone island","canada goose","moncler","diesel","guess","levi","levis","versace","kenzo","paul smith","allsaints","ted baker"],
    "luxury": ["gucci","prada","louis vuitton","lv","balenciaga","dior","ysl","saint laurent","fendi","valentino","celine","loewe","maison margiela","givenchy","hermes","bottega veneta"],
    "high_street": ["zara","zara man","zara woman","h&m","cos","weekday","monki","mango","pull&bear","bershka","stradivarius","river island","new look","primark","george","matalan","next","topman","topshop","asos","asos design","boohoo","boohoo man","prettylittlething","plt","missguided","shein","oh polly","house of cb","lipsy","coast","jack & jones","only & sons","selected homme"],
    "outdoor": ["regatta","berghaus","craghoppers","helly hansen","rab","jack wolfskin","mountain warehouse","columbia","sprayway"],
    "footwear": ["dr martens","doc martens","ugg","clarks","birkenstock","crocs","timberland","yeezy","jordan","nike air max","adidas originals","air force 1","air jordan","new balance"],
    "kids": ["mothercare","jojo maman bébé","mini boden","boden","m&s kids","marks & spencer","george kids","next kids"]
}

ALL_BRANDS = sorted({b for group in BRANDS.values() for b in group})

def fuzzy_ratio(a, b):
    return SequenceMatcher(None, a, b).ratio()

def best_match_brand(text: str) -> str:
    text = text.lower()
    words = set(re.findall(r"\b[a-z0-9']+\b", text))
    best_brand = "Unknown"
    best_score = 0

    for brand in ALL_BRANDS:
        brand_lower = brand.lower()
        brand_words = brand_lower.split()

        if len(brand_words) == 1:
            if brand_lower in words:
                score = 1
            else:
                score = max(fuzzy_ratio(word, brand_lower) for word in words)
                if score < 0.8:
                    score = 0
        else:
            if all(w in words for w in brand_words):
                score = len(brand_words)
            else:
                score = 0

        if score > best_score:
            best_score = score
            best_brand = brand

    inference_map = {
        "air max": "Nike",
        "tn": "Nike",
        "tuned": "Nike",
        "af1": "Nike",
        "air force": "Nike",
        "stan smith": "Adidas",
        "yeezy": "Adidas",
        "jordan": "Jordan",
        "doc martens": "Dr Martens",
        "docs": "Dr Martens"
    }

    for key, val in inference_map.items():
        if key in text:
            return val

    return best_brand if best_score > 0 else "Unknown"

# -----------------------------
# INPUT BOX
# -----------------------------
st.markdown("<div class='box'>", unsafe_allow_html=True)
user_text = st.text_area("Paste your messy item description:", height=200)

if st.button("Generate Listing 💸"):
    if check_paywall():
        st.session_state["uses"] += 1

        # Simple demo output
        brand = best_match_brand(user_text)
        title = f"{brand} {user_text.split()[1].capitalize()} Listing"
        description = f"This {user_text} is in great condition. Perfect for everyday wear!"
        tags = [brand, "fashion", "vinted", "resale", "smart-seller"]
        price = "£5.00"

        st.success("Listing generated successfully!")
        st.markdown(f"**Title:** {title}")
        st.markdown(f"**Description:** {description}")
        st.markdown(f"**Tags:** {', '.join(tags)}")
        st.markdown(f"**Suggested Price:** {price}")
        
st.markdown("</div>", unsafe_allow_html=True)
