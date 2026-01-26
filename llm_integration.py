import google.generativeai as genai
from config import settings
import re

# Initialize Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

def extract_product_info(message: str):
    """Use Gemini to extract product information from messages"""
    if not settings.GEMINI_API_KEY:
        return extract_keywords_fallback(message)
    
    try:
        prompt = f"""
        Extract product information from this vendor message: "{message}"
        
        Return a JSON object with:
        - is_product_offer: boolean (true if the message is offering a product for sale)
        - product_name: string or null
        - product_category: string or null
        - price: number or null
        - quantity: number or null
        - description: string or null
        
        If no product information is found, set is_product_offer to false.
        """
        
        response = model.generate_content(prompt)
        # Parse the response and return as dict
        # This is a simplified implementation - you'd need to properly parse the JSON response
        return parse_gemini_response(response.text)
    except Exception as e:
        print(f"Gemini API error: {e}")
        return extract_keywords_fallback(message)

def parse_gemini_response(response_text):
    """Parse Gemini response to extract product info"""
    # This is a simplified implementation
    # You would need to implement proper JSON parsing
    try:
        # Extract JSON from response (Gemini might add explanations)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            import json
            return json.loads(json_match.group())
    except:
        pass
    
    return {
        "is_product_offer": False,
        "product_name": None,
        "product_category": None,
        "price": None,
        "quantity": None,
        "description": None
    }

def extract_keywords_fallback(message: str):
    """Fallback keyword extraction if Gemini fails"""
    keywords = []
    message_lower = message.lower()
    
    # Product categories
    categories = ["phone", "smartphone", "laptop", "computer", "tablet", "ipad", 
                 "shirt", "tshirt", "jeans", "shoes", "jacket", "clothing",
                 "coffee", "maker", "sheets", "lamp", "home", "appliance"]
    
    # Check if this is a product offer
    offer_words = ["sell", "offer", "have", "stock", "available", "supply"]
    is_offer = any(word in message_lower for word in offer_words)
    
    product_name = None
    product_category = None
    price = None
    quantity = None
    
    # Extract price
    price_pattern = r'\$?\d+(?:,\d{3})*(?:\.\d{2})?'
    prices = re.findall(price_pattern, message)
    if prices:
        price = float(prices[0].replace('$', '').replace(',', ''))
    
    # Extract quantity
    quantity_pattern = r'(\d+)\s*(pcs|pieces|units|items)'
    quantity_match = re.search(quantity_pattern, message_lower)
    if quantity_match:
        quantity = int(quantity_match.group(1))
    
    return {
        "is_product_offer": is_offer,
        "product_name": product_name,
        "product_category": product_category,
        "price": price,
        "quantity": quantity or 1,
        "description": message
    }

def generate_vendor_response(message: str, sender: str, chat_history: list = None):
    """Generate a vendor response using Gemini"""
    if not settings.GEMINI_API_KEY:
        return generate_vendor_response_fallback(message, sender)
    
    try:
        history_context = ""
        if chat_history:
            # Use last 5 messages for context
            recent_messages = chat_history[-5:] if len(chat_history) > 5 else chat_history
            history_context = "Previous conversation:\n" + "\n".join(
                [f"{msg['sender']}: {msg['message']}" for msg in recent_messages]
            )
        
        prompt = f"""
        You are a vendor in a business-to-business chat system. 
        {history_context}
        
        The other vendor ({sender}) just said: "{message}"
        
        Respond as a professional vendor. Keep your response concise and business-appropriate.
        If they're offering products, ask relevant questions about specifications, pricing, or quantities.
        If they're looking to buy, offer suitable products from your inventory.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return generate_vendor_response_fallback(message, sender)

def generate_vendor_response_fallback(message: str, sender: str):
    """Fallback response generation if Gemini fails"""
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
    
    import random
    return random.choice(responses)