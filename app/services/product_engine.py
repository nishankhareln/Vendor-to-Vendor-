"""
Rule-based product extraction and market intelligence.
No LLM required — uses keyword matching, regex, and a built-in market catalog.
Supports English and Nepali (नेपाली).
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Nepali ↔ English mappings
# ---------------------------------------------------------------------------

NEPALI_TO_ENGLISH = {
    # Products
    "चामल": "rice", "दाल": "lentils", "तेल": "oil", "चिनी": "sugar",
    "नुन": "salt", "पीठो": "flour", "मैदा": "maida", "चिउरा": "chiura",
    "गहुँ": "wheat", "मकै": "corn", "आलु": "potato", "प्याज": "onion",
    "गोलभेडा": "tomato", "लसुन": "garlic", "अदुवा": "ginger",
    "दूध": "milk", "दही": "yogurt", "घिउ": "ghee", "मासु": "meat",
    "कुखुरा": "chicken", "माछा": "fish", "अण्डा": "egg",
    "सिमेन्ट": "cement", "छड": "rod", "इँटा": "brick", "बालुवा": "sand",
    "फोन": "phone", "मोबाइल": "mobile", "ल्यापटप": "laptop",
    "कपडा": "cloth", "जुत्ता": "shoes", "चप्पल": "sandals",
    # Categories
    "खाद्य": "grocery", "खाना": "food", "किराना": "grocery",
    "निर्माण": "construction", "इलेक्ट्रोनिक्स": "electronics",
    "कपडा": "clothing", "सब्जी": "vegetables", "फलफूल": "fruits",
    "मसला": "spices",
    # Action words
    "बेच्नु": "sell", "बेच्छु": "sell", "बेच्ने": "sell",
    "किन्नु": "buy", "किन्छु": "buy", "किन्ने": "buy",
    "चाहिन्छ": "need", "चाहियो": "need", "छ": "available",
    "स्टक": "stock", "उपलब्ध": "available",
    "मूल्य": "price", "दाम": "price", "रेट": "rate",
    "कति": "how much", "किलो": "kg", "केजी": "kg",
    "बोरा": "sack", "पाथी": "pathi", "मुरी": "muri",
    "वटा": "pieces", "गोटा": "pieces", "थान": "pieces",
}

# Nepali digits → ASCII
NEPALI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


# ---------------------------------------------------------------------------
# Market price catalog (NPR) — average wholesale rates
# ---------------------------------------------------------------------------

MARKET_CATALOG: dict[str, dict[str, Any]] = {
    # --- Grocery / Food ---
    "rice": {"name_np": "चामल", "category": "grocery", "unit": "kg", "market_price": 80, "price_range": (60, 120)},
    "lentils": {"name_np": "दाल", "category": "grocery", "unit": "kg", "market_price": 180, "price_range": (140, 250)},
    "oil": {"name_np": "तेल", "category": "grocery", "unit": "ltr", "market_price": 220, "price_range": (180, 300)},
    "sugar": {"name_np": "चिनी", "category": "grocery", "unit": "kg", "market_price": 110, "price_range": (90, 140)},
    "salt": {"name_np": "नुन", "category": "grocery", "unit": "kg", "market_price": 30, "price_range": (20, 45)},
    "flour": {"name_np": "पीठो", "category": "grocery", "unit": "kg", "market_price": 65, "price_range": (50, 90)},
    "maida": {"name_np": "मैदा", "category": "grocery", "unit": "kg", "market_price": 70, "price_range": (55, 95)},
    "chiura": {"name_np": "चिउरा", "category": "grocery", "unit": "kg", "market_price": 90, "price_range": (70, 130)},
    "wheat": {"name_np": "गहुँ", "category": "grocery", "unit": "kg", "market_price": 45, "price_range": (35, 60)},
    "corn": {"name_np": "मकै", "category": "grocery", "unit": "kg", "market_price": 40, "price_range": (30, 55)},
    "ghee": {"name_np": "घिउ", "category": "grocery", "unit": "kg", "market_price": 900, "price_range": (700, 1200)},
    # --- Vegetables ---
    "potato": {"name_np": "आलु", "category": "vegetables", "unit": "kg", "market_price": 45, "price_range": (30, 70)},
    "onion": {"name_np": "प्याज", "category": "vegetables", "unit": "kg", "market_price": 60, "price_range": (35, 100)},
    "tomato": {"name_np": "गोलभेडा", "category": "vegetables", "unit": "kg", "market_price": 50, "price_range": (30, 90)},
    "garlic": {"name_np": "लसुन", "category": "vegetables", "unit": "kg", "market_price": 300, "price_range": (200, 450)},
    "ginger": {"name_np": "अदुवा", "category": "vegetables", "unit": "kg", "market_price": 250, "price_range": (180, 350)},
    # --- Meat / Dairy ---
    "chicken": {"name_np": "कुखुरा", "category": "meat", "unit": "kg", "market_price": 380, "price_range": (320, 450)},
    "meat": {"name_np": "मासु", "category": "meat", "unit": "kg", "market_price": 700, "price_range": (550, 900)},
    "fish": {"name_np": "माछा", "category": "meat", "unit": "kg", "market_price": 450, "price_range": (300, 650)},
    "egg": {"name_np": "अण्डा", "category": "meat", "unit": "piece", "market_price": 16, "price_range": (13, 20)},
    "milk": {"name_np": "दूध", "category": "dairy", "unit": "ltr", "market_price": 80, "price_range": (65, 100)},
    "yogurt": {"name_np": "दही", "category": "dairy", "unit": "ltr", "market_price": 100, "price_range": (80, 130)},
    # --- Construction ---
    "cement": {"name_np": "सिमेन्ट", "category": "construction", "unit": "bag", "market_price": 680, "price_range": (620, 780)},
    "rod": {"name_np": "छड", "category": "construction", "unit": "kg", "market_price": 110, "price_range": (95, 130)},
    "brick": {"name_np": "इँटा", "category": "construction", "unit": "piece", "market_price": 18, "price_range": (14, 24)},
    "sand": {"name_np": "बालुवा", "category": "construction", "unit": "truck", "market_price": 18000, "price_range": (14000, 22000)},
    # --- Electronics ---
    "phone": {"name_np": "फोन", "category": "electronics", "unit": "piece", "market_price": 25000, "price_range": (8000, 80000)},
    "mobile": {"name_np": "मोबाइल", "category": "electronics", "unit": "piece", "market_price": 25000, "price_range": (8000, 80000)},
    "laptop": {"name_np": "ल्यापटप", "category": "electronics", "unit": "piece", "market_price": 75000, "price_range": (35000, 200000)},
    # --- Clothing ---
    "cloth": {"name_np": "कपडा", "category": "clothing", "unit": "meter", "market_price": 350, "price_range": (100, 800)},
    "shoes": {"name_np": "जुत्ता", "category": "clothing", "unit": "pair", "market_price": 1500, "price_range": (500, 5000)},
    "sandals": {"name_np": "चप्पल", "category": "clothing", "unit": "pair", "market_price": 500, "price_range": (200, 1500)},
}


# ---------------------------------------------------------------------------
# Text normalization
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Normalize text: convert Nepali digits, translate Nepali words to English."""
    text = text.translate(NEPALI_DIGITS)
    lower = text.lower()
    for np_word, en_word in NEPALI_TO_ENGLISH.items():
        if np_word in text:
            lower = lower + " " + en_word
    return lower


# ---------------------------------------------------------------------------
# Product extraction from messages
# ---------------------------------------------------------------------------

def extract_product_info(message: str) -> dict[str, Any]:
    """Extract product info from a chat message using keyword + regex matching."""
    normalized = _normalize(message)

    # Detect offer intent — match natural phrases vendors actually use
    offer_words = [
        "sell", "offer", "stock", "available", "supply", "wholesale",
        "have for sale", "i have", "i had", "i got", "we have", "we got",
        "selling", "offering", "providing",
        "मसँग", "हामीसँग", "छ", "उपलब्ध", "बेच्छु", "बेच्ने", "स्टक",
    ]
    is_offer = any(w in normalized for w in offer_words)

    # Find matching product from catalog
    product_name = None
    product_category = None
    matched_key = None

    for key, info in MARKET_CATALOG.items():
        if key in normalized or info["name_np"] in message:
            product_name = key
            product_category = info["category"]
            matched_key = key
            break

    # Extract price (supports Rs, Rs., NPR, रु, ₨, and no-space like Rs50)
    price = None
    price_patterns = [
        r"(?:rs\.?|npr\.?|रु\.?|₨)\s*([\d,]+(?:\.\d{1,2})?)",
        r"([\d,]+(?:\.\d{1,2})?)\s*(?:rs\.?|npr\.?|रु\.?|₨|रुपैयाँ|per\s+kg|per\s+unit|per\s+piece|प्रति)",
        r"\$\s*([\d,]+(?:\.\d{1,2})?)",
        r"(?:price|rate|cost|मूल्य|दाम|रेट)\s*[:\-]?\s*(?:rs\.?|रु\.?)?\s*([\d,]+(?:\.\d{1,2})?)",
        r"(?:at|@)\s*(?:rs\.?|रु\.?)?\s*([\d,]+(?:\.\d{1,2})?)",
    ]
    for pattern in price_patterns:
        match = re.search(pattern, normalized)
        if not match:
            match = re.search(pattern, message, re.IGNORECASE)
        if match:
            price = float(match.group(1).replace(",", ""))
            break

    # Extract quantity
    quantity = 1
    qty_patterns = [
        r"(\d+)\s*(?:kg|केजी|किलो|ltr|लिटर|bag|बोरा|piece|pcs|वटा|गोटा|थान|unit|pair|जोडी|truck|meter|मिटर|muri|मुरी|pathi|पाथी)",
        r"(\d+)\s*(?:pieces|units|items|bags|sacks|dozen)",
    ]
    for pattern in qty_patterns:
        qty_match = re.search(pattern, normalized)
        if not qty_match:
            qty_match = re.search(pattern, message)
        if qty_match:
            quantity = int(qty_match.group(1))
            break

    return {
        "is_product_offer": is_offer and product_name is not None,
        "product_name": product_name,
        "product_category": product_category,
        "price": price,
        "quantity": quantity,
        "description": message,
        "matched_key": matched_key,
    }


# ---------------------------------------------------------------------------
# Market price comparison
# ---------------------------------------------------------------------------

def get_market_price(product_key: str) -> dict[str, Any] | None:
    """Get market price info for a product."""
    info = MARKET_CATALOG.get(product_key)
    if not info:
        for key, val in MARKET_CATALOG.items():
            if val["name_np"] == product_key or key in product_key:
                info = val
                product_key = key
                break
    if not info:
        return None

    return {
        "product": product_key,
        "name_np": info["name_np"],
        "category": info["category"],
        "unit": info["unit"],
        "market_price": info["market_price"],
        "price_min": info["price_range"][0],
        "price_max": info["price_range"][1],
    }


def compare_price(product_key: str, offered_price: float) -> dict[str, Any] | None:
    """Compare an offered price against market rate."""
    market = get_market_price(product_key)
    if not market:
        return None

    mp = market["market_price"]
    diff = offered_price - mp
    diff_pct = (diff / mp) * 100

    if diff_pct > 10:
        verdict = "above_market"
        verdict_np = "बजार भाउ भन्दा महँगो"
    elif diff_pct < -10:
        verdict = "below_market"
        verdict_np = "बजार भाउ भन्दा सस्तो"
    else:
        verdict = "fair_price"
        verdict_np = "उचित मूल्य"

    return {
        **market,
        "offered_price": offered_price,
        "difference": round(diff, 2),
        "difference_pct": round(diff_pct, 1),
        "verdict": verdict,
        "verdict_np": verdict_np,
    }


def search_market_catalog(query: str) -> list[dict[str, Any]]:
    """Search the market catalog by keyword (English or Nepali)."""
    normalized = _normalize(query)
    results = []
    for key, info in MARKET_CATALOG.items():
        if (
            key in normalized
            or info["name_np"] in query
            or info["category"] in normalized
        ):
            results.append({
                "product": key,
                "name_np": info["name_np"],
                "category": info["category"],
                "unit": info["unit"],
                "market_price": info["market_price"],
                "price_min": info["price_range"][0],
                "price_max": info["price_range"][1],
            })
    return results


def get_all_market_prices() -> list[dict[str, Any]]:
    """Return the full market catalog."""
    return [
        {
            "product": key,
            "name_np": info["name_np"],
            "category": info["category"],
            "unit": info["unit"],
            "market_price": info["market_price"],
            "price_min": info["price_range"][0],
            "price_max": info["price_range"][1],
        }
        for key, info in MARKET_CATALOG.items()
    ]
