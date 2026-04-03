import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="व्यापारी बजार / Vendor Marketplace", layout="wide")

# --- Session state ---
defaults = {
    "chat_history": [],
    "products": [],
    "negotiations": [],
    "orders": [],
    "last_update": datetime.now(),
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# --- Nepali product name lookup ---
PRODUCT_NEPALI = {
    "rice": "चामल", "lentils": "दाल", "oil": "तेल", "sugar": "चिनी",
    "salt": "नुन", "flour": "पीठो", "maida": "मैदा", "chiura": "चिउरा",
    "wheat": "गहुँ", "corn": "मकै", "ghee": "घिउ",
    "potato": "आलु", "onion": "प्याज", "tomato": "गोलभेडा",
    "garlic": "लसुन", "ginger": "अदुवा",
    "chicken": "कुखुरा", "meat": "मासु", "fish": "माछा", "egg": "अण्डा",
    "milk": "दूध", "yogurt": "दही",
    "cement": "सिमेन्ट", "rod": "छड", "brick": "इँटा", "sand": "बालुवा",
    "phone": "फोन", "mobile": "मोबाइल", "laptop": "ल्यापटप",
    "cloth": "कपडा", "shoes": "जुत्ता", "sandals": "चप्पल",
}

CATEGORY_NEPALI = {
    "grocery": "किराना", "vegetables": "तरकारी", "meat": "मासु",
    "dairy": "डेरी", "construction": "निर्माण", "electronics": "इलेक्ट्रोनिक्स",
    "clothing": "कपडा", "general": "सामान्य",
}

STATUS_LABEL = {
    "open": "🟡 खुला / Open",
    "countered": "🔵 काउन्टर भयो / Countered",
    "accepted": "🟢 स्वीकृत / Accepted",
    "rejected": "🔴 अस्वीकृत / Rejected",
}

ORDER_STATUS = {
    "confirmed": "📋 पुष्टि भयो / Confirmed",
    "half_paid": "💰 आधा तिरिसकेको / Half Paid",
    "shipped": "🚚 पठाइसकेको / Shipped",
    "delivered": "📦 डेलिभर भयो / Delivered",
    "completed": "✅ सम्पन्न / Completed",
}

PAY_STATUS = {
    "pending": "⏳ बाँकी / Pending",
    "half_paid": "💰 आधा तिरेको / Half Paid",
    "full_paid": "✅ पूरा तिरेको / Fully Paid",
}

PAY_METHODS = {
    "esewa": "📱 eSewa (इसेवा)",
    "khalti": "💜 Khalti (खल्ती)",
    "ime_pay": "💚 IME Pay (आईएमई पे)",
    "bank": "🏦 Bank Transfer (बैंक ट्रान्सफर)",
    "cash": "💵 Cash on Delivery (क्यास अन डेलिभरी)",
}


def np_name(name):
    """Get bilingual product name."""
    n = PRODUCT_NEPALI.get(name.lower())
    return f"{name} ({n})" if n else name


def np_cat(cat):
    """Get bilingual category name."""
    n = CATEGORY_NEPALI.get(cat.lower())
    return f"{cat} / {n}" if n else cat


def api_get(path, params=None):
    try:
        return requests.get(f"{API_URL}{path}", params=params, timeout=5)
    except requests.ConnectionError:
        return None


def api_post(path, json=None, params=None):
    try:
        return requests.post(f"{API_URL}{path}", json=json, params=params, timeout=5)
    except requests.ConnectionError:
        return None


def api_delete(path):
    try:
        return requests.delete(f"{API_URL}{path}", timeout=5)
    except requests.ConnectionError:
        return None


def refresh_all():
    r = api_get("/chat/history")
    if r and r.status_code == 200:
        st.session_state.chat_history = r.json()
    r = api_get("/products")
    if r and r.status_code == 200:
        st.session_state.products = r.json()
    r = api_get(f"/negotiations/user/{sender}")
    if r and r.status_code == 200:
        st.session_state.negotiations = r.json()
    r = api_get(f"/orders/user/{sender}")
    if r and r.status_code == 200:
        st.session_state.orders = r.json()
    st.session_state.last_update = datetime.now()


# ===================== SIDEBAR =====================
st.sidebar.title("व्यापारी / Vendor")

VENDORS = {"व्यापारी क / Vendor A": "VendorA", "व्यापारी ख / Vendor B": "VendorB"}
vendor_label = st.sidebar.selectbox("भूमिका छान्नुहोस् / Select Role", list(VENDORS.keys()))
sender = VENDORS[vendor_label]

c1, c2 = st.sidebar.columns(2)
if c1.button("🔄 रिफ्रेस / Refresh"):
    refresh_all()
    st.rerun()
if c2.button("🗑️ मेटाउ / Clear"):
    api_delete("/chat/clear")
    st.session_state.chat_history = []
    st.rerun()

# Auto-refresh
if (datetime.now() - st.session_state.last_update).seconds > 5:
    refresh_all()

# ===================== MAIN =====================
st.title("व्यापारी बजार / Vendor Marketplace")

tab_chat, tab_products, tab_deals, tab_orders, tab_market = st.tabs([
    "💬 च्याट / Chat",
    "📦 सामान / Products",
    "🤝 सौदा / Deals",
    "📋 अर्डर / Orders",
    "📊 बजार भाउ / Market",
])


# ===================== TAB 1: CHAT =====================
with tab_chat:
    st.caption("सन्देशमा सामान र मूल्य लेख्नुहोस् — अटो डिटेक्ट हुन्छ / Type products & prices in chat — auto detected")

    chat_box = st.container(height=400)
    with chat_box:
        for msg in st.session_state.chat_history:
            ts = datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M")
            is_me = msg["sender"] == sender
            if is_me:
                st.markdown(
                    f"<div style='text-align:right;background:#dcf8c6;padding:8px 14px;"
                    f"border-radius:14px 14px 0 14px;margin:4px 0;display:inline-block;"
                    f"float:right;clear:both;max-width:75%'>"
                    f"<small>तपाईं / You • {ts}</small><br>{msg['message']}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div style='text-align:left;background:#f0f0f0;padding:8px 14px;"
                    f"border-radius:14px 14px 14px 0;margin:4px 0;display:inline-block;"
                    f"float:left;clear:both;max-width:75%'>"
                    f"<small><b>{msg['sender']}</b> • {ts}</small><br>{msg['message']}</div>",
                    unsafe_allow_html=True,
                )

    with st.form("chat_form", clear_on_submit=True):
        col_msg, col_btn = st.columns([5, 1])
        message = col_msg.text_input(
            "सन्देश / Message",
            placeholder="जस्तै: मसँग ५० केजी चामल छ रु.८५ / e.g. I have 50kg rice at Rs.85",
            label_visibility="collapsed",
            key="msg_input",
        )
        submitted = col_btn.form_submit_button("पठाउ / Send")

    if submitted and message:
        r = api_post("/chat", json={"sender": sender, "message": message})
        if r and r.status_code == 200:
            data = r.json()
            st.session_state.chat_history = data["chat_history"]
            st.session_state.products = data["recommendations"]
            if data.get("response"):
                st.info(data["response"])
            st.rerun()


# ===================== TAB 2: PRODUCTS =====================
with tab_products:
    if not st.session_state.products:
        st.info("अहिलेसम्म कुनै सामान छैन — च्याटमा सामान लिस्ट गर्नुहोस्!\n\nNo products yet — list them via chat!")
    else:
        for p in st.session_state.products:
            with st.container(border=True):
                col_info, col_action = st.columns([3, 2])
                with col_info:
                    st.markdown(f"### {np_name(p['name'])}")
                    st.markdown(
                        f"💰 **रु.{p['price']}** प्रति एकाइ / per unit\n\n"
                        f"📦 **{p['quantity']}** उपलब्ध / available"
                    )
                    st.caption(
                        f"विक्रेता / Seller: {p['supplier']} | "
                        f"वर्ग / Category: {np_cat(p['category'])}"
                    )

                with col_action:
                    if p["supplier"] != sender:
                        with st.form(f"nego_{p['id']}"):
                            st.markdown("**मोलमोलाई गर्नुहोस् / Make Offer**")
                            offer = st.number_input(
                                "प्रस्तावित मूल्य (रु.) / Offer Price (Rs.)",
                                min_value=0.0,
                                value=float(p["price"]),
                                step=1.0,
                                key=f"offer_{p['id']}",
                            )
                            msg = st.text_input(
                                "सन्देश / Message",
                                placeholder="रु.८० मा दिनुस् न / Can you do Rs.80?",
                                key=f"nego_msg_{p['id']}",
                            )
                            if st.form_submit_button("🤝 अफर पठाउ / Send Offer"):
                                r = api_post("/negotiations", json={
                                    "product_id": p["id"],
                                    "buyer": sender,
                                    "offered_price": offer,
                                    "message": msg or None,
                                })
                                if r and r.status_code == 200:
                                    st.success(f"अफर पठाइयो! / Offer sent! रु.{offer}")
                                    st.rerun()
                                else:
                                    st.error("अफर पठाउन सकिएन / Failed to send offer")
                    else:
                        st.caption("📌 तपाईंको सामान हो / This is your listing")


# ===================== TAB 3: DEALS =====================
with tab_deals:
    r = api_get(f"/negotiations/user/{sender}")
    negos = r.json() if r and r.status_code == 200 else []

    if not negos:
        st.info("कुनै सक्रिय सौदा छैन / No active deals")
    else:
        for n in negos:
            with st.container(border=True):
                st.markdown(f"### {STATUS_LABEL.get(n['status'], n['status'])} — सौदा / Deal #{n['id']}")
                st.markdown(
                    f"**विक्रेता / Seller:** {n['seller']} | **खरिदकर्ता / Buyer:** {n['buyer']}\n\n"
                    f"मूल मूल्य / Original: **रु.{n['original_price']}** → "
                    f"प्रस्ताव / Offered: **रु.{n['offered_price']}**"
                    + (f" → काउन्टर / Counter: **रु.{n['counter_price']}**" if n.get("counter_price") else "")
                    + (f" → ✅ **अन्तिम मूल्य / Final: रु.{n['final_price']}**" if n.get("final_price") else "")
                )
                if n.get("last_message"):
                    st.caption(f'💬 "{n["last_message"]}"')

                is_seller = n["seller"] == sender
                is_buyer = n["buyer"] == sender

                if n["status"] in ("open", "countered"):
                    cols = st.columns(3)

                    if is_seller:
                        with cols[0]:
                            with st.form(f"counter_{n['id']}"):
                                cp = st.number_input(
                                    "काउन्टर मूल्य (रु.) / Counter Price (Rs.)",
                                    min_value=0.0, step=1.0, key=f"cp_{n['id']}",
                                )
                                cmsg = st.text_input(
                                    "सन्देश / Message",
                                    placeholder="रु.११० मा दिन्छु / I can do Rs.110",
                                    key=f"cmsg_{n['id']}",
                                )
                                if st.form_submit_button("🔄 काउन्टर / Counter"):
                                    r = api_post(f"/negotiations/{n['id']}/counter", json={
                                        "counter_price": cp, "message": cmsg or None,
                                    })
                                    if r and r.status_code == 200:
                                        st.success("काउन्टर पठाइयो! / Counter sent!")
                                        st.rerun()
                        with cols[1]:
                            if st.button("✅ स्वीकार / Accept", key=f"acc_{n['id']}"):
                                api_post(f"/negotiations/{n['id']}/accept")
                                st.success("सौदा स्वीकार भयो! / Deal accepted!")
                                st.rerun()
                        with cols[2]:
                            if st.button("❌ अस्वीकार / Reject", key=f"rej_{n['id']}"):
                                api_post(f"/negotiations/{n['id']}/reject")
                                st.rerun()

                    if is_buyer and n["status"] == "countered":
                        with cols[1]:
                            if st.button("✅ स्वीकार / Accept", key=f"bacc_{n['id']}"):
                                api_post(f"/negotiations/{n['id']}/accept")
                                st.success("सौदा स्वीकार भयो! / Deal accepted!")
                                st.rerun()
                        with cols[2]:
                            if st.button("❌ अस्वीकार / Reject", key=f"brej_{n['id']}"):
                                api_post(f"/negotiations/{n['id']}/reject")
                                st.rerun()

                # Accepted → buyer places order
                if n["status"] == "accepted" and is_buyer:
                    st.success(f"🎉 सौदा मिल्यो रु.{n['final_price']} मा! / Deal agreed at Rs.{n['final_price']}!")
                    with st.form(f"order_{n['id']}"):
                        st.markdown("**अर्डर दिनुहोस् / Place Order**")
                        qty = st.number_input("मात्रा / Quantity", min_value=1, value=1, key=f"oqty_{n['id']}")
                        addr = st.text_input(
                            "डेलिभरी ठेगाना / Delivery Address",
                            placeholder="काठमाडौं, वडा नं. १० / Kathmandu, Ward 10",
                            key=f"oaddr_{n['id']}",
                        )
                        phone = st.text_input(
                            "फोन नम्बर / Phone",
                            placeholder="98XXXXXXXX",
                            key=f"ophone_{n['id']}",
                        )
                        note = st.text_input(
                            "नोट (ऐच्छिक) / Note (optional)",
                            placeholder="बिहान डेलिभर गर्नुस् / Deliver in the morning",
                            key=f"onote_{n['id']}",
                        )
                        pay_method = st.selectbox(
                            "भुक्तानी विधि / Payment Method",
                            list(PAY_METHODS.keys()),
                            format_func=lambda x: PAY_METHODS[x],
                            key=f"opay_{n['id']}",
                        )
                        st.caption("⚡ आधा पैसा अहिले, बाँकी डेलिभरी पछि / Half payment now, rest after delivery")

                        if st.form_submit_button("📋 अर्डर दिनुहोस् / Place Order"):
                            if not addr or not phone:
                                st.error("ठेगाना र फोन आवश्यक छ / Address and phone required")
                            else:
                                r = api_post(
                                    f"/orders?buyer={sender}",
                                    json={
                                        "product_id": n["product_id"],
                                        "negotiation_id": n["id"],
                                        "quantity": qty,
                                        "delivery_address": addr,
                                        "delivery_phone": phone,
                                        "delivery_note": note or None,
                                        "payment_method": pay_method,
                                    },
                                )
                                if r and r.status_code == 200:
                                    order = r.json()
                                    st.success(
                                        f"✅ अर्डर #{order['id']} दिइयो! जम्मा रु.{order['total_price']}\n\n"
                                        f"Order #{order['id']} placed! Total Rs.{order['total_price']}"
                                    )
                                    st.rerun()
                                else:
                                    detail = r.json().get("detail", "अर्डर दिन सकिएन") if r else "सर्भर त्रुटि"
                                    st.error(detail)


# ===================== TAB 4: ORDERS =====================
with tab_orders:
    r = api_get(f"/orders/user/{sender}")
    orders = r.json() if r and r.status_code == 200 else []

    if not orders:
        st.info("अहिलेसम्म कुनै अर्डर छैन / No orders yet")
    else:
        for o in orders:
            with st.container(border=True):
                st.markdown(f"### अर्डर / Order #{o['id']} — {np_name(o['product_name'])}")

                c1, c2, c3 = st.columns(3)
                c1.metric("जम्मा / Total", f"रु.{o['total_price']}")
                c2.metric("तिरेको / Paid", f"रु.{o['amount_paid']}")
                remaining = o["total_price"] - o["amount_paid"]
                c3.metric("बाँकी / Remaining", f"रु.{remaining}")

                st.markdown(
                    f"**मात्रा / Qty:** {o['quantity']} x रु.{o['unit_price']} | "
                    f"**स्थिति / Status:** {ORDER_STATUS.get(o['status'], o['status'])} | "
                    f"**भुक्तानी / Payment:** {PAY_STATUS.get(o['payment_status'], o['payment_status'])} | "
                    f"**माध्यम / Via:** {PAY_METHODS.get(o['payment_method'], o['payment_method'])}"
                )
                st.caption(f"📍 ठेगाना / Address: {o.get('delivery_address', '-')} | 📞 फोन / Phone: {o.get('delivery_phone', '-')}")

                is_buyer = o["buyer"] == sender
                is_seller = o["seller"] == sender
                cols = st.columns(4)

                # Step 1: Buyer pays half
                if is_buyer and o["payment_status"] == "pending":
                    half = o["total_price"] / 2
                    with cols[0]:
                        if st.button(f"💰 आधा तिर्नुहोस् / Pay Half (रु.{half:.0f})", key=f"phalf_{o['id']}"):
                            r = api_post(f"/orders/{o['id']}/pay", json={"amount": half})
                            if r and r.status_code == 200:
                                st.success(
                                    f"रु.{half:.0f} तिरियो {PAY_METHODS.get(o['payment_method'])} बाट!\n\n"
                                    f"Rs.{half:.0f} paid via {PAY_METHODS.get(o['payment_method'])}!"
                                )
                                st.rerun()

                # Step 2: Seller ships after half payment
                if is_seller and o["status"] == "half_paid":
                    with cols[1]:
                        if st.button("🚚 सामान पठाउ / Ship Now", key=f"ship_{o['id']}"):
                            api_post(f"/orders/{o['id']}/ship")
                            st.success("सामान पठाइयो! / Marked as shipped!")
                            st.rerun()

                # Step 3: Seller marks delivered
                if is_seller and o["status"] == "shipped":
                    with cols[2]:
                        if st.button("📦 डेलिभर भयो / Delivered", key=f"dlvr_{o['id']}"):
                            api_post(f"/orders/{o['id']}/deliver")
                            st.success("डेलिभर भयो! / Marked as delivered!")
                            st.rerun()

                # Step 4: Buyer pays remaining after delivery
                if is_buyer and o["status"] == "delivered" and o["payment_status"] == "half_paid":
                    with cols[3]:
                        if st.button(f"💰 बाँकी तिर्नुहोस् / Pay Rest (रु.{remaining:.0f})", key=f"pfull_{o['id']}"):
                            r = api_post(f"/orders/{o['id']}/pay", json={"amount": remaining})
                            if r and r.status_code == 200:
                                st.success("✅ पूरा भुक्तानी भयो! अर्डर सम्पन्न!\n\nFully paid! Order completed!")
                                st.rerun()


# ===================== TAB 5: MARKET PRICES =====================
with tab_market:
    st.caption("नेपाली बजार भाउ हेर्नुहोस् / Browse Nepali market prices")
    search_q = st.text_input(
        "खोज्नुहोस् / Search",
        placeholder="चामल, rice, construction, निर्माण...",
        key="mkt_search",
    )
    try:
        if search_q:
            r = api_get("/market/search", params={"q": search_q})
        else:
            r = api_get("/market")
        if r and r.status_code == 200:
            data = r.json()
            if data:
                rows = []
                for item in data:
                    rows.append({
                        "सामान / Product": f"{item['product'].title()} ({item['name_np']})",
                        "वर्ग / Category": np_cat(item["category"]),
                        "एकाइ / Unit": item["unit"],
                        "बजार भाउ (रु.) / Market Price": f"रु.{item['market_price']}",
                        "दायरा (रु.) / Range": f"रु.{item['price_min']} - रु.{item['price_max']}",
                    })
                st.dataframe(rows, use_container_width=True, hide_index=True)
        elif r and r.status_code == 404:
            st.warning("केही भेटिएन / No results found")
    except Exception:
        st.error("बजार डाटा लोड हुन सकेन / Could not load market data")

    st.divider()
    st.subheader("⚖️ मूल्य तुलना / Price Compare")
    cc1, cc2 = st.columns(2)
    cmp_product = cc1.text_input("सामान / Product", placeholder="rice / चामल", key="cmp_p")
    cmp_price = cc2.number_input("तपाईंको मूल्य (रु.) / Your Price (Rs.)", min_value=0.0, step=1.0, key="cmp_pr")
    if st.button("⚖️ तुलना गर्नुहोस् / Compare"):
        if cmp_product and cmp_price > 0:
            r = api_post("/market/compare", json={"product": cmp_product, "price": cmp_price})
            if r and r.status_code == 200:
                d = r.json()
                m1, m2, m3 = st.columns(3)
                m1.metric("बजार भाउ / Market", f"रु.{d['market_price']}")
                m2.metric("तपाईंको / Yours", f"रु.{d['offered_price']}", f"{d['difference_pct']:+.1f}%")
                m3.metric("निर्णय / Verdict", d["verdict_np"])
                st.caption(f"दायरा / Range: रु.{d['price_min']} - रु.{d['price_max']} प्रति {d['unit']}")
            elif r:
                st.warning(r.json().get("detail", "भेटिएन / Not found"))
