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

# Premium UI styling
st.markdown("""
<style>
body {background-color: #f0f2f6;}
.big-title {font-size: 40px; font-weight: 800; text-align: center; color: #1f2933;}
.sub {font-size: 18px; text-align: center; color: #6b7280;}
.box {background: white; padding: 24px; border-radius: 16px; box-shadow: 0 10px 30px rgba(15,23,42,0.12);}
.output-box {background: #f9fafb; padding: 18px; border-radius: 12px; border: 1px solid #e5e7eb;}
.badge {display:inline-block; padding:4px 10px; border-radius:999px; font-size:11px; font-weight:600;}
.badge-free {background:#e5f3ff; color:#1d4ed8;}
.badge-premium {background:#fef3c7; color:#92400e;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='big-title'>SellSmart AI</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>Turn messy Vinted ideas into clean, ready-to-post listings.</div>", unsafe_allow_html=True)
st.write("")

# -----------------------------------
# PAYWALL CHECK
# -----------------------------------
def check_paywall():
    if st.session_state["premium"]:
        return True

    if st.session_state["uses"] < 3:
        left = 3 - st.session_state["uses"]
        st.markdown(
            f"<span class='badge badge-free'>Free uses left today: {left}</span>",
            unsafe_allow_html=True
        )
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
# HELPER: PRICE ESTIMATE
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
# MAIN BOX
# -----------------------------------
st.markdown("<div class='box'>", unsafe_allow_html=True)

st.markdown(
    "<span class='badge badge-premium'>v2.0 • Listing Generator</span>",
    unsafe_allow_html=True
)
st.write("")

user_text = st.text_area(
    "Paste your messy item description:",
    height=160,
    placeholder="e.g. blue primark shorts size 10 worn a few times but still good"
)

col1, col2 = st.columns([2, 1])
with col1:
    generate = st.button("Generate Listing 💸", use_container_width=True)
with col2:
    st.write("")

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

        # Detect condition keywords
        condition_words = {
            "new": ["new","brand new","with tags","nwt"],
            "excellent": ["like new","worn once","hardly worn"],
            "good": ["good condition","no major flaws","no marks"],
            "used": ["worn","used","some wear","a bit worn"]
        }
        condition_label = "Good used condition"
        for label, kws in condition_words.items():
            if any(kw in text for kw in kws):
                if label == "new":
                    condition_label = "Brand new / with tags"
                elif label == "excellent":
                    condition_label = "Excellent condition"
                elif label == "good":
                    condition_label = "Good condition"
                else:
                    condition_label = "Used but still in good wearable condition"
                break

        # Build title
        title_parts = []
        if brand != "Unknown":
            title_parts.append(brand)
        if colour:
            title_parts.append(colour.capitalize())
        title_parts.append(item.capitalize())
        title = " ".join(title_parts).strip()

        # Build description
        description = (
            f"{title}.\n\n"
            f"{condition_label}. No major flaws unless stated. "
            "Perfect for everyday wear and easy to style.\n\n"
            "From a smoke-free home. Will be posted quickly after purchase."
        )

        # Tags
        tags = [t for t in [brand, colour, item, "fashion", "vinted", "sellsmart"] if t]

        # Price suggestion
        price = estimate_price(brand, item)

        st.success("Listing generated successfully!")

        st.markdown("<div class='output-box'>", unsafe_allow_html=True)
        st.markdown("### 🏷️ Title")
        st.code(title, language="text")

        st.markdown("### 📝 Description")
        st.code(description, language="text")

        st.markdown("### 🔖 Tags")
        st.code(", ".join(tags), language="text")

        st.markdown("### 💷 Suggested Price")
        st.code(price, language="text")

        # Copy buttons (simple UX hint)
        st.info("Tip: long‑press on any box to copy on mobile, or use right‑click → copy on desktop.")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
