# =========================================================
# SellSmart AI v3.0 — Single File Edition (Drop 1 / 4)
# =========================================================

import streamlit as st
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any

# =========================================================
# APP CONFIG
# =========================================================

st.set_page_config(
    page_title="SellSmart AI",
    page_icon="💸",
    layout="centered"
)

HISTORY_FILE = "history.json"

# =========================================================
# SESSION STATE INITIALISATION
# =========================================================

def init_session_state() -> None:
    defaults = {
        "page": "home",
        "luxury_mode": False,
        "premium": False,   # manually flip to True if you want unlimited
        "uses": 0,
        "history": [],
        "last_input": "",
        "last_output": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

DAILY_FREE_LIMIT = 5

# Replace these with your real Stripe links
WEEKLY_LINK = "https://buy.stripe.com/YOUR_REAL_WEEKLY_LINK"
MONTHLY_LINK = "https://buy.stripe.com/YOUR_REAL_MONTHLY_LINK"

# =========================================================
# GLOBAL STYLING (NEON GLASS)
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

def load_history() -> None:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    st.session_state["history"] = data
        except Exception:
            st.session_state["history"] = []

def save_history() -> None:
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state["history"], f, ensure_ascii=False, indent=2)
    except Exception:
        pass

load_history()

# =========================================================
# BRAND + CATEGORY KNOWLEDGE BASE
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

CATEGORIES: Dict[str, List[str]] = {
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

# =========================================================
# LOW-LEVEL DETECTION HELPERS
# =========================================================

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

def detect_condition_and_flaws(text: str) -> Tuple[str, str, bool]:
    t = text.lower()
    condition = "Good"
    if any(w in t for w in ["brand new", "with tags", "bnwt", "never worn", "unworn"]):
        condition = "New with tags"
    elif any(w in t for w in ["worn once", "like new", "hardly worn"]):
        condition = "Excellent"
    elif any(w in t for w in ["worn loads", "worn a lot", "faded", "used"]):
        condition = "Fair"

    flaw_phrases: List[str] = []
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

def extract_details(text: str) -> Dict[str, Any]:
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
    }# =========================================================
# MATERIAL INFERENCE ENGINE
# =========================================================

MATERIAL_KEYWORDS = {
    "denim": ["jean", "denim"],
    "cotton": ["cotton", "tee", "tshirt", "shirt"],
    "leather": ["leather", "hide"],
    "puffer": ["puffer", "down", "quilted"],
    "knit": ["knit", "wool", "jumper", "sweater"],
    "polyester": ["polyester", "synthetic"],
    "fleece": ["fleece"],
}

def infer_material(text: str) -> str:
    t = text.lower()
    for material, keys in MATERIAL_KEYWORDS.items():
        for k in keys:
            if k in t:
                return material
    return "unknown"


# =========================================================
# SEASONAL PRICING ENGINE
# =========================================================

def seasonal_multiplier(category: str) -> float:
    """Boosts or reduces price depending on season."""
    month = datetime.now().month

    winter = {12, 1, 2}
    summer = {6, 7, 8}

    if category in ["coat", "jacket", "puffer", "parka"]:
        return 1.25 if month in winter else 0.9

    if category in ["dress", "shorts", "skirt"]:
        return 1.2 if month in summer else 0.95

    return 1.0


# =========================================================
# DEMAND-BASED PRICING ENGINE
# =========================================================

DEMAND_BOOST = {
    "luxury": 1.15,
    "streetwear": 1.12,
    "outdoor": 1.08,
    "denim": 1.05,
    "high_street": 1.02,
    "generic": 1.0,
}

def demand_multiplier(tier: str) -> float:
    return DEMAND_BOOST.get(tier, 1.0)


# =========================================================
# FLAW SEVERITY ENGINE
# =========================================================

def flaw_severity(details: dict) -> float:
    """More flaws = bigger penalty."""
    if not details["has_flaws"]:
        return 1.0

    flaws = details["flaws"].lower()
    severity = 1.0

    if "rip" in flaws or "tear" in flaws:
        severity -= 0.15

    if "hole" in flaws:
        severity -= 0.10

    if "stain" in flaws or "mark" in flaws:
        severity -= 0.08

    if "bobble" in flaws or "bobbly" in flaws# =========================================================
# MATERIAL INFERENCE ENGINE
# =========================================================

MATERIAL_KEYWORDS = {
    "denim": ["jean", "denim"],
    "cotton": ["cotton", "tee", "tshirt", "shirt"],
    "leather": ["leather", "hide"],
    "puffer": ["puffer", "down", "quilted"],
    "knit": ["knit", "wool", "jumper", "sweater"],
    "polyester": ["polyester", "synthetic"],
    "fleece": ["fleece"],
}

def infer_material(text: str) -> str:
    t = text.lower()
    for material, keys in MATERIAL_KEYWORDS.items():
        for k in keys:
            if k in t:
                return material
    return "unknown"


# =========================================================
# SEASONAL PRICING ENGINE
# =========================================================

def seasonal_multiplier(category: str) -> float:
    """Boosts or reduces price depending on season."""
    month = datetime.now().month

    winter = {12, 1, 2}
    summer = {6, 7, 8}

    if category in ["coat", "jacket", "puffer", "parka"]:
        return 1.25 if month in winter else 0.9

    if category in ["dress", "shorts", "skirt"]:
        return 1.2 if month in summer else 0.95

    return 1.0


# =========================================================
# DEMAND-BASED PRICING ENGINE
# =========================================================

DEMAND_BOOST = {
    "luxury": 1.15,
    "streetwear": 1.12,
    "outdoor": 1.08,
    "denim": 1.05,
    "high_street": 1.02,
    "generic": 1.0,
}

def demand_multiplier(tier: str) -> float:
    return DEMAND_BOOST.get(tier, 1.0)


# =========================================================
# FLAW SEVERITY ENGINE
# =========================================================

def flaw_severity(details: dict) -> float:
    """More flaws = bigger penalty."""
    if not details["has_flaws"]:
        return 1.0

    flaws = details["flaws"].lower()
    severity = 1.0

    if "rip" in flaws or "tear" in flaws:
        severity -= 0.15

    if "hole" in flaws:
        severity -= 0.10

    if "stain" in flaws or "mark" in flaws:
        severity -= 0.08

    if "bobble" in flaws or "bobbly" in flaws or "pilling" in flaws:
        severity -= 0.05

    return max(0.65, severity)


# =========================================================
# QUICK SALE MODE
# =========================================================

def quick_sale_adjust(price: float, enabled: bool) -> float:
    if not enabled:
        return price
    return price * 0.85  # 15% cheaper for fast sale


# =========================================================
# FINAL PRICE ENGINE v3 — ALL FACTORS COMBINED
# =========================================================

BASE_PRICES = {
    "luxury": 85,
    "streetwear": 28,
    "outdoor": 35,
    "denim": 30,
    "high_street": 15,
    "generic": 10,
}

CATEGORY_MULTIPLIERS = {
    "coat": 1.6,
    "jacket": 1.5,
    "parka": 1.7,
    "puffer": 1.8,
    "jeans": 1.2,
    "tracksuit": 1.25,
    "cargos": 1.2,
    "dress": 1.15,
    "trainers": 1.4,
    "bag": 1.3,
}

CONDITION_MULTIPLIERS = {
    "New with tags": 1.45,
    "Excellent": 1.25,
    "Good": 1.0,
    "Fair": 0.7,
}

def calculate_price_v3(details: dict, luxury_mode: bool, quick_sale: bool = False) -> str:
    tier = details["tier"]
    category = details["category"]
    condition = details["condition"]

    base = BASE_PRICES.get(tier, 10)

    # Luxury override
    if luxury_mode:
        base = max(base, 95)

    # Category multiplier
    base *= CATEGORY_MULTIPLIERS.get(category, 1.0)

    # Condition multiplier
    base *= CONDITION_MULTIPLIERS.get(condition, 1.0)

    # Seasonal multiplier
    base *= seasonal_multiplier(category)

    # Demand multiplier
    base *= demand_multiplier(tier)

    # Flaw severity
    base *= flaw_severity(details)

    # Quick sale mode
    base = quick_sale_adjust(base, quick_sale)

    price = max(4, round(base))
    return f"£{price}"


# =========================================================
# TEXT POLISH ENGINE
# =========================================================

def polish_text(text: str) -> str:
    """Small grammar + spacing improvements."""
    text = text.replace(" .", ".")
    text = text.replace(" ,", ",")
    text = text.replace("  ", " ")
    text = text.strip()
    if not text.endswith("."):
        text += "."
    return text


# =========================================================
# CATEGORY-SPECIFIC TRUST LINES
# =========================================================

CATEGORY_TRUST = {
    "coat": "Perfect for cold weather and built to last.",
    "jacket": "Reliable outerwear with great durability.",
    "dress": "Ideal for events, nights out or everyday wear.",
    "trainers": "Comfortable and stylish for daily use.",
    "bag": "Practical and stylish accessory.",
    "jeans": "Classic fit suitable for any wardrobe.",
    "hoodie": "Comfortable everyday essential.",
}

def category_trust_line(category: str) -> str:
    return CATEGORY_TRUST.get(category, "Great addition to any wardrobe.")


# =========================================================
# DESCRIPTION ENGINE v3 — POLISHED + CATEGORY TRUST
# =========================================================

def format_description_v3(details: dict, luxury_mode: bool) -> str:
    base = format_description(details, luxury_mode)
    trust = category_trust_line(details["category"])
    final = base + " " + trust
    return polish_text(final)# =========================================================
# TITLE ENGINE v2 — CATEGORY + TONE AWARE
# =========================================================

TITLE_TEMPLATES = {
    "luxury": {
        "default": "{brand} {gender}{colour}{category}{size} – Authentic Designer Piece",
        "coat": "{brand} {gender}{colour}{category}{size} – Premium Outerwear",
        "bag": "{brand} {colour}{category}{size} – Luxury Leather Piece",
        "dress": "{brand} {colour}{category}{size} – High‑End Designer Dress",
        "trainers": "{brand} {colour}{category}{size} – Premium Designer Footwear",
    },
    "streetwear": {
        "default": "{brand} {gender}{colour}{category}{size} – Streetwear Essential",
        "hoodie": "{brand} {colour}{category}{size} – Core Hoodie Drop",
        "tshirt": "{brand} {colour}{category}{size} – Clean Graphic Tee",
        "tracksuit": "{brand} {colour}{category}{size} – Full Tracksuit Fit",
        "trainers": "{brand} {colour}{category}{size} – Hype Footwear",
    },
    "outdoor": {
        "default": "{brand} {colour}{category}{size} – Outdoor Performance",
        "coat": "{brand} {colour}{category}{size} – Technical Outerwear",
        "bag": "{brand} {colour}{category}{size} – Durable Outdoor Pack",
    },
    "denim": {
        "default": "{brand} {colour}{category}{size} – Classic Denim",
        "jeans": "{brand} {colour}{category}{size} – Signature Denim Fit",
        "jacket": "{brand} {colour}{category}{size} – Vintage Denim Jacket",
    },
    "high_street": {
        "default": "{brand} {gender}{colour}{category}{size}",
        "dress": "{brand} {colour}{category}{size} – Simple & Stylish",
        "coat": "{brand} {colour}{category}{size} – Everyday Outerwear",
    },
    "generic": {
        "default": "{brand} {gender}{colour}{category}{size}",
    }
}

def format_title(details: dict, luxury_mode: bool) -> str:
    brand = "Unbranded" if details["brand"] == "unbranded" else details["brand"].title()
    tier = details["tier"]
    category = details["category"]
    colour = "" if details["colour"] == "unknown" else details["colour"].title() + " "

    gender = ""
    if details["gender"] == "women":
        gender = "Women's "
    elif details["gender"] == "men":
        gender = "Men's "
    elif details["gender"] == "unisex":
        gender = "Unisex "

    size = f" – Size {details['size']}" if details["size"] != "not specified" else ""

    tone = "luxury" if luxury_mode else tier
    if tone not in TITLE_TEMPLATES:
        tone = "generic"

    template_group = TITLE_TEMPLATES[tone]
    template = template_group.get(category, template_group["default"])

    return template.format(
        brand=brand,
        gender=gender,
        colour=colour,
        category=category.title(),
        size=size
    )


# =========================================================
# DESCRIPTION ENGINE v2 — BASE LAYER
# =========================================================

DESCRIPTION_TEMPLATES = {
    "luxury": {
        "intro": "Premium {brand} {gender}{category} {colour}crafted with high‑end materials{size}. ",
        "condition": "Condition: {condition}. ",
        "flaws": "{flaws} ",
        "trust": "100% authentic. Carefully stored. Fast dispatch. ",
    },
    "streetwear": {
        "intro": "{brand} {gender}{category} {colour}with a clean streetwear aesthetic{size}. ",
        "condition": "Condition: {condition}. ",
        "flaws": "{flaws} ",
        "trust": "Trusted seller. Fast dispatch. ",
    },
    "outdoor": {
        "intro": "{brand} {category} {colour}designed for outdoor performance and durability{size}. ",
        "condition": "Condition: {condition}. ",
        "flaws": "{flaws} ",
        "trust": "Reliable seller. Quick dispatch. ",
    },
    "denim": {
        "intro": "{brand} denim {category} {colour}with a classic fit{size}. ",
        "condition": "Condition: {condition}. ",
        "flaws": "{flaws} ",
        "trust": "Fast dispatch. Trusted seller. ",
    },
    "high_street": {
        "intro": "{brand} {gender}{category} {colour}{size}. ",
        "condition": "Condition: {condition}. ",
        "flaws": "{flaws} ",
        "trust": "Fast dispatch. ",
    },
    "generic": {
        "intro": "{brand} {gender}{category} {colour}{size}. ",
        "condition": "Condition: {condition}. ",
        "flaws": "{flaws} ",
        "trust": "Fast dispatch. ",
    }
}

def format_description(details: dict, luxury_mode: bool) -> str:
    brand = "Unbranded" if details["brand"] == "unbranded" else details["brand"].title()
    tier = details["tier"]
    category = details["category"]
    colour = "" if details["colour"] == "unknown" else f"in a {details['colour']} colourway "

    gender = ""
    if details["gender"] == "women":
        gender = "women's "
    elif details["gender"] == "men":
        gender = "men's "
    elif details["gender"] == "unisex":
        gender = "unisex "

    size = f"(size {details['size']})" if details["size"] != "not specified" else ""
    condition = details["condition"]
    flaws = details["flaws"] if details["has_flaws"] else ""

    tone = "luxury" if luxury_mode else tier
    if tone not in DESCRIPTION_TEMPLATES:
        tone = "generic"

    t = DESCRIPTION_TEMPLATES[tone]

    return (
        t["intro"].format(brand=brand, gender=gender, category=category, colour=colour, size=size)
        + t["condition"].format(condition=condition)
        + t["flaws"].format(flaws=flaws)
        + t["trust"]
    )


# =========================================================
# TAG ENGINE v2 — SEO + TONE + CATEGORY
# =========================================================

def generate_tags_v2(details: dict, luxury_mode: bool) -> str:
    tags = []

    brand = details["brand"]
    if brand != "unbranded":
        tags.append("#" + brand.replace(" ", "").lower())

    if details["colour"] != "unknown":
        tags.append(f"#{details['colour'].lower()}")

    tags.append(f"#{details['category'].lower()}")

    if luxury_mode or details["tier"] == "luxury":
        tags.extend(["#designer", "#luxuryfashion"])
    elif details["tier"] == "streetwear":
        tags.extend(["#streetwear", "#hype"])
    elif details["tier"] == "outdoor":
        tags.extend(["#outdoor", "#techwear"])
    elif details["tier"] == "denim":
        tags.extend(["#denim", "#jeans"])

    if details["gender"] == "women":
        tags.append("#womenswear")
    elif details["gender"] == "men":
        tags.append("#menswear")
    elif details["gender"] == "unisex":
        tags.append("#unisex")

    tags.append("#vinted")
    tags.append("#reseller")

    return " ".join(tags)


# =========================================================
# AI UNDERSTANDING PANEL
# =========================================================

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


# =========================================================
# PAYWALL SYSTEM
# =========================================================

def check_paywall() -> bool:
    """Returns True if user can generate, False if blocked."""
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


# =========================================================
# NAVIGATION BAR
# =========================================================

def render_nav():
    st.markdown("<div class='nav-bar'>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("🏠 Home"):
            st.session_state["page"] = "home"

    with col2:
        if st.button("🕒 History"):
            st.session_state["page"] = "history"

    with col3:
        if st.button("⚙️ Settings"):
            st.session_state["page"] = "settings"

    with col4:
        if st.button("💎 Upgrade"):
            st.session_state["page"] = "upgrade"

    with col5:
        if st.button("📄 Policies"):
            st.session_state["page"] = "policies"

    st.markdown("</div>", unsafe_allow_html=True)# =========================================================
# HOME PAGE — FULL VERSION (v3.0)
# =========================================================

def page_home():
    # Header image
    st.image("image_1778389857310.jpeg", width=380)
    st.markdown("<h3 class='subtitle-glow'>Smarter listings. More sales. Less effort.</h3>", unsafe_allow_html=True)

    # Feature pills
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("<span class='stat-pill'>⚡ AI‑Optimised Titles</span>", unsafe_allow_html=True)
    with col_b:
        st.markdown("<span class='stat-pill'>💷 Dynamic Pricing v3</span>", unsafe_allow_html=True)
    with col_c:
        st.markdown("<span class='stat-pill'>🛍️ SEO‑Perfect Tags</span>", unsafe_allow_html=True)

    # Main card
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    # Luxury badge
    lux_badge = "luxury-badge-on" if st.session_state["luxury_mode"] else "luxury-badge-off"
    lux_text = "Luxury Mode: ON" if st.session_state["luxury_mode"] else "Luxury Mode: OFF"
    st.markdown(f"<span class='{lux_badge}'>{lux_text}</span>", unsafe_allow_html=True)

    # Input
    st.markdown("### ✏️ Describe your item")
    st.caption("Be messy — brand, colour, condition, flaws, size, anything you remember.")

    user_text = st.text_area(
        "",
        height=150,
        placeholder="e.g. black north face puffer jacket mens medium worn a bit small rip on sleeve"
    )

    # Quick sale toggle
    quick_sale = st.checkbox("Quick Sale Mode (15% cheaper)")

    # Generate button
    generate = st.button("Generate Listing 💸", use_container_width=True)

    if generate:
        if not user_text.strip():
            st.warning("Type something first.")
            return

        if not check_paywall():
            return

        st.session_state["uses"] += 1
        st.session_state["last_input"] = user_text

        # Extract details
        details = extract_details(user_text)
        details["material"] = infer_material(user_text)

        # Generate outputs
        title = format_title(details, st.session_state["luxury_mode"])
        description = format_description_v3(details, st.session_state["luxury_mode"])
        price = calculate_price_v3(details, st.session_state["luxury_mode"], quick_sale)
        tags = generate_tags_v2(details, st.session_state["luxury_mode"])

        st.session_state["last_output"] = {
            "title": title,
            "description": description,
            "price": price,
            "tags": tags,
            "details": details
        }

        st.success("Listing generated!")

        # Output blocks
        st.markdown("### 🏷️ Title")
        st.code(title)

        st.markdown("### 📝 Description")
        st.code(description)

        st.markdown("### 💷 Price Recommendation")
        st.code(price)

        st.markdown("### 🔖 Tags")
        st.code(tags)

        # Understanding panel
        render_understanding_panel(details)

        # Save to history
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

    st.markdown("</div>", unsafe_allow_html=True)# =========================================================
# HISTORY PAGE
# =========================================================

def page_history():
    st.markdown("## 🕒 History")

    if not st.session_state["history"]:
        st.info("No saved listings yet.")
        return

    for idx, item in enumerate(reversed(st.session_state["history"])):
        real_index = len(st.session_state["history"]) - 1 - idx

        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

        st.markdown(f"### Listing #{real_index+1}")
        st.caption(item["timestamp"])

        lux_label = "ON" if item["luxury_mode"] else "OFF"
        st.write(f"**Luxury Mode:** {lux_label}")

        st.write("**Title**")
        st.code(item["title"])

        st.write("**Description**")
        st.code(item["description"])

        st.write("**Price**")
        st.code(item["price"])

        st.write("**Tags**")
        st.code(item["tags"])

        col1, col2, col3 = st.columns(3)

        # Re-generate with luxury mode ON
        with col1:
            if st.button("Re‑Generate (Luxury ON)", key=f"regen_{real_index}"):
                details = extract_details(item["description"])
                title = format_title(details, True)
                description = format_description_v3(details, True)
                price = calculate_price_v3(details, True)
                tags = generate_tags_v2(details, True)

                st.markdown("### Re‑Generated (Luxury Mode ON)")
                st.code(title)
                st.code(description)
                st.code(price)
                st.code(tags)

        # Delete entry
        with col2:
            if st.button("Delete", key=f"delete_{real_index}"):
                del st.session_state["history"][real_index]
                save_history()
                st.experimental_rerun()

        # Copy note
        with col3:
            st.caption("Copy manually from code blocks.")

        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# SETTINGS PAGE
# =========================================================

def page_settings():
    st.markdown("## ⚙️ Settings")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    # Luxury mode toggle
    st.markdown("### Luxury Mode")
    st.caption("Premium tone, authenticity notes, higher pricing, luxury tags.")

    st.session_state["luxury_mode"] = st.checkbox(
        "Enable Luxury Mode",
        value=st.session_state["luxury_mode"]
    )

    st.markdown("---")

    # Premium status
    st.markdown("### Premium Status")
    if st.session_state["premium"]:
        st.success("You are on Premium. Unlimited listings unlocked.")
    else:
        st.info("You are on the Free plan. Upgrade for unlimited listings.")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# UPGRADE PAGE
# =========================================================

def page_upgrade():
    st.markdown("## 💎 Upgrade to Premium")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    st.write("Unlock unlimited listings, Luxury Mode and full history access.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ⚡ Weekly")
        st.write("**£3.99 / week**")
        st.write("- Unlimited listings\n- Luxury Mode\n- Full history\n- Priority improvements")
        st.markdown(f"[Upgrade Weekly]({WEEKLY_LINK})")

    with col2:
        st.markdown("### 🚀 Monthly")
        st.write("**£9.99 / month**")
        st.write("- Unlimited listings\n- Luxury Mode\n- Full history\n- Best value")
        st.markdown(f"[Upgrade Monthly]({MONTHLY_LINK})")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# POLICIES PAGE
# =========================================================

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


# =========================================================
# PAGE ROUTER
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

# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<hr style='margin-top:40px; margin-bottom:10px;'>
<div style='text-align:center; font-size:14px; color:#9ca3af;'>
    SellSmart AI © 2026 • Built for Vinted sellers
</div>
""", unsafe_allow_html=True)# =========================================================
# TITLE ENGINE v2 — CATEGORY + TONE AWARE
# =========================================================

TITLE_TEMPLATES = {
    "luxury": {
        "default": "{brand} {gender}{colour}{category}{size} – Authentic Designer Piece",
        "coat": "{brand} {gender}{colour}{category}{size} – Premium Outerwear",
        "bag": "{brand} {colour}{category}{size} – Luxury Leather Piece",
        "dress": "{brand} {colour}{category}{size} – High‑End Designer Dress",
        "trainers": "{brand} {colour}{category}{size} – Premium Designer Footwear",
    },
    "streetwear": {
        "default": "{brand} {gender}{colour}{category}{size} – Streetwear Essential",
        "hoodie": "{brand} {colour}{category}{size} – Core Hoodie Drop",
        "tshirt": "{brand} {colour}{category}{size} – Clean Graphic Tee",
        "tracksuit": "{brand} {colour}{category}{size} – Full Tracksuit Fit",
        "trainers": "{brand} {colour}{category}{size} – Hype Footwear",
    },
    "outdoor": {
        "default": "{brand} {colour}{category}{size} – Outdoor Performance",
        "coat": "{brand} {colour}{category}{size} – Technical Outerwear",
        "bag": "{brand} {colour}{category}{size} – Durable Outdoor Pack",
    },
    "denim": {
        "default": "{brand} {colour}{category}{size} – Classic Denim",
        "jeans": "{brand} {colour}{category}{size} – Signature Denim Fit",
        "jacket": "{brand} {colour}{category}{size} – Vintage Denim Jacket",
    },
    "high_street": {
        "default": "{brand} {gender}{colour}{category}{size}",
        "dress": "{brand} {colour}{category}{size} – Simple & Stylish",
        "coat": "{brand} {colour}{category}{size} – Everyday Outerwear",
    },
    "generic": {
        "default": "{brand} {gender}{colour}{category}{size}",
    }
}

def format_title(details: dict, luxury_mode: bool) -> str:
    brand = "Unbranded" if details["brand"] == "unbranded" else details["brand"].title()
    tier = details["tier"]
    category = details["category"]
    colour = "" if details["colour"] == "unknown" else details["colour"].title() + " "
    gender = ""
    if details["gender"] == "women":
        gender = "Women's "
    elif details["gender"] == "men":
        gender = "Men's "
    elif details["gender"] == "unisex":
        gender = "Unisex "

    size = f" – Size {details['size']}" if details["size"] != "not specified" else ""

    tone = "luxury" if luxury_mode else tier
    if tone not in TITLE_TEMPLATES:
        tone = "generic"

    template_group = TITLE_TEMPLATES[tone]
    template = template_group.get(category, template_group["default"])

    return template.format(
        brand=brand,
        gender=gender,
        colour=colour,
        category=category.title(),
        size=size
    )

# =========================================================
# DESCRIPTION ENGINE v2 — TONE + CATEGORY AWARE
# =========================================================

DESCRIPTION_TEMPLATES = {
    "luxury": {
        "intro": "Premium {brand} {gender}{category} {colour}crafted with high‑end materials{size}. ",
        "condition": "Condition: {condition}. ",
        "flaws": "{flaws} ",
        "trust": "100% authentic. Carefully stored. Fast dispatch. ",
    },
    "streetwear": {
        "intro": "{brand} {gender}{category} {colour}with a clean streetwear aesthetic{size}. ",
        "condition": "Condition: {condition}. ",
        "flaws": "{flaws} ",
        "trust": "Trusted seller. Fast dispatch. ",
    },
    "outdoor": {
        "intro": "{brand} {category} {colour}designed for outdoor performance and durability{size}. ",
        "condition": "Condition: {condition}. ",
        "flaws": "{flaws} ",
        "trust": "Reliable seller. Quick dispatch. ",
    },
    "denim": {
        "intro": "{brand} denim {category} {colour}with a classic fit{size}. ",
        "condition": "Condition: {condition}. ",
        "flaws": "{flaws} ",
        "trust": "Fast dispatch. Trusted seller. ",
    },
    "high_street": {
        "intro": "{brand} {gender}{category} {colour}{size}. ",
        "condition": "Condition: {condition}. ",
        "flaws": "{flaws} ",
        "trust": "Fast dispatch. ",
    },
    "generic": {
        "intro": "{brand} {gender}{category} {colour}{size}. ",
        "condition": "Condition: {condition}. ",
        "flaws": "{flaws} ",
        "trust": "Fast dispatch. ",
    }
}

def format_description(details: dict, luxury_mode: bool) -> str:
    brand = "Unbranded" if details["brand"] == "unbranded" else details["brand"].title()
    tier = details["tier"]
    category = details["category"]
    colour = "" if details["colour"] == "unknown" else f"in a {details['colour']} colourway "
    gender = ""
    if details["gender"] == "women":
        gender = "women's "
    elif details["gender"] == "men":
        gender = "men's "
    elif details["gender"] == "unisex":
        gender = "unisex "

    size = f"(size {details['size']})" if details["size"] != "not specified" else ""
    condition = details["condition"]
    flaws = details["flaws"] if details["has_flaws"] else ""

    tone = "luxury" if luxury_mode else tier
    if tone not in DESCRIPTION_TEMPLATES:
        tone = "generic"

    t = DESCRIPTION_TEMPLATES[tone]

    return (
        t["intro"].format(brand=brand, gender=gender, category=category, colour=colour, size=size)
        + t["condition"].format(condition=condition)
        + t["flaws"].format(flaws=flaws)
        + t["trust"]
    )

# =========================================================
# PRICING ENGINE v2 — CURVES + MULTIPLIERS
# =========================================================

BASE_PRICES = {
    "luxury": 85,
    "streetwear": 28,
    "outdoor": 35,
    "denim": 30,
    "high_street": 15,
    "generic": 10,
}

CATEGORY_MULTIPLIERS = {
    "coat": 1.6,
    "jacket": 1.5,
    "parka": 1.7,
    "puffer": 1.8,
    "jeans": 1.2,
    "tracksuit": 1.25,
    "cargos": 1.2,
    "dress": 1.15,
    "trainers": 1.4,
    "bag": 1.3,
}

CONDITION_MULTIPLIERS = {
    "New with tags": 1.45,
    "Excellent": 1.25,
    "Good": 1.0,
    "Fair": 0.7,
}

FLAW_PENALTY = 0.82

def calculate_price(details: dict, luxury_mode: bool) -> str:
    tier = details["tier"]
    category = details["category"]
    condition = details["condition"]
    has_flaws = details["has_flaws"]

    base = BASE_PRICES.get(tier, 10)
    if luxury_mode:
        base = max(base, 90)

    base *= CATEGORY_MULTIPLIERS.get(category, 1.0)
    base *= CONDITION_MULTIPLIERS.get(condition, 1.0)

    if has_flaws:
        base *= FLAW_PENALTY

    price = max(4, round(base))
    return f"£{price}"

# =========================================================
# TAG ENGINE v2 — SEO + TONE + CATEGORY
# =========================================================

def generate_tags_v2(details: dict, luxury_mode: bool) -> str:
    tags = []

    brand = details["brand"]
    if brand != "unbranded":
        tags.append("#" + brand.replace(" ", "").lower())

    if details["colour"] != "unknown":
        tags.append(f"#{details['colour'].lower()}")

    tags.append(f"#{details['category'].lower()}")

    if luxury_mode or details["tier"] == "luxury":
        tags.extend(["#designer", "#luxuryfashion"])
    elif details["tier"] == "streetwear":
        tags.extend(["#streetwear", "#hype"])
    elif details["tier"] == "outdoor":
        tags.extend(["#outdoor", "#techwear"])
    elif details["tier"] == "denim":
        tags.extend(["#denim", "#jeans"])

    if details["gender"] == "women":
        tags.append("#womenswear")
    elif details["gender"] == "men":
        tags.append("#menswear")
    elif details["gender"] == "unisex":
        tags.append("#unisex")

    tags.append("#vinted")
    tags.append("#reseller")

    return " ".join(tags)

# =========================================================
# AI UNDERSTANDING PANEL
# =========================================================

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

    st.markdown("</div>", unsafe_allow_html=True)# =========================================================
# PAYWALL SYSTEM
# =========================================================

def check_paywall() -> bool:
    """Returns True if user can generate, False if blocked."""
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


# =========================================================
# NAVIGATION BAR
# =========================================================

def render_nav():
    st.markdown("<div class='nav-bar'>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("🏠 Home"):
            st.session_state["page"] = "home"

    with col2:
        if st.button("🕒 History"):
            st.session_state["page"] = "history"

    with col3:
        if st.button("⚙️ Settings"):
            st.session_state["page"] = "settings"

    with col4:
        if st.button("💎 Upgrade"):
            st.session_state["page"] = "upgrade"

    with col5:
        if st.button("📄 Policies"):
            st.session_state["page"] = "policies"

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# HOME PAGE
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

    # Luxury badge
    lux_badge = "luxury-badge-on" if st.session_state["luxury_mode"] else "luxury-badge-off"
    lux_text = "Luxury Mode: ON" if st.session_state["luxury_mode"] else "Luxury Mode: OFF"
    st.markdown(f"<span class='{lux_badge}'>{lux_text}</span>", unsafe_allow_html=True)

    st.markdown("### ✏️ Describe your item")
    st.caption("Be messy — brand, colour, condition, flaws, size, anything you remember.")

    user_text = st.text_area(
        "",
        height=150,
        placeholder="e.g. red gucci jeans womens worn a few times tiny mark on knee"
    )

    generate = st.button("Generate Listing 💸", use_container_width=True)

    if generate:
        if not user_text.strip():
            st.warning("Type something first.")
            return

        if not check_paywall():
            return

        st.session_state["uses"] += 1
        st.session_state["last_input"] = user_text

        details = extract_details(user_text)

        title = format_title(details, st.session_state["luxury_mode"])
        description = format_description(details, st.session_state["luxury_mode"])
        price = calculate_price(details, st.session_state["luxury_mode"])
        tags = generate_tags_v2(details, st.session_state["luxury_mode"])

        st.session_state["last_output"] = {
            "title": title,
            "description": description,
            "price": price,
            "tags": tags,
            "details": details
        }

        st.success("Listing generated!")

        st.markdown("### 🏷️ Title")
        st.code(title)

        st.markdown("### 📝 Description")
        st.code(description)

        st.markdown("### 💷 Price Recommendation")
        st.code(price)

        st.markdown("### 🔖 Tags")
        st.code(tags)

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


# =========================================================
# HISTORY PAGE
# =========================================================

def page_history():
    st.markdown("## 🕒 History")

    if not st.session_state["history"]:
        st.info("No saved listings yet.")
        return

    for idx, item in enumerate(reversed(st.session_state["history"])):
        real_index = len(st.session_state["history"]) - 1 - idx

        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

        st.markdown(f"### Listing #{real_index+1}")
        st.caption(item["timestamp"])

        lux_label = "ON" if item["luxury_mode"] else "OFF"
        st.write(f"**Luxury Mode:** {lux_label}")

        st.write("**Title**")
        st.code(item["title"])

        st.write("**Description**")
        st.code(item["description"])

        st.write("**Price**")
        st.code(item["price"])

        st.write("**Tags**")
        st.code(item["tags"])

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Re‑Generate (Luxury ON)", key=f"regen_{real_index}"):
                details = extract_details(item["description"])
                title = format_title(details, True)
                description = format_description(details, True)
                price = calculate_price(details, True)
                tags = generate_tags_v2(details, True)

                st.markdown("### Re‑Generated (Luxury Mode ON)")
                st.code(title)
                st.code(description)
                st.code(price)
                st.code(tags)

        with col2:
            if st.button("Delete", key=f"delete_{real_index}"):
                del st.session_state["history"][real_index]
                save_history()
                st.experimental_rerun()

        with col3:
            st.caption("Copy manually from code blocks.")

        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# SETTINGS PAGE
# =========================================================

def page_settings():
    st.markdown("## ⚙️ Settings")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    st.markdown("### Luxury Mode")
    st.caption("Premium tone, authenticity notes, higher pricing, luxury tags.")

    st.session_state["luxury_mode"] = st.checkbox(
        "Enable Luxury Mode",
        value=st.session_state["luxury_mode"]
    )

    st.markdown("---")

    st.markdown("### Premium Status")
    if st.session_state["premium"]:
        st.success("You are on Premium. Unlimited listings unlocked.")
    else:
        st.info("You are on the Free plan. Upgrade for unlimited listings.")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# UPGRADE PAGE
# =========================================================

def page_upgrade():
    st.markdown("## 💎 Upgrade to Premium")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    st.write("Unlock unlimited listings, Luxury Mode and full history access.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ⚡ Weekly")
        st.write("**£3.99 / week**")
        st.write("- Unlimited listings\n- Luxury Mode\n- Full history\n- Priority improvements")
        st.markdown(f"[Upgrade Weekly]({WEEKLY_LINK})")

    with col2:
        st.markdown("### 🚀 Monthly")
        st.write("**£9.99 / month**")
        st.write("- Unlimited listings\n- Luxury Mode\n- Full history\n- Best value")
        st.markdown(f"[Upgrade Monthly]({MONTHLY_LINK})")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# POLICIES PAGE
# =========================================================

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


# =========================================================
# PAGE ROUTER
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
""", unsafe_allow_html=True)# =========================================================
# STAGE 4 — INTELLIGENCE POLISH + UX ENHANCEMENTS
# =========================================================

# =========================================================
# MATERIAL INFERENCE ENGINE
# =========================================================

MATERIAL_KEYWORDS = {
    "denim": ["jean", "denim"],
    "cotton": ["cotton", "tee", "tshirt", "shirt"],
    "leather": ["leather", "hide"],
    "puffer": ["puffer", "down", "quilted"],
    "knit": ["knit", "wool", "jumper", "sweater"],
    "polyester": ["polyester", "synthetic"],
    "fleece": ["fleece"],
}

def infer_material(text: str) -> str:
    t = text.lower()
    for material, keys in MATERIAL_KEYWORDS.items():
        for k in keys:
            if k in t:
                return material
    return "unknown"


# =========================================================
# SEASONAL PRICING ENGINE
# =========================================================

def seasonal_multiplier(category: str) -> float:
    """Boosts or reduces price depending on season."""
    month = datetime.now().month

    winter = {12, 1, 2}
    summer = {6, 7, 8}

    if category in ["coat", "jacket", "puffer", "parka"]:
        return 1.25 if month in winter else 0.9

    if category in ["dress", "shorts", "skirt"]:
        return 1.2 if month in summer else 0.95

    return 1.0


# =========================================================
# DEMAND-BASED PRICING ENGINE
# =========================================================

DEMAND_BOOST = {
    "luxury": 1.15,
    "streetwear": 1.12,
    "outdoor": 1.08,
    "denim": 1.05,
    "high_street": 1.02,
    "generic": 1.0,
}

def demand_multiplier(tier: str) -> float:
    return DEMAND_BOOST.get(tier, 1.0)


# =========================================================
# FLAW SEVERITY ENGINE
# =========================================================

def flaw_severity(details: dict) -> float:
    """More flaws = bigger penalty."""
    if not details["has_flaws"]:
        return 1.0

    flaws = details["flaws"].lower()

    severity = 1.0
    if "rip" in flaws or "tear"# =========================================================
# STAGE 4 — INTELLIGENCE POLISH + UX ENHANCEMENTS
# =========================================================

# =========================================================
# MATERIAL INFERENCE ENGINE
# =========================================================

MATERIAL_KEYWORDS = {
    "denim": ["jean", "denim"],
    "cotton": ["cotton", "tee", "tshirt", "shirt"],
    "leather": ["leather", "hide"],
    "puffer": ["puffer", "down", "quilted"],
    "knit": ["knit", "wool", "jumper", "sweater"],
    "polyester": ["polyester", "synthetic"],
    "fleece": ["fleece"],
}

def infer_material(text: str) -> str:
    t = text.lower()
    for material, keys in MATERIAL_KEYWORDS.items():
        for k in keys:
            if k in t:
                return material
    return "unknown"


# =========================================================
# SEASONAL PRICING ENGINE
# =========================================================

def seasonal_multiplier(category: str) -> float:
    """Boosts or reduces price depending on season."""
    month = datetime.now().month

    winter = {12, 1, 2}
    summer = {6, 7, 8}

    if category in ["coat", "jacket", "puffer", "parka"]:
        return 1.25 if month in winter else 0.9

    if category in ["dress", "shorts", "skirt"]:
        return 1.2 if month in summer else 0.95

    return 1.0


# =========================================================
# DEMAND-BASED PRICING ENGINE
# =========================================================

DEMAND_BOOST = {
    "luxury": 1.15,
    "streetwear": 1.12,
    "outdoor": 1.08,
    "denim": 1.05,
    "high_street": 1.02,
    "generic": 1.0,
}

def demand_multiplier(tier: str) -> float:
    return DEMAND_BOOST.get(tier, 1.0)


# =========================================================
# FLAW SEVERITY ENGINE
# =========================================================

def flaw_severity(details: dict) -> float:
    """More flaws = bigger penalty."""
    if not details["has_flaws"]:
        return 1.0

    flaws = details["flaws"].lower()

    severity = 1.0

    if "rip" in flaws or "tear" in flaws:
        severity -= 0.15

    if "hole" in flaws:
        severity -= 0.10

    if "stain" in flaws or "mark" in flaws:
        severity -= 0.08

    if "bobble" in flaws or "bobbly" in flaws or "pilling" in flaws:
        severity -= 0.05

    return max(0.65, severity)

# =========================================================
# QUICK SALE MODE (OPTIONAL)
# =========================================================

def quick_sale_adjust(price: float, enabled: bool) -> float:
    if not enabled:
        return price
    return price * 0.85  # 15% cheaper for fast sale


# =========================================================
# FINAL PRICE ENGINE v3 — ALL FACTORS COMBINED
# =========================================================

def calculate_price_v3(details: dict, luxury_mode: bool, quick_sale: bool = False) -> str:
    tier = details["tier"]
    category = details["category"]
    condition = details["condition"]

    base = BASE_PRICES.get(tier, 10)

    # Luxury override
    if luxury_mode:
        base = max(base, 95)

    # Category multiplier
    base *= CATEGORY_MULTIPLIERS.get(category, 1.0)

    # Condition multiplier
    base *= CONDITION_MULTIPLIERS.get(condition, 1.0)

    # Seasonal multiplier
    base *= seasonal_multiplier(category)

    # Demand multiplier
    base *= demand_multiplier(tier)

    # Flaw severity
    base *= flaw_severity(details)

    # Quick sale mode
    base = quick_sale_adjust(base, quick_sale)

    price = max(4, round(base))
    return f"£{price}"


# =========================================================
# DESCRIPTION POLISH ENGINE
# =========================================================

def polish_text(text: str) -> str:
    """Small grammar + spacing improvements."""
    text = text.replace(" .", ".")
    text = text.replace(" ,", ",")
    text = text.replace("  ", " ")
    text = text.strip()
    if not text.endswith("."):
        text += "."
    return text


# =========================================================
# CATEGORY-SPECIFIC TRUST LINES
# =========================================================

CATEGORY_TRUST = {
    "coat": "Perfect for cold weather and built to last.",
    "jacket": "Reliable outerwear with great durability.",
    "dress": "Ideal for events, nights out or everyday wear.",
    "trainers": "Comfortable and stylish for daily use.",
    "bag": "Practical and stylish accessory.",
    "jeans": "Classic fit suitable for any wardrobe.",
    "hoodie": "Comfortable everyday essential.",
}

def category_trust_line(category: str) -> str:
    return CATEGORY_TRUST.get(category, "Great addition to any wardrobe.")


# =========================================================
# DESCRIPTION ENGINE v3 — POLISHED + CATEGORY TRUST
# =========================================================

def format_description_v3(details: dict, luxury_mode: bool) -> str:
    base = format_description(details, luxury_mode)
    trust = category_trust_line(details["category"])
    final = base + " " + trust
    return polish_text(final)


# =========================================================
# HOME PAGE — FINAL UPGRADED VERSION
# =========================================================

def page_home():
    st.image("image_1778389857310.jpeg", width=380)
    st.markdown("<h3 class='subtitle-glow'>Smarter listings. More sales. Less effort.</h3>", unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("<span class='stat-pill'>⚡ AI‑Optimised Titles</span>", unsafe_allow_html=True)
    with col_b:
        st.markdown("<span class='stat-pill'>💷 Dynamic Pricing v3</span>", unsafe_allow_html=True)
    with col_c:
        st.markdown("<span class='stat-pill'>🛍️ SEO‑Perfect Tags</span>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    # Luxury badge
    lux_badge = "luxury-badge-on" if st.session_state["luxury_mode"] else "luxury-badge-off"
    lux_text = "Luxury Mode: ON" if st.session_state["luxury_mode"] else "Luxury Mode: OFF"
    st.markdown(f"<span class='{lux_badge}'>{lux_text}</span>", unsafe_allow_html=True)

    st.markdown("### ✏️ Describe your item")
    st.caption("Be messy — brand, colour, condition, flaws, size, anything you remember.")

    user_text = st.text_area(
        "",
        height=150,
        placeholder="e.g. black north face puffer jacket mens medium worn a bit small rip on sleeve"
    )

    quick_sale = st.checkbox("Quick Sale Mode (15% cheaper)")

    generate = st.button("Generate Listing 💸", use_container_width=True)

    if generate:
        if not user_text.strip():
            st.warning("Type something first.")
            return

        if not check_paywall():
            return

        st.session_state["uses"] += 1
        st.session_state["last_input"] = user_text

        details = extract_details(user_text)
        details["material"] = infer_material(user_text)

        title = format_title(details, st.session_state["luxury_mode"])
        description = format_description_v3(details, st.session_state["luxury_mode"])
        price = calculate_price_v3(details, st.session_state["luxury_mode"], quick_sale)
        tags = generate_tags_v2(details, st.session_state["luxury_mode"])

        st.session_state["last_output"] = {
            "title": title,
            "description": description,
            "price": price,
            "tags": tags,
            "details": details
        }

        st.success("Listing generated!")

        st.markdown("### 🏷️ Title")
        st.code(title)

        st.markdown("### 📝 Description")
        st.code(description)

        st.markdown("### 💷 Price Recommendation")
        st.code(price)

        st.markdown("### 🔖 Tags")
        st.code(tags)

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
