import streamlit as st
import re
from difflib import SequenceMatcher

# -----------------------------------
# SELL SMART AI – v3.3
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
# GLOBAL UI STYLING (PREMIUM THEME)
# -----------------------------------
st.markdown("""
<style>

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

/* Center the main content */
.main {
    padding-top: 20px;
}

/* Input box styling */
textarea {
    border-radius: 12px !important;
    border: 1px solid #3a3a3a !important;
    background-color: #111 !important;
    color: #e5e5e5 !important;
    padding: 12px !important;
    font-size: 15px !important;
}

/* Card container */
.card {
    background-color: #0f0f0f;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 0 25px rgba(0, 255, 150, 0.15);
    margin-top: 20px;
    margin-bottom: 20px;
}

/* Generate button */
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

/* Output code boxes */
code {
    font-size: 15px !important;
    line-height: 1.5 !important;
}

/* Footer spacing */
footer {
    margin-top: 40px;
}

</style>
""", unsafe_allow_html=True)
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

st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
st.image("image_1778389857310.jpeg", width=380)
st.markdown("</div>", unsafe_allow_html=True)

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
# ENGINE (from your v3.3 file)
# -----------------------------------

BRANDS = {
    "sportswear": [
        "nike", "adidas", "puma", "reebok", "asics", "under armour",
        "gymshark", "champion", "fila", "new balance", "converse",
        "vans", "salomon", "the north face", "north face", "patagonia",
        "columbia", "umbro", "lotto", "kappa"
    ],
    "streetwear": [
        "supreme", "palace", "stussy", "carhartt", "dickies", "obey",
        "bape", "a bathing ape", "off-white", "essentials", "trapstar",
        "hoodrich", "siksilk", "11 degrees", "represent", "corteiz",
        "huf", "billionaire boys club"
    ],
    "designer": [
        "armani", "emporio armani", "giorgio armani", "hugo boss", "boss",
        "calvin klein", "ck", "tommy hilfiger", "ralph lauren",
        "polo ralph lauren", "lacoste", "burberry", "stone island",
        "canada goose", "moncler", "diesel", "guess", "levi", "levis",
        "versace", "kenzo", "paul smith", "allsaints", "ted baker"
    ],
    "luxury": [
        "gucci", "prada", "louis vuitton", "lv", "balenciaga", "dior",
        "ysl", "saint laurent", "fendi", "valentino", "celine", "loewe",
        "maison margiela", "givenchy", "hermes", "bottega veneta"
    ],
    "high_street": [
        "zara", "zara man", "zara woman", "h&m", "cos", "weekday",
        "monki", "mango", "pull&bear", "bershka", "stradivarius",
        "river island", "new look", "primark", "george", "matalan",
        "next", "topman", "topshop", "asos", "asos design", "boohoo",
        "boohoo man", "prettylittlething", "plt", "missguided", "shein",
        "oh polly", "house of cb", "lipsy", "coast", "jack & jones",
        "only & sons", "selected homme"
    ],
    "outdoor": [
        "regatta", "berghaus", "craghoppers", "helly hansen", "rab",
        "jack wolfskin", "mountain warehouse", "columbia", "sprayway"
    ],
    "footwear": [
        "dr martens", "doc martens", "ugg", "clarks", "birkenstock",
        "crocs", "timberland", "yeezy", "jordan", "nike air max",
        "adidas originals", "air force 1", "air jordan", "new balance"
    ],
    "kids": [
        "mothercare", "jojo maman bébé", "mini boden", "boden",
        "m&s kids", "marks & spencer", "george kids", "next kids"
    ]
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
                score = max(fuzzy_ratio(word, brand_lower) for word in words) if words else 0
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

def extract_details(text):
    original_text = text
    text = text.lower()

    brand = best_match_brand(text)

    items = [
        "jeans", "jacket", "hoodie", "t-shirt", "shirt", "shorts",
        "trousers", "coat", "jumper", "fleece", "top", "dress",
        "leggings", "cargo pants", "cargo trousers", "sweatshirt",
        "tracksuit", "puffer jacket", "gilet"
    ]
    item = next((i for i in items if i in text), "Item")

    if "men" in text or "male" in text or "man " in text:
        gender = "Men"
    elif "women" in text or "ladies" in text or "female" in text:
        gender = "Women"
    elif "girls" in text:
        gender = "Girls"
    elif "boys" in text:
        gender = "Boys"
    else:
        gender = "Unisex"

    fits = [
        "slim fit", "regular fit", "relaxed fit", "skinny", "straight leg",
        "bootcut", "baggy", "oversized", "tapered", "loose fit"
    ]
    fit = next((f for f in fits if f in text), "Regular Fit")

    size_patterns = [
        r"size\s*\d+[a-z]?",
        r"size\s*[a-z]+",
        r"\b(w\d+\s*l\d+)\b",
        r"\b\d{2}\/\d{2}\b",
        r"\bsmall\b", r"\bmedium\b", r"\blarge\b",
        r"\bxl\b", r"\bxxl\b", r"\bs\b", r"\bm\b",
        r"\bl\b", r"\bxs\b", r"\bxxs\b"
    ]
    size = "Unknown"
    for pattern in size_patterns:
        match = re.search(pattern, text)
        if match:
            size = match.group(0).replace("size", "").strip()
            break

    measurements = []
    measure_patterns = [
        r"\b\d{2}\s*waist\b",
        r"\bwaist\s*\d{2}\b",
        r"\bleg\s*\d{2}\b",
        r"\b\d{2}\s*leg\b",
        r"pit to pit\s*\d{2}",
        r"length\s*\d{2,3}"
    ]
    for p in measure_patterns:
        m = re.findall(p, text)
        if m:
            measurements.extend(m)

    colours = [
        "black", "white", "blue", "red", "green", "grey", "gray", "pink",
        "yellow", "purple", "brown", "beige", "navy", "cream", "khaki",
        "tan", "burgundy", "maroon", "orange", "teal", "turquoise"
    ]
    colour = next((c for c in colours if c in text), "Unknown")
    if colour == "gray":
        colour = "Grey"

    conditions = ["brand new", "new", "excellent", "very good", "good", "used"]
    condition = "Unknown"
    for c in conditions:
        if c in text:
            condition = c.title()
            break

    if "denim" in text or "jeans" in text:
        material = "Denim"
    elif "fleece" in text:
        material = "Fleece"
    elif "wool" in text:
        material = "Wool"
    elif "leather" in text:
        material = "Leather"
    elif "linen" in text:
        material = "Linen"
    elif "cotton" in text:
        material = "Cotton"
    elif "polyester" in text:
        material = "Polyester"
    elif "nylon" in text:
        material = "Nylon"
    else:
        material = "Unknown"

    patterns = [
        "striped", "checked", "checkered", "plaid", "floral",
        "printed", "graphic", "plain", "solid", "logo"
    ]
    pattern = next((p for p in patterns if p in text), "Plain" if "plain" in text else "Unknown")

    keywords = [
        "zip fly", "button fastening", "five pocket", "belt loops",
        "drawstring", "elastic waist", "zip pockets", "cargo pockets",
        "ribbed cuffs", "embroidered logo", "graphic print", "crew neck",
        "v-neck", "quarter zip", "half zip", "full zip", "kangaroo pocket",
        "fleece lined", "padded", "quilted", "waterproof", "windproof",
        "insulated", "lined"
    ]
    features = [k for k in keywords if k in text]

    logo_map = {
        "big logo": "Large front logo",
        "small logo": "Small chest logo",
        "chest logo": "Chest logo",
        "back print": "Back print graphic"
    }
    logo_features = [v for k, v in logo_map.items() if k in text]

    rises = [
        "high rise", "mid rise", "low rise",
        "high waisted", "mid waisted", "low waisted"
    ]
    rise = next((r for r in rises if r in text), "Unknown")

    stretch = any(k in text for k in ["stretch", "stretchy", "elastane", "flex"])

    rrp_match = re.search(r"rrp\s*£?\s*(\d+)", text)
    rrp = rrp_match.group(1) if rrp_match else None

    smoke_free = "smoke free" in text or "smoke-free" in text
    pet_free = "pet free" in text or "pet-free" in text

    vintage = any(k in text for k in ["vintage", "y2k", "retro"])

    limited = any(k in text for k in ["limited edition", "rare", "sold out"])

    flaw_keywords = [
        "mark", "stain", "hole", "rip", "tear", "snag", "loose thread",
        "pulled thread", "bobble", "bobbles", "pilling", "faded",
        "fading", "scuff", "scuffs"
    ]
    negative_context = [
        "has", "have", "with", "shows", "showing",
        "there is", "there's", "some", "slight", "small", "tiny"
    ]
    ignore_phrases = [
        "no marks", "no stains", "no holes", "no rips", "no tears",
        "no flaws", "no damage", "no signs of wear",
        "barely worn", "light wear", "normal wear"
    ]

    flaws = []
    if not any(p in text for p in ignore_phrases):
        for fk in flaw_keywords:
            if fk in text:
                for ctx in negative_context:
                    if re.search(rf"{ctx}[^.]*{fk}|{fk}[^.]*{ctx}", text):
                        flaws.append(fk)
                        break

    if gender == "Men" and "jeans" in item:
        category = "Men's Jeans"
    elif gender == "Men" and "hoodie" in item:
        category = "Men's Hoodies"
    elif gender == "Women" and "dress" in item:
        category = "Women's Dresses"
    else:
        category = f"{gender} {item.title()}"

    return {
        "brand": brand.title(),
        "item": item.title(),
        "gender": gender,
        "fit": fit.title(),
        "size": size.title(),
        "colour": colour.title(),
        "condition": condition.title(),
        "material": material.title(),
        "pattern": pattern.title(),
        "features": features + logo_features,
        "rise": rise.title(),
        "stretch": stretch,
        "flaws": flaws,
        "category": category,
        "measurements": measurements,
        "rrp": rrp,
        "smoke_free": smoke_free,
        "pet_free": pet_free,
        "vintage": vintage,
        "limited": limited
    }

def price_recommendation(brand, condition, has_flaws=False):
    brand_lower = brand.lower()
    condition_lower = condition.lower()

    if any(b in brand_lower for b in ["primark", "pepco", "george", "shein"]):
        base = 3
    elif any(b in brand_lower for b in ["boohoo", "new look", "matalan", "asos", "river island"]):
        base = 6
    elif any(b in brand_lower for b in ["nike", "adidas", "puma", "reebok", "vans", "converse", "north face", "berghaus"]):
        base = 12
    elif any(b in brand_lower for b in ["levi", "levis", "tommy hilfiger", "ralph lauren", "lacoste", "stone island"]):
        base = 18
    elif any(b in brand_lower for b in ["gucci", "prada", "louis vuitton", "balenciaga", "dior", "ysl", "fendi", "valentino"]):
        base = 40
    else:
        base = 7

    if "brand new" in condition_lower or condition_lower == "new":
        base += 4
    elif "excellent" in condition_lower:
        base += 2
    elif "very good" in condition_lower:
        base += 1
    elif "used" in condition_lower:
        base -= 1

    if has_flaws:
        base -= 2

    if base < 2:
        base = 2

    return f"£{base}"

def generate_listing(details):
    condition_order = ["Brand New", "New", "Excellent", "Very Good", "Good", "Used"]
    condition = details["condition"]
    if details["flaws"] and condition in condition_order:
        idx = condition_order.index(condition)
        condition_effective = condition_order[min(idx + 1, len(condition_order) - 1)]
    else:
        condition_effective = condition

    title = (
        f"{details['brand']} "
        f"{details['colour']} "
        f"{details['material']} "
        f"{details['item']} – "
        f"{details['gender']} Size {details['size']}"
    )

    condition_sentences = {
        "Brand New": "Brand new condition — never worn.",
        "New": "New condition — tried on only.",
        "Excellent": "Excellent condition — barely worn with no flaws.",
        "Very Good": "Very good condition — no major marks, fading, or damage.",
        "Good": "Good condition — light signs of wear but nothing major.",
        "Used": "Used condition — shows wear but still fully wearable."
    }
    condition_line = condition_sentences.get(condition_effective, "Good used condition.")

    flaw_line = ""
    if details["flaws"]:
        flaw_line = (
            "Flaws noted: "
            + ", ".join(sorted(set(details["flaws"])))
            + " (shown in photos)."
        )

    use_cases = {
        "Jeans": "Great for everyday wear, casual outfits, or pairing with trainers.",
        "Hoodie": "Perfect for casual wear, lounging, or layering in colder weather.",
        "Jacket": "Ideal for outdoor wear, layering, or everyday use.",
        "T-Shirt": "Perfect for casual outfits, gym wear, or layering.",
        "Shirt": "Great for smart‑casual outfits, workwear, or evenings out.",
        "Fleece": "Warm and comfortable — ideal for outdoor activities or layering.",
        "Coat": "Ideal for colder days and layering over winter outfits."
    }
    use_case_line = use_cases.get(details["item"], "Ideal for everyday wear or casual outfits.")

    seasonal_trending = []
    item_lower = details["item"].lower()

    if item_lower in ["shorts", "t-shirt", "top"]:
        seasonal_trending.append("Great for warmer weather and summer outfits.")
    if item_lower in ["coat", "jacket", "fleece", "hoodie", "jumper", "puffer jacket"]:
        seasonal_trending.append("Ideal for colder weather and layering.")
    if "cargo" in item_lower:
        seasonal_trending.append("Cargo style is currently trending and in high demand.")
    if details["vintage"]:
        seasonal_trending.append("Vintage/Y2K style — popular and in demand.")
    if "levi" in details["brand"].lower():
        seasonal_trending.append("Classic denim brand with strong resale demand.")

    seasonal_line = " ".join(seasonal_trending)

    high_demand = False
    size_lower = details["size"].lower()
    if details["gender"] == "Men" and any(s in size_lower for s in ["large", "l", "xl", "xxl"]):
        high_demand = True
    if details["gender"] == "Women" and any(ch.isdigit() for ch in size_lower):
        high_demand = True

    size_line = "Popular size — tends to sell quickly on Vinted." if high_demand else ""

    brand_notes = {
        "Levi": "Levi’s are known for durable, high‑quality denim with strong resale value.",
        "Levis": "Levi’s are known for durable, high‑quality denim with strong resale value.",
        "Nike": "Nike is a popular sportswear brand with high demand on resale platforms.",
        "Adidas": "Adidas is a well‑known sportswear brand with consistent resale interest.",
        "The North Face": "The North Face is a premium outdoor brand with strong resale value.",
        "North Face": "The North Face is a premium outdoor brand with strong resale value.",
        "Ralph Lauren": "Ralph Lauren pieces often hold value due to their classic style.",
        "Tommy Hilfiger": "Tommy Hilfiger is a popular brand with good resale demand.",
        "Stone Island": "Stone Island is highly sought after and holds resale value well.",
        "Canada Goose": "Canada Goose outerwear is premium and in high demand."
    }
    brand_line = brand_notes.get(details["brand"], "")

    measurements_line = ""
    if details["measurements"]:
        measurements_line = "Measurements: " + ", ".join(details["measurements"]) + "."

    rrp_line = ""
    if details["rrp"]:
        rrp_line = f"Originally £{details['rrp']} RRP — great saving."

    home_line = ""
    if details["smoke_free"] and details["pet_free"]:
        home_line = "From a smoke‑free, pet‑free home."
    elif details["smoke_free"]:
        home_line = "From a smoke‑free home."
    elif details["pet_free"]:
        home_line = "From a pet‑free home."

    limited_line = ""
    if details["limited"]:
        limited_line = "Limited edition / rare item — harder to find."

    feature_line = ""
    if details["features"]:
        feature_line = "Features: " + ", ".join(details["features"]) + "."

    description_parts = [
        f"{details['gender']} {details['material'].lower()} {details['item'].lower()} in Size {details['size']}.",
        condition_line,
        flaw_line,
        use_case_line,
        seasonal_line,
        size_line,
        brand_line,
        measurements_line,
        rrp_line,
        home_line,
        limited_line,
        feature_line,
        "",
        "Details:",
        f"- Brand: {details['brand']}",
        f"- Category: {details['category']}",
        f"- Size: {details['size']}",
        f"- Colour: {details['colour']}",
        f"- Material: {details['material']}",
        f"- Fit: {details['fit']}",
        f"- Condition: {condition_effective}",
        f"- Pattern: {details['pattern']}",
        f"- Rise: {details['rise']}",
        f"- Stretch: {'Yes' if details['stretch'] else 'No'}",
        f"- Features: {', '.join(details['features']) if details['features'] else 'N/A'}",
        "",
        "Recommended photos: front, back, close‑ups, size tag, brand label.",
        "Offer: bundle 2+ items for a discount."
    ]

    description = "\n".join([p for p in description_parts if p])

    tags = (
        f"{details['brand'].lower()}, "
        f"{details['item'].lower()}, "
        f"{details['gender'].lower()}, "
        f"size {details['size'].lower()}, "
        f"{details['colour'].lower()}, "
        f"{details['material'].lower()}, "
        f"{details['fit'].lower()}, "
        f"{details['category'].lower()}, "
        f"vinted, clothing"
    )

    return title, description, tags

# -----------------------------------
# INPUT
# -----------------------------------st.markdown("<div class='card'>", unsafe_allow_html=True)
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

        st.info("Tip: long‑press to copy on mobile, or right‑click → copy on desktop.")
st.markdown("""
<hr style='margin-top:40px; margin-bottom:10px;'>

<div style='text-align:center; font-size:14px; color:#9ca3af;'>
    SellSmart AI © 2026<br>
    <a href="/terms" target="_blank">Terms of Service</a> •
    <a href="/privacy" target="_blank">Privacy Policy</a> •
    <a href="/aup" target="_blank">Acceptable Use</a> •
    <a href="/refunds" target="_blank">Refund Policy</a>
</div>
""", unsafe_allow_html=True)
st.markdown("""
<hr style='margin-top:40px; margin-bottom:10px;'>

<div style='text-align:center; font-size:14px; color:#9ca3af;'>
    SellSmart AI © 2026<br>
    <a href="/terms" target="_blank">Terms of Service</a> •
    <a href="/privacy" target="_blank">Privacy Policy</a> •
    <a href="/aup" target="_blank">Acceptable Use</a> •
    <a href="/refunds" target="_blank">Refund Policy</a>
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
