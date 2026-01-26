
import re
from typing import List, Dict, Optional
import random

PRODUCTS_DB = {
    "electronics": [
        {"id": 1, "name": "iPhone 15", "category": "smartphones", "price": 999, "supplier": "TechCorp"},
        {"id": 2, "name": "Samsung Galaxy S24", "category": "smartphones", "price": 899, "supplier": "MobileTech"},
        {"id": 3, "name": "MacBook Pro", "category": "laptops", "price": 1999, "supplier": "TechCorp"},
        {"id": 4, "name": "Dell XPS 13", "category": "laptops", "price": 1299, "supplier": "CompuWorld"},
        {"id": 5, "name": "iPad Air", "category": "tablets", "price": 599, "supplier": "TechCorp"},
    ],
    "clothing": [
        {"id": 6, "name": "Cotton T-Shirt", "category": "apparel", "price": 25, "supplier": "FashionHub"},
        {"id": 7, "name": "Denim Jeans", "category": "apparel", "price": 79, "supplier": "StyleCo"},
        {"id": 8, "name": "Running Shoes", "category": "footwear", "price": 120, "supplier": "SportGear"},
        {"id": 9, "name": "Winter Jacket", "category": "outerwear", "price": 199, "supplier": "OutdoorPro"},
    ],
    "home": [
        {"id": 10, "name": "Coffee Maker", "category": "appliances", "price": 149, "supplier": "HomeEssentials"},
        {"id": 11, "name": "Bed Sheets Set", "category": "bedding", "price": 89, "supplier": "ComfortCo"},
        {"id": 12, "name": "LED Desk Lamp", "category": "lighting", "price": 45, "supplier": "LightTech"},
    ]
}

def extract_keywords(text: str) -> List[str]:
    keywords = []
    text_lower = text.lower()
    categories = ["phone", "smartphone", "laptop", "computer", "tablet", "ipad", 
                  "shirt", "tshirt", "jeans", "shoes", "jacket", "clothing",
                  "coffee", "maker", "sheets", "lamp", "home", "appliance"]
    brands = ["iphone", "samsung", "macbook", "dell", "ipad", "apple"]
    for category in categories:
        if category in text_lower:
            keywords.append(category)
    for brand in brands:
        if brand in text_lower:
            keywords.append(brand)
    return keywords

def get_product_recommendations(keywords: List[str], budget: Optional[float] = None) -> List[Dict]:
    recommendations = []
    for category, products in PRODUCTS_DB.items():
        for product in products:
            score = 0
            product_text = (product["name"] + " " + product["category"]).lower()
            for keyword in keywords:
                if keyword in product_text:
                    score += 1
            if budget and product["price"] <= budget:
                score += 0.5
            if score > 0:
                recommendations.append({**product, "relevance_score": score})
    recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
    return recommendations[:5]

def generate_vendor_response(message: str, sender: str) -> str:
    message_lower = message.lower()
    if any(word in message_lower for word in ["buy", "purchase", "need", "looking for"]):
        responses = [
            "I can help you with that! What's your budget range?",
            "Great! I have some excellent options. What specific features are you looking for?",
            "Perfect timing! I have some new inventory that might interest you.",
            "I'd be happy to discuss bulk pricing. How many units are you thinking?",
        ]
    elif any(word in message_lower for word in ["sell", "offer", "have", "stock"]):
        responses = [
            "That sounds interesting! What's your wholesale pricing?",
            "I might be interested. Can you tell me more about the specifications?",
            "Do you have bulk quantities available? I'm looking for a reliable supplier.",
            "What's the minimum order quantity for those items?",
        ]
    elif any(word in message_lower for word in ["price", "cost", "budget"]):
        responses = [
            "Let me check my current pricing. I can offer competitive rates for bulk orders.",
            "Price depends on quantity. What volume are you looking at?",
            "I can work with different budget ranges. What's your target price point?",
        ]
    else:
        responses = [
            "Tell me more about what you're looking for.",
            "I'm listening. What can I help you with today?",
            "That's interesting. How can we work together on this?",
        ]
    return random.choice(responses)
