import streamlit as st
import json
import os
import re
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="SellSmart AI",
    page_icon="💸",
    layout="centered"
)

HISTORY_FILE = "history.json"

# =========================================================
# SESSION STATE
# =========================================================
if "page" not in st.session_state:
    st.session_state["page"] = "home"

if "luxury_mode" not in st.session_state:
    st.session_state["luxury_mode"] = False

if "premium" not in st.session_state:
    st.session_state["premium"] = False  # flip manually for now

if "uses" not in st.session_state:
    st.session_state["uses"] = 0

if "history" not in st.session_state:
    st.session_state["history"] = []

DAILY_FREE_LIMIT = 5

WEEKLY_LINK = "https://buy.stripe.com/aFadR9arXe0m6Mv4wHg3601"
MONTHLY_LINK = "https://buy.stripe.com/9B63cvfMhg8u3Aj4wHg3602"

# =========================================================
# STYLING
# =========================================================
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: radial-gradient(circle at top, #1f2937 0, #020617 45%, #000000 100%) !important;
}
.block-container {
    max-width: 900px !important;
}

/* Top nav */
.nav-bar {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-bottom: 18px;
}
.nav-btn {
    padding: 8px 16px;
    border-radius: 999px;
    border: 1px solid rgba(148,163,184,0.7);
    background: rgba(15,23,42,0.9);
    color: #e5e7eb;
    font-size: 13px;
    cursor: pointer;
}
.nav-btn-active {
    padding: 8px 16px;
    border-radius: 999px;
    border: 1px solid rgba(34,197,94,0.9);
    background: linear-gradient(90deg, #22c55e, #3b82f6);
    color: #020617;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
}

/* Glass card */
.glass-card {
    background: rgba(255, 255, 255, 0.10);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border-radius: 20px;
    padding: 26px 26px 22px 26px;
    border: 1px solid rgba(255, 255, 255, 0.18);
    box-shadow:
        0 0 30px rgba(34, 197, 94, 0.35),
        0 0 80px rgba(59, 130, 246, 0.25);
    margin-top: 18px;
}

/* Subtitle */
.subtitle-glow {
    text-align: center;
    font-size: 20px;
    margin-top: 4px;
    color: #e5e7eb;
    text-shadow:
        0 0 6px rgba(34, 197, 94, 0.7),
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
    backdrop-filter: blur(12px) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(148,163,184,0.7) !important;
    color: #e5e7eb !important;
    padding: 12px !important;
    font-size: 15px !important;
}

/* Main button */
div.stButton > button {
    background: linear-gradient(90deg, #22c55e, #3b82f6);
    color: #020617;
    border-radius: 999px;
    padding: 12px 20px;
    font-size: 17px;
    font-weight: 600;
    border: none;
    width: 100%;
    animation: pulse 2.2s infinite ease-in-out;
}
div.stButton > button:hover {
    filter: brightness(1.08);
    transform: translateY(-1px);
}

/* Secondary button style */
.secondary-btn {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    border: 1px solid rgba(148,163,184,0.7);
    color: #e5e7eb;
    font-size: 12px;
    margin-right: 6px;
    background: rgba(15,23,42,0.9);
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

/* Pulse animation */
@keyframes pulse {
    0% { box-shadow: 0 0 0px rgba(34,197,94,0.4); }
    50% { box-shadow: 0 0 18px rgba(34,197,94,0.9); }
    100% { box-shadow: 0 0 0px rgba(34,197,94,0.4); }
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HISTORY PERSISTENCE
# =========================================================
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    st.session_state["history"] = data
        except Exception:
            pass

def save_history():
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state["history"], f, ensure_ascii=False, indent=2)
    except Exception:
        pass

load_history()

# =========================================================
# INTELLIGENCE ENGINE (v50-ish)
# =========================================================

LUXURY_BRANDS = {
    "gucci", "louis vuitton", "lv", "prada", "balenciaga", "dior", "ysl",
    "saint laurent", "burberry", "fendi", "versace", "hermes", "celine",
    "off-white", "off white", "amiri", "palm angels", "fear of god", "moncler"
}

STREETWEAR_BRANDS = {
    "supreme", "stussy", "bape", "a bathing ape", "palace", "trapstar",
    "corteiz", "crtze", "essentials", "kith", "carhartt", "carhartt wip",
    "stone island", "nike", "jordan", "adidas", "yeezy", "new balance",
    "unknown london", "syna world"
}

OUTDOOR_BRANDS = {
    "the north face", "north face", "patagonia", "columbia", "berghaus",
    "rab", "montane", "arc'teryx", "arcteryx"
}

HIGH_STREET_BRANDS = {
    "zara", "h&m", "primark", "river island", "topman", "topshop",
    "boohoo", "boohoo man", "asos", "pull&bear", "pull and bear", "bershka",
    "new look", "next", "uniqlo"
}

DENIM_BRANDS = {
    "levis", "levi's", "wrangler", "lee", "diesel", "g-star", "g star"
}

FOOTWEAR_BRANDS = {
    "nike", "adidas", "new balance", "converse", "vans", "dr martens",
    "timberland", "ugg", "balenciaga", "gucci", "yeezy", "jordan"
}

ALL_BRANDS = (
    LUXURY_BRANDS
    | STREETWEAR_BRANDS
    | OUTDOOR_BRANDS
    | HIGH_STREET_BRANDS
    | DENIM_BRANDS
    | FOOTWEAR_BRANDS
)

CATEGORIES = {
    "jeans": ["jeans", "denim"],
    "hoodie": ["hoodie", "hoodies"],
    "jumper": ["jumper", "sweater", "knit"],
    "tshirt": ["t shirt", "t-shirt", "tee", "top"],
    "dress": ["dress"],
    "coat": ["coat", "jacket", "parka", "puffer"],
    "trainers": ["trainers", "sneakers", "shoes", "boots"],
    "shorts": ["shorts"],
    "tracksuit": ["tracksuit", "joggers", "trackies"],
    "bag": ["bag", "handbag", "tote"],
    "cargos": ["cargo", "cargos"],
    "skirt": ["skirt"],
}

SIZES = ["xs", "s", "m", "l", "xl", "xxl", "xxxl"]

def detect_brand(text: str) -> str:
    t = text.lower()
    for b in sorted(ALL_BRANDS, key=len, reverse=True):
        if b in t:
            return b
    return "unbranded"

def brand_tier(brand: str) -> str:
    b = brand.lower()
    if b in LUXURY_BRANDS:
        return "luxury"
    if b in STREETWEAR_BRANDS:
        return "streetwear"
    if b in OUTDOOR_BRANDS:
        return "outdoor"
    if b in HIGH_STREET_BRANDS:
        return "high_street"
    if b in DENIM_BRANDS:
        return "denim"
    if b in FOOTWEAR_BRANDS:
        return "footwear"
    return "generic"

def detect_category(text: str) -> str:
    t = text.lower()
    for cat, keywords in CATEGORIES.items():
        for k in keywords:
            if k in t:
                return cat
    return "general"

def detect_colour(text: str) -> str:
    colours = [
        "black", "white", "red", "blue", "green", "grey", "gray",
        "pink", "purple", "yellow", "brown", "beige", "cream",
        "navy", "khaki", "orange"
    ]
    t = text.lower()
    for c in colours:
        if c in t:
            return c
    return "unknown"

def detect_gender(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["women", "womens", "woman", "ladies", "girl"]):
        return "women"
    if any(w in t for w in ["men", "mens", "man", "guy", "male"]):
        return "men"
    if any(w in t for w in ["unisex", "both"]):
        return "unisex"
    return "unspecified"

def detect_size(text: str) -> str:
    t = text.lower()
    for s in SIZES:
        if re.search(rf"\b{s}\b", t):
            return s.upper()
    num_match = re.search(r"\b(\d{2})\b", t)
    if num_match:
        return num_match.group(1)
    return "not specified"

def detect_condition_and_flaws(text: str):
    t = text.lower()
    condition = "Good"
    if any(w in t for w in ["brand new", "with tags", "bnwt", "never worn", "unworn"]):
        condition = "New with tags"
    elif any(w in t for w in ["worn once", "like new", "hardly worn"]):
        condition = "Excellent"
    elif any(w in t for w in ["worn loads", "worn a lot", "faded", "used"]):
        condition = "Fair"

    flaw_phrases = []
    if "mark" in t or "stain" in t:
        flaw_phrases.append("small mark / stain")
    if "rip" in t or "ripped" in t or "tear" in t:
        flaw_phrases.append("minor rip / tear")
    if "hole" in t:
        flaw_phrases.append("small hole")
    if "bobble" in t or "bobbly" in t or "pilling" in t:
        flaw_phrases.append("light bobbling")

    flaws = ""
    if flaw_phrases:
        flaws = "Flaws: " + ", ".join(flaw_phrases) + "."

    has_flaws = len(flaw_phrases) > 0
    return condition, flaws, has_flaws

def extract_details(text: str) -> dict:
    brand = detect_brand(text)
    tier = brand_tier(brand)
    category = detect_category(text)
    colour = detect_colour(text)
    gender = detect_gender(text)
    size = detect_size(text)
    condition, flaws, has_flaws = detect_condition_and_flaws(text)

    return {
        "brand": brand,
        "tier": tier,
        "category": category,
        "colour": colour,
        "gender": gender,
        "size": size,
        "condition": condition,
        "flaws": flaws,
        "has_flaws": has_flaws,
    }

def generate_title(details: dict, luxury_mode: bool) -> str:
    brand = details["brand"]
    tier = details["tier"]
    category = details["category"]
    colour = details["colour"]
    gender = details["gender"]
    size = details["size"]

    brand_clean = "Unbranded" if brand == "unbranded" else brand.title()
    colour_clean = "" if colour == "unknown" else colour.title() + " "

    gender_label = ""
    if gender == "women":
        gender_label = "Women's "
    elif gender == "men":
        gender_label = "Men's "
    elif gender == "unisex":
        gender_label = "Unisex "

    cat_label = {
        "jeans": "Jeans",
        "hoodie": "Hoodie",
        "jumper": "Jumper",
        "tshirt": "T‑Shirt",
        "dress": "Dress",
        "coat": "Coat",
        "trainers": "Trainers",
        "shorts": "Shorts",
        "tracksuit": "Tracksuit",
        "bag": "Bag",
        "cargos": "Cargo Trousers",
        "skirt": "Skirt",
        "general": "Item",
    }.get(category, "Item")

    size_part = f" – Size {size}" if size != "not specified" else ""

    if luxury_mode or tier == "luxury":
        return f"{brand_clean} {gender_label}{colour_clean}{cat_label}{size_part} – Authentic Designer Piece"
    elif tier == "streetwear":
        return f"{brand_clean} {gender_label}{colour_clean}{cat_label}{size_part} – Streetwear Essential"
    elif tier == "outdoor":
        return f"{brand_clean} {colour_clean}{cat_label}{size_part} – Outdoor Performance"
    elif tier == "denim":
        return f"{brand_clean} {colour_clean}{cat_label}{size_part} – Classic Denim"
    else:
        return f"{brand_clean} {gender_label}{colour_clean}{cat_label}{size_part}"

def generate_description(details: dict, luxury_mode: bool) -> str:
    brand = details["brand"]
    tier = details["tier"]
    category = details["category"]
    colour = details["colour"]
    gender = details["gender"]
    size = details["size"]
    condition = details["condition"]
    flaws = details["flaws"]
    has_flaws = details["has_flaws"]

    brand_clean = "Unbranded" if brand == "unbranded" else brand.title()
    colour_phrase = "" if colour == "unknown" else f"in a {colour} colourway "
    size_phrase = "" if size == "not specified" else f" (size {size})"

    gender_phrase = ""
    if gender == "women":
        gender_phrase = "women's "
    elif gender == "men":
        gender_phrase = "men's "
    elif gender == "unisex":
        gender_phrase = "unisex "

    if luxury_mode or tier == "luxury":
        base_intro = f"Premium {brand_clean} {gender_phrase}{category} {colour_phrase}crafted with high‑end materials{size_phrase}. "
    elif tier == "streetwear":
        base_intro = f"{brand_clean} {gender_phrase}{category} {colour_phrase}with a clean streetwear look{size_phrase}. "
    elif tier == "outdoor":
        base_intro = f"{brand_clean} {category} {colour_phrase}designed for outdoor performance and comfort{size_phrase}. "
    elif tier == "denim":
        base_intro = f"{brand_clean} denim {category} {colour_phrase}with a classic fit{size_phrase}. "
    else:
        base_intro = f"{brand_clean} {gender_phrase}{category} {colour_phrase}{size_phrase}. "

    condition_line = f"Condition: {condition}."
    if has_flaws and flaws:
        condition_line += f" {flaws}"

    trust_bits = []
    if luxury_mode or tier == "luxury":
        trust_bits.append("100% authentic – buy with confidence.")
    if tier in {"luxury", "streetwear"} or luxury_mode:
        trust_bits.append("Carefully stored and ready to wear.")
    trust_bits.append("Fast dispatch from a reliable seller.")

    trust_line = " ".join(trust_bits)

    return f"{base_intro}{condition_line} {trust_line}"

def price_recommendation(details: dict, luxury_mode: bool) -> str:
    tier = details["tier"]
    category = details["category"]
    condition = details["condition"]
    has_flaws = details["has_flaws"]

    if luxury_mode:
        base = 90
    else:
        if tier == "luxury":
            base = 80
        elif tier == "streetwear":
            base = 25
        elif tier == "outdoor":
            base = 35
        elif tier == "denim":
            base = 28
        elif tier == "high_street":
            base = 15
        else:
            base = 10

    if category in ["coat", "jacket", "parka", "puffer"]:
        base += 20
    elif category in ["jeans", "tracksuit", "cargos"]:
        base += 8
    elif category in ["trainers"]:
        base += 15
    elif category in ["dress"]:
        base += 6

    if condition == "New with tags":
        base *= 1.4
    elif condition == "Excellent":
        base *= 1.2
    elif condition == "Fair":
        base *= 0.7

    if has_flaws:
        base *= 0.8

    price = max(4, round(base))
    return f"£{price}"

def generate_tags(details: dict, luxury_mode: bool) -> str:
    brand = details["brand"]
    tier = details["tier"]
    category = details["category"]
    colour = details["colour"]
    gender = details["gender"]

    tags = []

    if brand != "unbranded":
        tags.append("#" + brand.replace(" ", "").lower())
    else:
        tags.append("#unbranded")

    if colour != "unknown":
        tags.append(f"#{colour.lower()}")

    if category != "general":
        tags.append(f"#{category.lower()}")

    if luxury_mode or tier == "luxury":
        tags.extend(["#designer", "#luxuryfashion"])
    elif tier == "streetwear":
        tags.extend(["#streetwear", "#style"])
    elif tier == "outdoor":
        tags.extend(["#outdoor", "#techwear"])
    elif tier == "denim":
        tags.extend(["#denim", "#jeans"])

    if gender == "women":
        tags.append("#womenswear")
    elif gender == "men":
        tags.append("#menswear")
    elif gender == "unisex":
        tags.append("#unisex")

    tags.append("#vinted")
    tags.append("#reseller")

    return " ".join(tags)

# =========================================================
# PAYWALL
# =========================================================
def check_paywall():
    if st.session_state["premium"]:
        return True

    if st.session_state["uses"] < DAILY_FREE_LIMIT:
        left = DAILY_FREE_LIMIT - st.session_state["uses"]
        st.info(f"Free uses left today: {left}")
        return True

    st.error("Free limit reached. Upgrade to Weekly or Monthly for unlimited listings.")
    st.markdown(f"[⚡ Weekly – £3.99]({WEEKLY_LINK})")
    st.markdown(f"[🚀 Monthly – £9.99]({MONTHLY_LINK})")
    return False

# =========================================================
# NAVIGATION
# =========================================================
def nav_button(label, page_key):
    cls = "nav-btn-active" if st.session_state["page"] == page_key else "nav-btn"
    if st.markdown(f"<button class='{cls}'>{label}</button>", unsafe_allow_html=True):
        pass  # placeholder (Streamlit doesn't handle raw button clicks here)

# We'll use columns with st.button instead of pure HTML for navigation
def render_nav():
    st.markdown("<div class='nav-bar'>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("🏠 Home", key="nav_home"):
            st.session_state["page"] = "home"
    with col2:
        if st.button("🕒 History", key="nav_history"):
            st.session_state["page"] = "history"
    with col3:
        if st.button("⚙️ Settings", key="nav_settings"):
            st.session_state["page"] = "settings"
    with col4:
        if st.button("💎 Upgrade", key="nav_upgrade"):
            st.session_state["page"] = "upgrade"
    with col5:
        if st.button("📄 Policies", key="nav_policies"):
            st.session_state["page"] = "policies"
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# PAGES
# =========================================================
def page_home():
    st.image("image_1778389857310.jpeg", width=380)
    st.markdown("<h3 class='subtitle-glow'>Smarter listings. More sales. Less effort.</h3>", unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("<span class='stat-pill'>⚡ AI‑Optimised Titles</span>", unsafe_allow_html=True)
    with col_b:
        st.markdown("<span class='stat-pill'>💷 Realistic Pricing</span>", unsafe_allow_html=True)
    with col_c:
        st.markdown("<span class='stat-pill'>🛍️ Vinted‑Ready Tags</span>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    lux_badge = "luxury-badge-on" if st.session_state["luxury_mode"] else "luxury-badge-off"
    lux_text = "Luxury Mode: ON" if st.session_state["luxury_mode"] else "Luxury Mode: OFF"
    st.markdown(f"<span class='{lux_badge}'>{lux_text}</span>", unsafe_allow_html=True)

    st.markdown("### ✏️ Describe your item")
    st.caption("Be messy if you want – brand, colour, condition, flaws, size, anything you remember.")

    user_text = st.text_area(
        "",
        height=150,
        placeholder="e.g. i got some red gucci jeans women worn a few times, tiny mark on knee"
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        generate = st.button("Generate Vinted Listing 💸", use_container_width=True)
    with col2:
        clear = st.button("Clear Uses", use_container_width=True)

    if clear:
        st.session_state["uses"] = 0
        st.success("Daily uses reset.")

    if generate:
        if not user_text.strip():
            st.warning("Type something about your item first.")
        elif check_paywall():
            st.session_state["uses"] += 1

            details = extract_details(user_text)
            title = generate_title(details, st.session_state["luxury_mode"])
            description = generate_description(details, st.session_state["luxury_mode"])
            price = price_recommendation(details, st.session_state["luxury_mode"])
            tags = generate_tags(details, st.session_state["luxury_mode"])

            st.success("Listing generated!")

            st.markdown("### 🏷️ Title")
            st.code(title)

            st.markdown("### 📝 Description")
            st.code(description)

            st.markdown("### 💷 Price Recommendation")
            st.code(price)

            st.markdown("### 🔖 Tags")
            st.code(tags)

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
        st.info("No listings saved yet. Generate something on Home and save it.")
        return

    for idx, item in enumerate(reversed(st.session_state["history"])):
        real_index = len(st.session_state["history"]) - 1 - idx
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"**#{real_index+1} • {item['timestamp']}**")
        lux_label = "ON" if item.get("luxury_mode") else "OFF"
        st.markdown(f"*Luxury Mode: {lux_label}*")

        st.markdown("**Title**")
        st.code(item["title"])

        st.markdown("**Description**")
        st.code(item["description"])

        st.markdown("**Price**")
        st.code(item["price"])

        st.markdown("**Tags**")
        st.code(item["tags"])

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Copy All", key=f"copy_{real_index}"):
                st.write("Copy manually from the blocks above (Streamlit can't access clipboard directly).")
        with c2:
            if st.button("Re‑generate (Luxury ON)", key=f"regen_{real_index}"):
                details = extract_details(item["description"])
                title = generate_title(details, True)
                description = generate_description(details, True)
                price = price_recommendation(details, True)
                tags = generate_tags(details, True)

                st.markdown("**Re‑generated with Luxury Mode ON**")
                st.code(title)
                st.code(description)
                st.code(price)
                st.code(tags)
        with c3:
            if st.button("Delete", key=f"del_{real_index}"):
                del st.session_state["history"][real_index]
                save_history()
                st.experimental_rerun()

        st.markdown("</div>", unsafe_allow_html=True)

def page_settings():
    st.markdown("## ⚙️ Settings")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    st.markdown("### Luxury Mode")
    st.caption("When ON, the AI writes in a premium, designer‑style tone with higher pricing and authenticity notes.")
    lux = st.checkbox("Enable Luxury Mode", value=st.session_state["luxury_mode"])
    st.session_state["luxury_mode"] = lux

    st.markdown("---")
    st.markdown("### Premium Status")
    if st.session_state["premium"]:
        st.success("You are currently on a Premium plan. Unlimited listings unlocked.")
    else:
        st.info("You are currently on the Free plan. Upgrade for unlimited listings and full features.")

    st.markdown("</div>", unsafe_allow_html=True)

def page_upgrade():
    st.markdown("## 💎 Upgrade to Premium")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    st.markdown("Unlock unlimited listings, Luxury Mode and full history access.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ⚡ Weekly")
        st.markdown("**£3.99 / week**")
        st.markdown("- Unlimited listings\n- Luxury Mode\n- Full history\n- Priority improvements")
        st.markdown(f"[Upgrade Weekly]({WEEKLY_LINK})")
    with col2:
        st.markdown("### 🚀 Monthly")
        st.markdown("**£9.99 / month**")
        st.markdown("- Unlimited listings\n- Luxury Mode\n- Full history\n- Best value")
        st.markdown(f"[Upgrade Monthly]({MONTHLY_LINK})")

    st.markdown("</div>", unsafe_allow_html=True)

def page_policies():
    st.markdown("## 📄 Policies")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    st.markdown("### Terms of Service")
    st.write("Use SellSmart AI at your own discretion. You are responsible for the accuracy of your listings and compliance with Vinted’s rules.")

    st.markdown("### Privacy Policy")
    st.write("We do not store sensitive personal data. Text you enter is used only to generate listings and optional history on your device/server.")

    st.markdown("### Acceptable Use")
    st.write("Do not use this tool for illegal items, counterfeit goods, or anything that violates marketplace policies.")

    st.markdown("### Refund Policy")
    st.write("Digital products are typically non‑refundable. Any refunds are handled manually on a case‑by‑case basis.")

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# RENDER
# =========================================================
render_nav()

if st.session_state["page"] == "home":
    page_home()
elif st.session_state["page"] == "history":
    page_history()
elif st.session_state["page"] == "settings":
    page_settings()
elif st.session_state["page"] == "upgrade":
    page_upgrade()
elif st.session_state["page"] == "policies":
    page_policies()

st.markdown("""
<hr style='margin-top:40px; margin-bottom:10px;'>
<div style='text-align:center; font-size:14px; color:#9ca3af;'>
    SellSmart AI © 2026 • Built for Vinted sellers
</div>
""", unsafe_allow_html=True)
