import streamlit as st
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any

# =========================
# BASIC CONFIG
# =========================

st.set_page_config(page_title="SellSmart AI", page_icon="💸", layout="centered")

HISTORY_FILE = "history.json"
DAILY_FREE_LIMIT = 5

# Stripe links – replace with real ones
WEEKLY_LINK = "https://buy.stripe.com/YOUR_REAL_WEEKLY_LINK"
MONTHLY_LINK = "https://buy.stripe.com/YOUR_REAL_MONTHLY_LINK"

# =========================
# SESSION STATE
# =========================

def init_session_state():
    defaults = {
        "page": "home",
        "luxury_mode": False,
        "premium": False,   # set True manually if you want unlimited
        "uses": 0,
        "history": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# =========================
# STYLING
# =========================

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: radial-gradient(circle at top, #1f2937 0, #020617 45%, #000000 100%) !important;
}
.block-container { max-width: 900px !important; }

/* Nav */
.nav-bar {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-bottom: 18px;
}
.nav-btn, .nav-btn-active {
    padding: 8px 16px;
    border-radius: 999px;
    font-size: 13px;
    cursor: pointer;
}
.nav-btn {
    border: 1px solid rgba(148,163,184,0.7);
    background: rgba(15,23,42,0.9);
    color: #e5e7eb;
}
.nav-btn-active {
    border: 1px solid rgba(34,197,94,0.9);
    background: linear-gradient(90deg, #22c55e, #3b82f6);
    color: #020617;
    font-weight: 600;
}

/* Card */
.glass-card {
    background: rgba(255, 255, 255, 0.10);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border-radius: 20px;
    padding: 26px 26px 22px 26px;
    border: 1px solid rgba(255, 255, 255, 0.18);
    box-shadow: 0 0 30px rgba(34, 197, 94, 0.35),
                0 0 80px rgba(59, 130, 246, 0.25);
    margin-top: 18px;
}

/* Subtitle */
.subtitle-glow {
    text-align: center;
    font-size: 20px;
    margin-top: 4px;
    color: #e5e7eb;
    text-shadow: 0 0 6px rgba(34, 197, 94, 0.7),
                 0 0 14px rgba(59, 130, 246, 0.6);
}

/* Pills */
.stat-pill {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(148, 163, 184, 0.5);
    color: #e5e7eb;
    font-size: 12px;
    margin-right: 6px;
}

/* Textarea */
textarea {
    background: rgba(15,23,42,0.85) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(148,163,184,0.7) !important;
    color: #e5e7eb !important;
    padding: 12px !important;
    font-size: 15px !important;
}

/* Button */
div.stButton > button {
    background: linear-gradient(90deg, #22c55e, #3b82f6);
    color: #020617;
    border-radius: 999px;
    padding: 12px 20px;
    font-size: 17px;
    font-weight: 600;
    border: none;
    width: 100%;
}
div.stButton > button:hover {
    filter: brightness(1.08);
    transform: translateY(-1px);
}

/* Luxury badge */
.luxury-badge-on {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    background: linear-gradient(90deg, #facc15, #f97316);
    color: #111827;
    font-size: 11px;
    font-weight: 600;
}
.luxury-badge-off {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    background: rgba(15,23,42,0.9);
    border: 1px solid rgba(148,163,184,0.7);
    color: #e5e7eb;
    font-size: 11px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HISTORY
# =========================

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    st.session_state["history"] = data
        except Exception:
            st.session_state["history"] = []

def save_history():
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state["history"], f, ensure_ascii=False, indent=2)
    except Exception:
        pass

load_history()

# =========================
# KNOWLEDGE BASE
# =========================

LUXURY_BRANDS = {
    "gucci","louis vuitton","lv","prada","balenciaga","dior","ysl",
    "saint laurent","burberry","fendi","versace","hermes","celine",
    "off-white","off white","amiri","palm angels","fear of god","moncler"
}
STREETWEAR_BRANDS = {
    "supreme","stussy","bape","a bathing ape","palace","trapstar",
    "corteiz","crtze","essentials","kith","carhartt","carhartt wip",
    "stone island","nike","jordan","adidas","yeezy","new balance",
    "unknown london","syna world"
}
OUTDOOR_BRANDS = {
    "the north face","north face","patagonia","columbia","berghaus",
    "rab","montane","arc'teryx","arcteryx"
}
HIGH_STREET_BRANDS = {
    "zara","h&m","primark","river island","topman","topshop",
    "boohoo","boohoo man","asos","pull&bear","pull and bear","bershka",
    "new look","next","uniqlo"
}
DENIM_BRANDS = {"levis","levi's","wrangler","lee","diesel","g-star","g star"}
FOOTWEAR_BRANDS = {
    "nike","adidas","new balance","converse","vans","dr martens",
    "timberland","ugg","balenciaga","gucci","yeezy","jordan"
}

ALL_BRANDS = (
    LUXURY_BRANDS | STREETWEAR_BRANDS | OUTDOOR_BRANDS |
    HIGH_STREET_BRANDS | DENIM_BRANDS | FOOTWEAR_BRANDS
)

CATEGORIES: Dict[str, List[str]] = {
    "jeans": ["jeans","denim"],
    "hoodie": ["hoodie","hoodies"],
    "jumper": ["jumper","sweater","knit"],
    "tshirt": ["t shirt","t-shirt","tee","top"],
    "dress": ["dress"],
    "coat": ["coat","jacket","parka","puffer"],
    "trainers": ["trainers","sneakers","shoes","boots"],
    "shorts": ["shorts"],
    "tracksuit": ["tracksuit","joggers","trackies"],
    "bag": ["bag","handbag","tote"],
    "cargos": ["cargo","cargos"],
    "skirt": ["skirt"],
}
SIZES = ["xs","s","m","l","xl","xxl","xxxl"]

# =========================
# DETECTION
# =========================

def detect_brand(text: str) -> str:
    t = text.lower()
    for b in sorted(ALL_BRANDS, key=len, reverse=True):
        if b in t:
            return b
    return "unbranded"

def brand_tier(brand: str) -> str:
    b = brand.lower()
    if b in LUXURY_BRANDS: return "luxury"
    if b in STREETWEAR_BRANDS: return "streetwear"
    if b in OUTDOOR_BRANDS: return "outdoor"
    if b in HIGH_STREET_BRANDS: return "high_street"
    if b in DENIM_BRANDS: return "denim"
    if b in FOOTWEAR_BRANDS: return "footwear"
    return "generic"

def detect_category(text: str) -> str:
    t = text.lower()
    for cat, kws in CATEGORIES.items():
        for k in kws:
            if k in t:
                return cat
    return "general"

def detect_colour(text: str) -> str:
    colours = [
        "black","white","red","blue","green","grey","gray",
        "pink","purple","yellow","brown","beige","cream",
        "navy","khaki","orange"
    ]
    t = text.lower()
    for c in colours:
        if c in t:
            return c
    return "unknown"

def detect_gender(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["women","womens","woman","ladies","girl"]): return "women"
    if any(w in t for w in ["men","mens","man","guy","male"]): return "men"
    if any(w in t for w in ["unisex","both"]): return "unisex"
    return "unspecified"

def detect_size(text: str) -> str:
    t = text.lower()
    for s in SIZES:
        if re.search(rf"\\b{s}\\b", t):
            return s.upper()
    num = re.search(r"\\b(\\d{2})\\b", t)
    if num:
        return num.group(1)
    return "not specified"

def detect_condition_and_flaws(text: str) -> Tuple[str,str,bool]:
    t = text.lower()
    condition = "Good"
    if any(w in t for w in ["brand new","with tags","bnwt","never worn","unworn"]):
        condition = "New with tags"
    elif any(w in t for w in ["worn once","like new","hardly worn"]):
        condition = "Excellent"
    elif any(w in t for w in ["worn loads","worn a lot","faded","used"]):
        condition = "Fair"

    flaws_list: List[str] = []
    if "mark" in t or "stain" in t: flaws_list.append("small mark / stain")
    if "rip" in t or "ripped" in t or "tear" in t: flaws_list.append("minor rip / tear")
    if "hole" in t: flaws_list.append("small hole")
    if "bobble" in t or "bobbly" in t or "pilling" in t: flaws_list.append("light bobbling")

    flaws = ""
    if flaws_list:
        flaws = "Flaws: " + ", ".join(flaws_list) + "."
    return condition, flaws, len(flaws_list) > 0

def extract_details(text: str) -> Dict[str,Any]:
    brand = detect_brand(text)
    return {
        "brand": brand,
        "tier": brand_tier(brand),
        "category": detect_category(text),
        "colour": detect_colour(text),
        "gender": detect_gender(text),
        "size": detect_size(text),
        "condition": detect_condition_and_flaws(text)[0],
        "flaws": detect_condition_and_flaws(text)[1],
        "has_flaws": detect_condition_and_flaws(text)[2],
    }

# =========================
# MATERIAL + PRICING
# =========================

MATERIAL_KEYWORDS = {
    "denim": ["jean","denim"],
    "cotton": ["cotton","tee","tshirt","shirt"],
    "leather": ["leather","hide"],
    "puffer": ["puffer","down","quilted"],
    "knit": ["knit","wool","jumper","sweater"],
    "polyester": ["polyester","synthetic"],
    "fleece": ["fleece"],
}

def infer_material(text: str) -> str:
    t = text.lower()
    for mat, keys in MATERIAL_KEYWORDS.items():
        for k in keys:
            if k in t:
                return mat
    return "unknown"

def seasonal_multiplier(category: str) -> float:
    m = datetime.now().month
    winter = {12,1,2}
    summer = {6,7,8}
    if category in ["coat","jacket","puffer","parka"]:
        return 1.25 if m in winter else 0.9
    if category in ["dress","shorts","skirt"]:
        return 1.2 if m in summer else 0.95
    return 1.0

DEMAND_BOOST = {
    "luxury":1.15,"streetwear":1.12,"outdoor":1.08,
    "denim":1.05,"high_street":1.02,"generic":1.0
}
def demand_multiplier(tier: str) -> float:
    return DEMAND_BOOST.get(tier,1.0)

def flaw_severity(details: dict) -> float:
    if not details["has_flaws"]:
        return 1.0
    flaws = details["flaws"].lower()
    sev = 1.0
    if "rip" in flaws or "tear" in flaws: sev -= 0.15
    if "hole" in flaws: sev -= 0.10
    if "stain" in flaws or "mark" in flaws: sev -= 0.08
    if "bobble" in flaws or "bobbly" in flaws or "pilling" in flaws: sev -= 0.05
    return max(0.65, sev)

def quick_sale_adjust(price: float, enabled: bool) -> float:
    return price * 0.85 if enabled else price

BASE_PRICES = {
    "luxury":85,"streetwear":28,"outdoor":35,
    "denim":30,"high_street":15,"generic":10
}
CATEGORY_MULTIPLIERS = {
    "coat":1.6,"jacket":1.5,"parka":1.7,"puffer":1.8,
    "jeans":1.2,"tracksuit":1.25,"cargos":1.2,
    "dress":1.15,"trainers":1.4,"bag":1.3
}
CONDITION_MULTIPLIERS = {
    "New with tags":1.45,"Excellent":1.25,"Good":1.0,"Fair":0.7
}

def calculate_price_v3(details: dict, luxury_mode: bool, quick_sale: bool=False) -> str:
    tier = details["tier"]
    cat = details["category"]
    cond = details["condition"]
    base = BASE_PRICES.get(tier,10)
    if luxury_mode:
        base = max(base,95)
    base *= CATEGORY_MULTIPLIERS.get(cat,1.0)
    base *= CONDITION_MULTIPLIERS.get(cond,1.0)
    base *= seasonal_multiplier(cat)
    base *= demand_multiplier(tier)
    base *= flaw_severity(details)
    base = quick_sale_adjust(base, quick_sale)
    price = max(4, round(base))
    return f"£{price}"

# =========================
# TITLE / DESCRIPTION / TAGS
# =========================

TITLE_TEMPLATES = {
    "luxury": {
        "default":"{brand} {gender}{colour}{category}{size} – Authentic Designer Piece",
        "coat":"{brand} {gender}{colour}{category}{size} – Premium Outerwear",
        "bag":"{brand} {colour}{category}{size} – Luxury Leather Piece",
        "dress":"{brand} {colour}{category}{size} – High‑End Designer Dress",
        "trainers":"{brand} {colour}{category}{size} – Premium Designer Footwear",
    },
    "streetwear": {
        "default":"{brand} {gender}{colour}{category}{size} – Streetwear Essential",
        "hoodie":"{brand} {colour}{category}{size} – Core Hoodie Drop",
        "tshirt":"{brand} {colour}{category}{size} – Clean Graphic Tee",
        "tracksuit":"{brand} {colour}{category}{size} – Full Tracksuit Fit",
        "trainers":"{brand} {colour}{category}{size} – Hype Footwear",
    },
    "outdoor": {
        "default":"{brand} {colour}{category}{size} – Outdoor Performance",
        "coat":"{brand} {colour}{category}{size} – Technical Outerwear",
        "bag":"{brand} {colour}{category}{size} – Durable Outdoor Pack",
    },
    "denim": {
        "default":"{brand} {colour}{category}{size} – Classic Denim",
        "jeans":"{brand} {colour}{category}{size} – Signature Denim Fit",
        "jacket":"{brand} {colour}{category}{size} – Vintage Denim Jacket",
    },
    "high_street": {
        "default":"{brand} {gender}{colour}{category}{size}",
        "dress":"{brand} {colour}{category}{size} – Simple & Stylish",
        "coat":"{brand} {colour}{category}{size} – Everyday Outerwear",
    },
    "generic": {
        "default":"{brand} {gender}{colour}{category}{size}",
    }
}

def format_title(details: dict, luxury_mode: bool) -> str:
    brand = "Unbranded" if details["brand"]=="unbranded" else details["brand"].title()
    tier = details["tier"]
    cat = details["category"]
    colour = "" if details["colour"]=="unknown" else details["colour"].title()+" "
    gender = ""
    if details["gender"]=="women": gender="Women's "
    elif details["gender"]=="men": gender="Men's "
    elif details["gender"]=="unisex": gender="Unisex "
    size = f" – Size {details['size']}" if details["size"]!="not specified" else ""
    tone = "luxury" if luxury_mode else tier
    if tone not in TITLE_TEMPLATES: tone="generic"
    group = TITLE_TEMPLATES[tone]
    template = group.get(cat, group["default"])
    return template.format(brand=brand,gender=gender,colour=colour,category=cat.title(),size=size)

DESCRIPTION_TEMPLATES = {
    "luxury": {
        "intro":"Premium {brand} {gender}{category} {colour}crafted with high‑end materials{size}. ",
        "condition":"Condition: {condition}. ",
        "flaws":"{flaws} ",
        "trust":"100% authentic. Carefully stored. Fast dispatch. ",
    },
    "streetwear": {
        "intro":"{brand} {gender}{category} {colour}with a clean streetwear aesthetic{size}. ",
        "condition":"Condition: {condition}. ",
        "flaws":"{flaws} ",
        "trust":"Trusted seller. Fast dispatch. ",
    },
    "outdoor": {
        "intro":"{brand} {category} {colour}designed for outdoor performance and durability{size}. ",
        "condition":"Condition: {condition}. ",
        "flaws":"{flaws} ",
        "trust":"Reliable seller. Quick dispatch. ",
    },
    "denim": {
        "intro":"{brand} denim {category} {colour}with a classic fit{size}. ",
        "condition":"Condition: {condition}. ",
        "flaws":"{flaws} ",
        "trust":"Fast dispatch. Trusted seller. ",
    },
    "high_street": {
        "intro":"{brand} {gender}{category} {colour}{size}. ",
        "condition":"Condition: {condition}. ",
        "flaws":"{flaws} ",
        "trust":"Fast dispatch. ",
    },
    "generic": {
        "intro":"{brand} {gender}{category} {colour}{size}. ",
        "condition":"Condition: {condition}. ",
        "flaws":"{flaws} ",
        "trust":"Fast dispatch. ",
    }
}

def polish_text(text: str) -> str:
    text = text.replace(" .",".").replace(" ,",",").replace("  "," ").strip()
    if not text.endswith("."):
        text += "."
    return text

CATEGORY_TRUST = {
    "coat":"Perfect for cold weather and built to last.",
    "jacket":"Reliable outerwear with great durability.",
    "dress":"Ideal for events, nights out or everyday wear.",
    "trainers":"Comfortable and stylish for daily use.",
    "bag":"Practical and stylish accessory.",
    "jeans":"Classic fit suitable for any wardrobe.",
    "hoodie":"Comfortable everyday essential.",
}
def category_trust_line(cat: str) -> str:
    return CATEGORY_TRUST.get(cat,"Great addition to any wardrobe.")

def format_description(details: dict, luxury_mode: bool) -> str:
    brand = "Unbranded" if details["brand"]=="unbranded" else details["brand"].title()
    tier = details["tier"]
    cat = details["category"]
    colour = "" if details["colour"]=="unknown" else f"in a {details['colour']} colourway "
    gender = ""
    if details["gender"]=="women": gender="women's "
    elif details["gender"]=="men": gender="men's "
    elif details["gender"]=="unisex": gender="unisex "
    size = f"(size {details['size']})" if details["size"]!="not specified" else ""
    cond = details["condition"]
    flaws = details["flaws"] if details["has_flaws"] else ""
    tone = "luxury" if luxury_mode else tier
    if tone not in DESCRIPTION_TEMPLATES: tone="generic"
    t = DESCRIPTION_TEMPLATES[tone]
    base = (
        t["intro"].format(brand=brand,gender=gender,category=cat,colour=colour,size=size)
        + t["condition"].format(condition=cond)
        + t["flaws"].format(flaws=flaws)
        + t["trust"]
    )
    final = base + " " + category_trust_line(cat)
    return polish_text(final)

def generate_tags_v2(details: dict, luxury_mode: bool) -> str:
    tags = []
    brand = details["brand"]
    if brand!="unbranded":
        tags.append("#"+brand.replace(" ","").lower())
    if details["colour"]!="unknown":
        tags.append("#"+details["colour"].lower())
    tags.append("#"+details["category"].lower())
    if luxury_mode or details["tier"]=="luxury":
        tags += ["#designer","#luxuryfashion"]
    elif details["tier"]=="streetwear":
        tags += ["#streetwear","#hype"]
    elif details["tier"]=="outdoor":
        tags += ["#outdoor","#techwear"]
    elif details["tier"]=="denim":
        tags += ["#denim","#jeans"]
    if details["gender"]=="women": tags.append("#womenswear")
    elif details["gender"]=="men": tags.append("#menswear")
    elif details["gender"]=="unisex": tags.append("#unisex")
    tags += ["#vinted","#reseller"]
    return " ".join(tags)

# =========================
# AI UNDERSTANDING PANEL
# =========================

def render_understanding_panel(details: dict):
    st.markdown("### 🤖 What the AI Understood")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.write(f"**Brand:** {details['brand'].title()}")
    st.write(f"**Tier:** {details['tier']}")
    st.write(f"**Category:** {details['category']}")
    st.write(f"**Colour:** {details['colour']}")
    st.write(f"**Gender:** {details['gender']}")
    st.write(f"**Size:** {details['size']}")
    st.write(f"**Condition:** {details['condition']}")
    if details["has_flaws"]:
        st.write(f"**Flaws:** {details['flaws']}")
    else:
        st.write("**Flaws:** None detected")
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# PAYWALL
# =========================

def check_paywall() -> bool:
    if st.session_state["premium"]:
        return True
    if st.session_state["uses"] < DAILY_FREE_LIMIT:
        left = DAILY_FREE_LIMIT - st.session_state["uses"]
        st.info(f"Free uses left today: {left}")
        return True
    st.error("You've reached your free daily limit.")
    st.markdown(f"[⚡ Weekly – £3.99]({WEEKLY_LINK})")
    st.markdown(f"[🚀 Monthly – £9.99]({MONTHLY_LINK})")
    return False

# =========================
# NAV
# =========================

def render_nav():
    st.markdown("<div class='nav-bar'>", unsafe_allow_html=True)
    col1,col2,col3,col4,col5 = st.columns(5)
    with col1:
        if st.button("🏠 Home"): st.session_state["page"]="home"
    with col2:
        if st.button("🕒 History"): st.session_state["page"]="history"
    with col3:
        if st.button("⚙️ Settings"): st.session_state["page"]="settings"
    with col4:
        if st.button("💎 Upgrade"): st.session_state["page"]="upgrade"
    with col5:
        if st.button("📄 Policies"): st.session_state["page"]="policies"
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# PAGES
# =========================

def page_home():
    st.image("image_1778389857310.jpeg", width=380)
    st.markdown("<h3 class='subtitle-glow'>Smarter listings. More sales. Less effort.</h3>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    with c1: st.markdown("<span class='stat-pill'>⚡ AI‑Optimised Titles</span>", unsafe_allow_html=True)
    with c2: st.markdown("<span class='stat-pill'>💷 Dynamic Pricing</span>", unsafe_allow_html=True)
    with c3: st.markdown("<span class='stat-pill'>🛍️ SEO Tags</span>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    lux_badge = "luxury-badge-on" if st.session_state["luxury_mode"] else "luxury-badge-off"
    lux_text = "Luxury Mode: ON" if st.session_state["luxury_mode"] else "Luxury Mode: OFF"
    st.markdown(f"<span class='{lux_badge}'>{lux_text}</span>", unsafe_allow_html=True)

    st.markdown("### ✏️ Describe your item")
    st.caption("Be messy — brand, colour, condition, flaws, size, anything you remember.")
    user_text = st.text_area("", height=150,
        placeholder="e.g. black north face puffer jacket mens medium worn a bit small rip on sleeve")
    quick_sale = st.checkbox("Quick Sale Mode (15% cheaper)")
    generate = st.button("Generate Listing 💸", use_container_width=True)

    if generate:
        if not user_text.strip():
            st.warning("Type something first.")
            st.markdown("</div>", unsafe_allow_html=True)
            return
        if not check_paywall():
            st.markdown("</div>", unsafe_allow_html=True)
            return

        st.session_state["uses"] += 1
        details = extract_details(user_text)
        details["material"] = infer_material(user_text)

        title = format_title(details, st.session_state["luxury_mode"])
        description = format_description(details, st.session_state["luxury_mode"])
        price = calculate_price_v3(details, st.session_state["luxury_mode"], quick_sale)
        tags = generate_tags_v2(details, st.session_state["luxury_mode"])

        st.success("Listing generated!")
        st.markdown("### 🏷️ Title"); st.code(title)
        st.markdown("### 📝 Description"); st.code(description)
        st.markdown("### 💷 Price Recommendation"); st.code(price)
        st.markdown("### 🔖 Tags"); st.code(tags)
        render_understanding_panel(details)

        if st.button("Save to History 🕒"):
            entry = {
                "title": title,
                "description": description,
                "price": price,
                "tags": tags,
                "luxury_mode": st.session_state["luxury_mode"],
                "timestamp": datetime.now().isoformat(timespec="seconds")
            }
            st.session_state["history"].append(entry)
            save_history()
            st.success("Saved to history.")

    st.markdown("</div>", unsafe_allow_html=True)

def page_history():
    st.markdown("## 🕒 History")
    if not st.session_state["history"]:
        st.info("No saved listings yet.")
        return
    for idx,item in enumerate(reversed(st.session_state["history"])):
        real_index = len(st.session_state["history"])-1-idx
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"### Listing #{real_index+1}")
        st.caption(item["timestamp"])
        st.write(f"**Luxury Mode:** {'ON' if item['luxury_mode'] else 'OFF'}")
        st.write("**Title**"); st.code(item["title"])
        st.write("**Description**"); st.code(item["description"])
        st.write("**Price**"); st.code(item["price"])
        st.write("**Tags**"); st.code(item["tags"])
        c1,c2,c3 = st.columns(3)
        with c1:
            if st.button("Re‑Generate (Luxury ON)", key=f"regen_{real_index}"):
                details = extract_details(item["description"])
                title = format_title(details, True)
                description = format_description(details, True)
                price = calculate_price_v3(details, True)
                tags = generate_tags_v2(details, True)
                st.markdown("### Re‑Generated (Luxury Mode ON)")
                st.code(title); st.code(description); st.code(price); st.code(tags)
        with c2:
            if st.button("Delete", key=f"delete_{real_index}"):
                del st.session_state["history"][real_index]
                save_history()
                st.experimental_rerun()
        with c3:
            st.caption("Copy manually from code blocks.")
        st.markdown("</div>", unsafe_allow_html=True)

def page_settings():
    st.markdown("## ⚙️ Settings")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### Luxury Mode")
    st.caption("Premium tone, authenticity notes, higher pricing, luxury tags.")
    st.session_state["luxury_mode"] = st.checkbox(
        "Enable Luxury Mode", value=st.session_state["luxury_mode"]
    )
    st.markdown("---")
    st.markdown("### Premium Status")
    if st.session_state["premium"]:
        st.success("You are on Premium. Unlimited listings unlocked.")
    else:
        st.info("You are on the Free plan. Upgrade for unlimited listings.")
    st.markdown("</div>", unsafe_allow_html=True)

def page_upgrade():
    st.markdown("## 💎 Upgrade to Premium")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.write("Unlock unlimited listings, Luxury Mode and full history access.")
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("### ⚡ Weekly")
        st.write("**£3.99 / week**")
        st.write("- Unlimited listings\n- Luxury Mode\n- Full history\n- Priority improvements")
        st.markdown(f"[Upgrade Weekly]({WEEKLY_LINK})")
    with c2:
        st.markdown("### 🚀 Monthly")
        st.write("**£9.99 / month**")
        st.write("- Unlimited listings\n- Luxury Mode\n- Full history\n- Best value")
        st.markdown(f"[Upgrade Monthly]({MONTHLY_LINK})")
    st.markdown("</div>", unsafe_allow_html=True)

def page_policies():
    st.markdown("## 📄 Policies")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### Terms of Service")
    st.write("Use SellSmart AI responsibly. You are responsible for your listings.")
    st.markdown("### Privacy Policy")
    st.write("We do not store sensitive personal data. History is stored locally.")
    st.markdown("### Acceptable Use")
    st.write("Do not use this tool for illegal items or counterfeit goods.")
    st.markdown("### Refund Policy")
    st.write("Digital products are non‑refundable unless required by law.")
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# ROUTER + FOOTER
# =========================

render_nav()

if st.session_state["page"]=="home":
    page_home()
elif st.session_state["page"]=="history":
    page_history()
elif st.session_state["page"]=="settings":
    page_settings()
elif st.session_state["page"]=="upgrade":
    page_upgrade()
elif st.session_state["page"]=="policies":
    page_policies()

st.markdown("""
<hr style='margin-top:40px; margin-bottom:10px;'>
<div style='text-align:center; font-size:14px; color:#9ca3af;'>
    SellSmart AI © 2026 • Built for Vinted sellers
</div>
""", unsafe_allow_html=True)
