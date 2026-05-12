from pydantic import BaseModel

class AnalyzeRequest(BaseModel):
    text: str

@app.post("/analyze")
def analyze_item(req: AnalyzeRequest):
    text = req.text.lower()

    # --- BRAND DETECTION ---
    brands = [
        "gucci","louis vuitton","lv","prada","balenciaga","dior","ysl","saint laurent",
        "burberry","fendi","versace","hermes","celine","off-white","amiri","palm angels",
        "fear of god","moncler","supreme","stussy","bape","palace","trapstar","corteiz",
        "essentials","kith","carhartt","stone island","nike","jordan","adidas","yeezy",
        "new balance","unknown london","syna world","the north face","north face",
        "patagonia","columbia","berghaus","rab","montane","arcteryx","zara","h&m",
        "primark","river island","asos","pull&bear","bershka","uniqlo","levis","diesel"
    ]

    detected_brand = "unbranded"
    for b in sorted(brands, key=len, reverse=True):
        if b in text:
            detected_brand = b
            break

    # --- CATEGORY DETECTION ---
    categories = {
        "coat": ["coat","jacket","puffer","parka"],
        "hoodie": ["hoodie","hoodies"],
        "tshirt": ["t shirt","t-shirt","tee","top"],
        "jeans": ["jeans","denim"],
        "dress": ["dress"],
        "trainers": ["trainers","sneakers","shoes","boots"],
        "tracksuit": ["tracksuit","joggers","trackies"],
        "bag": ["bag","handbag","tote"],
        "shorts": ["shorts"],
        "cargos": ["cargo","cargos"]
    }

    detected_category = "general"
    for cat, kws in categories.items():
        for k in kws:
            if k in text:
                detected_category = cat
                break

    # --- COLOUR DETECTION ---
    colours = [
        "black","white","red","blue","green","grey","gray","pink","purple","yellow",
        "brown","beige","cream","navy","khaki","orange"
    ]
    detected_colour = next((c for c in colours if c in text), "unknown")

    # --- SIZE DETECTION ---
    sizes = ["xs","s","m","l","xl","xxl","xxxl"]
    detected_size = next((s.upper() for s in sizes if f" {s} " in f" {text} "), "not specified")

    # --- CONDITION DETECTION ---
    if "brand new" in text or "bnwt" in text:
        condition = "New with tags"
    elif "worn once" in text or "like new" in text:
        condition = "Excellent"
    elif "worn" in text or "used" in text:
        condition = "Good"
    else:
        condition = "Good"

    # --- FLAW DETECTION ---
    flaws = []
    if "rip" in text or "tear" in text:
        flaws.append("minor rip / tear")
    if "hole" in text:
        flaws.append("small hole")
    if "stain" in text or "mark" in text:
        flaws.append("small mark / stain")
    if "bobble" in text or "bobbly" in text:
        flaws.append("light bobbling")

    flaw_text = ", ".join(flaws) if flaws else "none"

    return {
        "brand": detected_brand,
        "category": detected_category,
        "colour": detected_colour,
        "size": detected_size,
        "condition": condition,
        "flaws": flaw_text
    }from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow Streamlit to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can tighten this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "SellSmart AI Backend Running"}
