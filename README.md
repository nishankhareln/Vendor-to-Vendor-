# Vendor Chat App / व्यापारी च्याट

A vendor-to-vendor marketplace chat system with built-in market price intelligence. Supports **English and Nepali (नेपाली)**.

No LLM or API key required — uses rule-based keyword matching and a built-in market catalog.

## What It Does

Two vendors open the chat and start talking. When a vendor mentions a product with a price (e.g., "I have 50kg rice at Rs.85" or "मसँग ५० केजी चामल छ रु.८५"), the system:

1. **Auto-detects** the product, price, and quantity from the message
2. **Lists it** in the marketplace for the other vendor to see and buy
3. **Compares** the offered price against real market rates and shows if it's fair, cheap, or expensive

Vendors can also browse the full **market price catalog** and use the **price comparison tool** to check any product against current rates.

## Tech Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Frontend:** Streamlit (bilingual English/Nepali)
- **Product Detection:** Rule-based keyword + regex (no LLM needed)
- **Market Data:** Built-in catalog with 30+ Nepali market products and price ranges
- **Migrations:** Alembic

## Project Structure

```
vendor_chat_app/
├── app/
│   ├── main.py              # FastAPI app factory
│   ├── core/
│   │   ├── config.py        # Settings (loads from .env)
│   │   ├── database.py      # SQLAlchemy engine & session
│   │   └── logging.py       # Logging setup
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── crud/                # Database operations
│   ├── services/
│   │   └── llm.py           # Product extraction & market intelligence
│   └── api/v1/              # API routes (versioned)
│       ├── chat.py          # Chat endpoints
│       ├── products.py      # Product CRUD
│       ├── transactions.py  # Buy/sell transactions
│       └── market.py        # Market prices & comparison
├── frontend/
│   └── app.py               # Streamlit UI (English + Nepali)
├── alembic/                 # Database migrations
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

Create a `.env` file in the project root:

```env
DATABASE_URL=sqlite:///./vendor_chat.db
```

### 3. Run

```bash
# Start the API server
uvicorn app.main:app --reload

# In a separate terminal, start the frontend
streamlit run frontend/app.py
```

The API runs at `http://localhost:8000` and the UI at `http://localhost:8501`.

## API Endpoints

All endpoints are prefixed with `/api/v1`.

| Method   | Endpoint                 | Description                              |
|----------|--------------------------|------------------------------------------|
| `POST`   | `/api/v1/chat`           | Send a chat message                      |
| `GET`    | `/api/v1/chat/history`   | Get chat history                         |
| `DELETE` | `/api/v1/chat/clear`     | Clear chat history                       |
| `GET`    | `/api/v1/products`       | List available products                  |
| `GET`    | `/api/v1/products/{cat}` | Filter products by category              |
| `POST`   | `/api/v1/products`       | Create a product                         |
| `POST`   | `/api/v1/transactions`   | Create a transaction                     |
| `GET`    | `/api/v1/market`         | Get all market prices                    |
| `GET`    | `/api/v1/market/search`  | Search market catalog (English/Nepali)   |
| `GET`    | `/api/v1/market/{product}` | Get market price for a product         |
| `POST`   | `/api/v1/market/compare` | Compare offered price vs market rate     |

## Features

- Real-time vendor-to-vendor chat
- Bilingual support (English + Nepali / नेपाली)
- Auto-detect products from chat messages (name, price, quantity)
- Built-in market catalog with 30+ products (grocery, vegetables, meat, construction, electronics, clothing)
- Price comparison tool: see if a price is fair, cheap, or expensive vs market rate
- Product catalog with search and filtering
- Transaction system with quantity tracking
- No API keys or external services required
