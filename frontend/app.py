import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Vendor Chat / व्यापारी च्याट", layout="wide")

# --- Session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "products" not in st.session_state:
    st.session_state.products = []
if "last_update" not in st.session_state:
    st.session_state.last_update = datetime.now()
if "lang" not in st.session_state:
    st.session_state.lang = "en"

# --- Language ---
L = {
    "en": {
        "title": "Vendor-to-Vendor Marketplace",
        "chat": "Live Chat",
        "send_placeholder": "Type your message... (e.g., 'I have 50kg rice at Rs.85')",
        "user_info": "User Info",
        "vendor_role": "Select Your Vendor Role",
        "refresh": "Refresh",
        "clear": "Clear Chat",
        "products": "Listed Products",
        "market": "Market Prices",
        "search_market": "Search product (English/Nepali)",
        "compare": "Price Compare",
        "compare_btn": "Compare with Market",
        "no_products": "No products listed yet",
        "cleared": "Chat history cleared!",
        "buy": "Buy",
        "product_col": "Product",
        "nepali_col": "नेपालीमा",
        "category_col": "Category",
        "unit_col": "Unit",
        "price_col": "Market Price (Rs.)",
        "range_col": "Price Range (Rs.)",
    },
    "np": {
        "title": "व्यापारी-बजार प्रणाली",
        "chat": "लाइभ च्याट",
        "send_placeholder": "सन्देश टाइप गर्नुहोस्... (जस्तै: 'मसँग ५० केजी चामल छ रु.८५')",
        "user_info": "प्रयोगकर्ता जानकारी",
        "vendor_role": "आफ्नो भूमिका छान्नुहोस्",
        "refresh": "रिफ्रेस",
        "clear": "च्याट मेटाउनुहोस्",
        "products": "सूचीकृत उत्पादनहरू",
        "market": "बजार भाउ",
        "search_market": "उत्पादन खोज्नुहोस् (English/नेपाली)",
        "compare": "मूल्य तुलना",
        "compare_btn": "बजारसँग तुलना गर्नुहोस्",
        "no_products": "अहिलेसम्म कुनै उत्पादन छैन",
        "cleared": "च्याट इतिहास मेटाइयो!",
        "buy": "किन्नुहोस्",
        "product_col": "उत्पादन",
        "nepali_col": "नेपालीमा",
        "category_col": "वर्ग",
        "unit_col": "एकाइ",
        "price_col": "बजार भाउ (रु.)",
        "range_col": "मूल्य दायरा (रु.)",
    },
}


def t(key: str) -> str:
    return L[st.session_state.lang].get(key, key)


def refresh_chat():
    try:
        resp = requests.get(f"{API_URL}/chat/history", timeout=5)
        if resp.status_code == 200:
            st.session_state.chat_history = resp.json()
        resp = requests.get(f"{API_URL}/products", timeout=5)
        if resp.status_code == 200:
            st.session_state.products = resp.json()
        st.session_state.last_update = datetime.now()
    except requests.ConnectionError:
        st.error("Server not reachable / सर्भरमा जडान हुन सकेन")


# Auto-refresh
if (datetime.now() - st.session_state.last_update).seconds > 5:
    refresh_chat()

# --- Sidebar ---
st.sidebar.title(t("user_info"))

lang = st.sidebar.radio("Language / भाषा", ["English", "नेपाली"], horizontal=True)
st.session_state.lang = "np" if lang == "नेपाली" else "en"

sender = st.sidebar.selectbox(t("vendor_role"), ["Vendor A / व्यापारी क", "Vendor B / व्यापारी ख"])

col1, col2 = st.sidebar.columns(2)
if col1.button(t("refresh")):
    refresh_chat()
    st.rerun()
if col2.button(t("clear")):
    try:
        requests.delete(f"{API_URL}/chat/clear", timeout=5)
        st.session_state.chat_history = []
        st.session_state.products = []
        st.rerun()
    except requests.ConnectionError:
        st.error("Server not reachable")

# ===================== MAIN AREA =====================
st.title(t("title"))

tab_chat, tab_market, tab_compare = st.tabs([t("chat"), t("market"), t("compare")])

# --- TAB 1: Chat ---
with tab_chat:
    # Display chat
    chat_container = st.container(height=400)
    with chat_container:
        for msg in st.session_state.chat_history:
            ts = datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M:%S")
            is_me = msg["sender"] == sender
            if is_me:
                st.markdown(f"**You ({ts}):** {msg['message']}")
            else:
                st.markdown(f"**{msg['sender']} ({ts}):** {msg['message']}")

    # Message input — use a form so it clears after submit
    with st.form("chat_form", clear_on_submit=True):
        message = st.text_input(t("send_placeholder"), key="message_input")
        submitted = st.form_submit_button("Send / पठाउनुहोस्")

    if submitted and message:
        try:
            resp = requests.post(
                f"{API_URL}/chat",
                json={"sender": sender, "message": message},
                timeout=5,
            )
            if resp.status_code == 200:
                data = resp.json()
                st.session_state.chat_history = data["chat_history"]
                st.session_state.products = data["recommendations"]
                if data.get("response"):
                    st.info(data["response"])
                st.rerun()
        except requests.ConnectionError:
            st.error("Server not reachable / सर्भरमा जडान हुन सकेन")

    # Listed products
    st.subheader(t("products"))
    if st.session_state.products:
        for product in st.session_state.products:
            with st.expander(f"{product['name']} - Rs.{product['price']} ({product['supplier']}) [{product['quantity']} available]"):
                st.write(f"**{t('category_col')}:** {product['category']}")
                st.write(f"**Seller:** {product['supplier']}")
                st.write(f"**Price:** Rs.{product['price']} per unit")
                st.write(f"**Available:** {product['quantity']}")

                # Only show buy option if this product was NOT listed by current vendor
                if product["supplier"] != sender:
                    with st.form(f"buy_form_{product['id']}"):
                        qty = st.number_input(
                            "Quantity / मात्रा",
                            min_value=1,
                            max_value=product["quantity"],
                            value=1,
                            key=f"qty_{product['id']}",
                        )
                        buy_clicked = st.form_submit_button(f"{t('buy')} ({product['name']})")

                    if buy_clicked:
                        try:
                            resp = requests.post(
                                f"{API_URL}/transactions",
                                json={
                                    "buyer": sender,
                                    "seller": product["supplier"],
                                    "product_id": product["id"],
                                    "quantity": qty,
                                },
                                timeout=5,
                            )
                            if resp.status_code == 200:
                                txn = resp.json()
                                st.success(
                                    f"Purchased {txn['quantity']}x {product['name']} "
                                    f"for Rs.{txn['total_price']} from {product['supplier']}!"
                                )
                                refresh_chat()
                                st.rerun()
                            else:
                                detail = resp.json().get("detail", "Purchase failed")
                                st.error(detail)
                        except requests.ConnectionError:
                            st.error("Server not reachable")
                else:
                    st.caption("This is your listing / यो तपाईंको उत्पादन हो")
    else:
        st.caption(t("no_products"))


# --- TAB 2: Market Prices ---
with tab_market:
    st.subheader(t("market"))

    search_query = st.text_input(t("search_market"), key="market_search")

    try:
        if search_query:
            resp = requests.get(f"{API_URL}/market/search", params={"q": search_query}, timeout=5)
        else:
            resp = requests.get(f"{API_URL}/market", timeout=5)

        if resp.status_code == 200:
            data = resp.json()
            if data:
                # Build table
                rows = []
                for item in data:
                    rows.append({
                        t("product_col"): item["product"].title(),
                        t("nepali_col"): item["name_np"],
                        t("category_col"): item["category"],
                        t("unit_col"): item["unit"],
                        t("price_col"): f"Rs.{item['market_price']}",
                        t("range_col"): f"Rs.{item['price_min']} - Rs.{item['price_max']}",
                    })
                st.dataframe(rows, use_container_width=True, hide_index=True)
            else:
                st.info("No results")
        elif resp.status_code == 404:
            st.warning(resp.json().get("detail", "Not found"))
    except requests.ConnectionError:
        st.error("Server not reachable")


# --- TAB 3: Price Compare ---
with tab_compare:
    st.subheader(t("compare"))

    col_p, col_pr = st.columns(2)
    product_name = col_p.text_input("Product / उत्पादन", placeholder="e.g., rice / चामल")
    offered_price = col_pr.number_input("Your Price (Rs.) / तपाईंको मूल्य (रु.)", min_value=0.0, step=1.0)

    if st.button(t("compare_btn")):
        if product_name and offered_price > 0:
            try:
                resp = requests.post(
                    f"{API_URL}/market/compare",
                    json={"product": product_name, "price": offered_price},
                    timeout=5,
                )
                if resp.status_code == 200:
                    r = resp.json()
                    # Verdict color
                    if r["verdict"] == "fair_price":
                        color = "green"
                    elif r["verdict"] == "below_market":
                        color = "blue"
                    else:
                        color = "red"

                    st.markdown(f"### {r['product'].title()} ({r['name_np']})")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Market Price / बजार भाउ", f"Rs.{r['market_price']}")
                    c2.metric("Your Price / तपाईंको मूल्य", f"Rs.{r['offered_price']}", f"{r['difference_pct']:+.1f}%")
                    c3.metric("Verdict / निर्णय", r["verdict_np"])

                    st.markdown(f"**Range / दायरा:** Rs.{r['price_min']} - Rs.{r['price_max']} per {r['unit']}")
                elif resp.status_code == 404:
                    st.warning(resp.json().get("detail", "Product not found"))
            except requests.ConnectionError:
                st.error("Server not reachable")
        else:
            st.warning("Please enter product name and price / उत्पादन र मूल्य भर्नुहोस्")
