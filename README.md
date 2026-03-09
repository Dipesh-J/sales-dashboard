# Sales & Store Analytics Dashboard

A full-stack analytics dashboard for visualizing sales metrics and active store coverage. Built with React + Vite (frontend) and FastAPI + PostgreSQL (backend).

## Features

- **Sales Dashboard** — Total sales, YoY growth, top brand, sales trend over time, sales by brand/region with drill-down
- **Stores Dashboard** — Active store count, YoY change, store trend, stores by region with drill-down
- **Global Filters** — Date range, brand, category, region — applied across all charts
- **Data Upload** — Upload CSV/XLSX files to populate the database
- **Dark Mode** — Toggle with localStorage persistence
- **CSV Export** — Export dashboard data

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | React 19, Vite 7, Recharts, Material UI 7, Axios |
| Backend | Python 3.9+, FastAPI, SQLAlchemy, Alembic |
| Database | PostgreSQL (Supabase) |

## Project Structure

```
sales-dashboard/
├── client/                  # React frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── context/         # Global state (filters, dark mode)
│   │   ├── pages/           # Dashboard & upload pages
│   │   └── services/        # Axios API instance
│   └── vercel.json          # Vercel SPA config
├── server/                  # FastAPI backend
│   ├── app/
│   │   ├── api/             # Route handlers & router
│   │   ├── core/            # Config, database setup
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic (upload)
│   ├── alembic/             # Database migrations
│   └── Procfile             # Production entrypoint
└── .env.example             # Environment variables reference
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL database (or use SQLite for local dev)

### Backend

```bash
cd server
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Create .env (see .env.example for reference)
cp ../.env.example .env
# Edit .env with your DATABASE_URL

# Run migrations
alembic upgrade head

# Start dev server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd client
npm install

# Create .env (see .env.example for reference)
echo "VITE_API_URL=http://localhost:8000" > .env

# Start dev server
npm run dev
```

Open http://localhost:5173 in your browser.

## Environment Variables

| Variable | Service | Description |
|----------|---------|-------------|
| `DATABASE_URL` | Backend | PostgreSQL connection string |
| `CORS_ORIGINS` | Backend | Comma-separated allowed origins (`*` for dev) |
| `DEBUG` | Backend | `true` for debug logging, `false` for production |
| `VITE_API_URL` | Frontend | Backend API base URL |

## Data Upload

The app expects CSV/XLSX files with these columns:

| Column | Example |
|--------|---------|
| Product Name | Widget Pro |
| Brand | Acme |
| Category | Electronics |
| Region | North |
| Store ID | 42 |
| Date | 2024-01-15 |
| Quantity | 10 |
| Value | 299.99 |

Upload via the Upload page (`/`) or `POST /api/data/upload`.

## Deployment

### Backend (Render)

1. Create a Web Service, set root directory to `server`
2. Build command: `pip install -r requirements.txt && alembic upgrade head`
3. Start command: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
4. Set env vars: `DATABASE_URL`, `CORS_ORIGINS` (your Vercel URL), `DEBUG=false`

### Frontend (Vercel)

1. Create a project, set root directory to `client`
2. Framework preset: Vite (auto-detected)
3. Set env var: `VITE_API_URL` (your Render backend URL)

## API Endpoints

All endpoints are under `/api`. Interactive docs available at `/docs` (Swagger UI).

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/data/upload` | Upload CSV/XLSX data |
| GET | `/api/sales/total` | Total sales value |
| GET | `/api/sales/yoy` | Year-over-year comparison |
| GET | `/api/sales/by-region` | Sales grouped by region |
| GET | `/api/sales/by-brand` | Sales grouped by brand |
| GET | `/api/sales/top-products` | Top N products by value |
| GET | `/api/sales/trend` | Sales trend over time |
| GET | `/api/stores/active` | Active store count |
| GET | `/api/stores/active/yoy` | YoY active store change |
| GET | `/api/stores/active/by-region` | Active stores by region |
| GET | `/api/stores/active/trend` | Active stores trend |
| GET | `/api/filters/{brands,categories,regions,date-range}` | Filter options |
