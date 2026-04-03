# व्यापारी बजार / Vendor Marketplace

A full-stack vendor-to-vendor marketplace where vendors chat, negotiate prices, place orders, and make payments — all in one system. Bilingual: **English + नेपाली**.

No LLM or API key required.

## How It Works

1. **Vendor A** lists a product through chat: `I have 50kg rice at Rs.85`
2. System **auto-detects** product, price, quantity and lists it in the marketplace
3. **Vendor B** sees the listing, makes an offer: `Can you do Rs.75?`
4. They **negotiate** back and forth (offer → counter → accept/reject)
5. Once agreed, Vendor B **places an order** with delivery address and payment method
6. **Half payment** via eSewa/Khalti → Seller **ships** → **Delivery** → **Remaining payment**
7. Order marked **completed**

## Features

- **Chat-based product listing** — type naturally, system detects products and prices
- **Bilingual UI** — English + नेपाली everywhere (buttons, labels, status, product names)
- **Negotiation system** — offer → counter → accept/reject flow
- **Order management** — confirmed → half paid → shipped → delivered → completed
- **Payment methods** — eSewa, Khalti, IME Pay, Bank Transfer, Cash on Delivery
- **Market price catalog** — 30+ Nepali market products with wholesale rates
- **Price comparison** — compare any price against बजार भाउ (market rate)
- **Nepali language detection** — understands चामल, दाल, सिमेन्ट, रु.८५, ५० केजी etc.

## Tech Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Frontend:** Streamlit
- **Product Detection:** Rule-based keyword + regex (no LLM)
- **Migrations:** Alembic

## Project Structure

```
vendor_chat_app/
├── app/
│   ├── main.py                    # FastAPI app factory
│   ├── core/
│   │   ├── config.py              # Pydantic Settings (.env)
│   │   ├── database.py            # SQLAlchemy engine & session
│   │   └── logging.py             # Logging setup
│   ├── models/
│   │   ├── chat.py                # Chat messages
│   │   ├── product.py             # Product listings
│   │   ├── negotiation.py         # Price negotiations
│   │   ├── order.py               # Orders with payment tracking
│   │   └── transaction.py         # Legacy transactions
│   ├── schemas/
│   │   ├── chat.py                # Chat request/response
│   │   ├── product.py             # Product schemas
│   │   ├── negotiation.py         # Negotiation schemas
│   │   ├── order.py               # Order + payment schemas
│   │   ├── market.py              # Market price schemas
│   │   └── transaction.py         # Transaction schemas
│   ├── crud/
│   │   ├── chat.py                # Chat DB operations
│   │   ├── product.py             # Product CRUD
│   │   ├── negotiation.py         # Negotiation CRUD
│   │   ├── order.py               # Order + payment CRUD
│   │   └── transaction.py         # Transaction CRUD
│   ├── services/
│   │   └── product_engine.py      # Product extraction + market intelligence
│   └── api/v1/
│       ├── router.py              # Aggregates all routes
│       ├── chat.py                # Chat endpoints
│       ├── products.py            # Product endpoints
│       ├── negotiations.py        # Negotiation endpoints
│       ├── orders.py              # Order + payment endpoints
│       ├── market.py              # Market price endpoints
│       └── transactions.py        # Legacy transaction endpoints
├── frontend/
│   └── app.py                     # Streamlit UI (bilingual)
├── alembic/                       # Database migrations
├── pyproject.toml
├── requirements.txt
└── .env
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file:

```env
DATABASE_URL=sqlite:///./vendor_chat.db
```

### 3. Run

```bash
# Terminal 1: Backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
streamlit run frontend/app.py
```

API: `http://localhost:8000` | UI: `http://localhost:8501` | Docs: `http://localhost:8000/docs`

## API Endpoints

All prefixed with `/api/v1`.

### Chat / च्याट
| Method   | Endpoint              | Description                                    |
|----------|-----------------------|------------------------------------------------|
| `POST`   | `/chat`               | Send message (auto-detects products)           |
| `GET`    | `/chat/history`       | Get chat history                               |
| `DELETE` | `/chat/clear`         | Clear chat history                             |

### Products / सामान
| Method   | Endpoint              | Description                                    |
|----------|-----------------------|------------------------------------------------|
| `GET`    | `/products`           | List available products                        |
| `GET`    | `/products/{category}`| Filter by category                             |
| `POST`   | `/products`           | Create a product                               |

### Negotiations / मोलमोलाई
| Method   | Endpoint                          | Description                          |
|----------|-----------------------------------|--------------------------------------|
| `POST`   | `/negotiations`                   | Start negotiation (buyer makes offer)|
| `POST`   | `/negotiations/{id}/counter`      | Seller counters with different price |
| `POST`   | `/negotiations/{id}/accept`       | Accept the deal                      |
| `POST`   | `/negotiations/{id}/reject`       | Reject the deal                      |
| `GET`    | `/negotiations/user/{username}`   | Get user's active negotiations       |
| `GET`    | `/negotiations/product/{id}`      | Get negotiations for a product       |

### Orders / अर्डर
| Method   | Endpoint                    | Description                              |
|----------|-----------------------------|------------------------------------------|
| `POST`   | `/orders`                   | Place order (with address + payment)     |
| `POST`   | `/orders/{id}/pay`          | Make payment (half or full)              |
| `POST`   | `/orders/{id}/ship`         | Seller marks as shipped                  |
| `POST`   | `/orders/{id}/deliver`      | Mark as delivered                        |
| `GET`    | `/orders/user/{username}`   | Get user's orders                        |
| `GET`    | `/orders/payment-methods`   | List payment methods                     |

### Market Prices / बजार भाउ
| Method   | Endpoint              | Description                                    |
|----------|-----------------------|------------------------------------------------|
| `GET`    | `/market`             | Get all market prices                          |
| `GET`    | `/market/search?q=`   | Search (English or Nepali)                     |
| `GET`    | `/market/{product}`   | Get price for specific product                 |
| `POST`   | `/market/compare`     | Compare offered price vs market rate           |

## Example Flow

```
Vendor A (chat):  "I have 50 kg rice available at Rs 85 per kg"
                   → System lists rice, shows market comparison

Vendor B (chat):  "Rs 85 is expensive"
Vendor B (products tab): Makes offer at Rs.75 → "रु.७५ मा दिनुस् न"

Vendor A (deals tab): Counters at Rs.80 → "Last price Rs 80"

Vendor B (deals tab): Accepts → fills delivery form:
                      Address: Kathmandu, Balaju Ward 16
                      Phone: 9841234567
                      Payment: eSewa

Vendor B (orders tab): Pays half (Rs.2000) via eSewa
Vendor A (orders tab): Ships → Marks delivered
Vendor B (orders tab): Pays remaining (Rs.2000)
                       → Order completed ✅
```

## Supported Products (Market Catalog)

| Category / वर्ग      | Products / सामान                                          |
|-----------------------|-----------------------------------------------------------|
| Grocery / किराना      | Rice (चामल), Lentils (दाल), Oil (तेल), Sugar (चिनी), Salt (नुन), Flour (पीठो), Ghee (घिउ) |
| Vegetables / तरकारी   | Potato (आलु), Onion (प्याज), Tomato (गोलभेडा), Garlic (लसुन), Ginger (अदुवा) |
| Meat & Dairy          | Chicken (कुखुरा), Meat (मासु), Fish (माछा), Egg (अण्डा), Milk (दूध), Yogurt (दही) |
| Construction / निर्माण | Cement (सिमेन्ट), Rod (छड), Brick (इँटा), Sand (बालुवा) |
| Electronics           | Phone (फोन), Mobile (मोबाइल), Laptop (ल्यापटप) |
| Clothing / कपडा       | Cloth (कपडा), Shoes (जुत्ता), Sandals (चप्पल) |

## Payment Methods

| Method | Description |
|--------|-------------|
| 📱 eSewa | eSewa Mobile Wallet (इसेवा) |
| 💜 Khalti | Khalti Digital Wallet (खल्ती) |
| 💚 IME Pay | IME Pay (आईएमई पे) |
| 🏦 Bank Transfer | Bank Transfer (बैंक ट्रान्सफर) |
| 💵 Cash on Delivery | Cash on Delivery (क्यास अन डेलिभरी) |
