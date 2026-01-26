import streamlit as st
import requests
from datetime import datetime
import time

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Vendor Chat System", layout="wide")
st.title("🤝 Vendor-to-Vendor Chat System")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "products" not in st.session_state:
    st.session_state.products = []
if "last_update" not in st.session_state:
    st.session_state.last_update = datetime.now()

# Function to refresh chat
def refresh_chat():
    try:
        response = requests.get(f"{API_URL}/chat/history")
        if response.status_code == 200:
            st.session_state.chat_history = response.json()["chat_history"]
        
        response = requests.get(f"{API_URL}/products")
        if response.status_code == 200:
            st.session_state.products = response.json()["products"]
            
        st.session_state.last_update = datetime.now()
    except:
        st.error("Could not connect to server")

# Auto-refresh every 5 seconds
if (datetime.now() - st.session_state.last_update).seconds > 5:
    refresh_chat()

# Sidebar for user info and controls
st.sidebar.title("User Info")
sender = st.sidebar.selectbox("Select Your Vendor Role", ["Vendor A", "Vendor B"])

# Manual refresh button
if st.sidebar.button("🔄 Refresh Chat"):
    refresh_chat()
    st.rerun()

# Main chat interface
st.subheader("💬 Live Chat")

# Display chat history
for msg in st.session_state.chat_history:
    timestamp = datetime.fromisoformat(msg['timestamp']).strftime("%H:%M:%S")
    st.markdown(f"**{msg['sender']} ({timestamp}):** {msg['message']}")

# Message input at the bottom
st.divider()
message = st.text_input("Type your message and press Enter to send", key="message_input")

if message:
    payload = {
        "sender": sender,
        "message": message
    }
    try:
        response = requests.post(f"{API_URL}/chat", json=payload)
        if response.status_code == 200:
            st.session_state.chat_history = response.json()["chat_history"]
            st.session_state.products = response.json()["recommendations"]
            st.rerun()
        else:
            st.error("Failed to send message.")
    except:
        st.error("Could not connect to server")

# Products section
st.sidebar.subheader("🛍️ Available Products")
for product in st.session_state.products:
    with st.sidebar.expander(f"{product['name']} - ${product['price']}"):
        st.write(f"**Seller:** {product['supplier']}")
        st.write(f"**Category:** {product['category']}")
        st.write(f"**Available:** {product['quantity']} units")
        if st.button("Buy This Product", key=f"buy_{product['id']}"):
            # Handle purchase logic here
            st.success(f"Purchase request sent for {product['name']}!")

# Clear chat button
if st.sidebar.button("🗑️ Clear Chat History"):
    try:
        response = requests.delete(f"{API_URL}/chat/clear")
        if response.status_code == 200:
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
            st.rerun()
    except:
        st.error("Could not connect to server")