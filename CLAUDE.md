# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sales & Store Analytics Dashboard — a full-stack analytics app with a React/Vite frontend and FastAPI Python backend. Provides sales metrics visualization and active store analytics with multi-dimensional filtering.

## Tech Stack

- **Frontend:** React 19, Vite 7, Recharts, MUI 7, axios, react-router-dom, date-fns
- **Backend:** Python 3.9+, FastAPI, SQLAlchemy, SQLite (dev) / PostgreSQL (prod-ready), pandas, uvicorn
- **Database:** 4 tables — Region, Store, Product, Sale (see `server/app/models/models.py`)

## Commands

### Backend
```bash
cd server
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000   # dev server (auto-creates tables)
```

### Frontend
```bash
cd client
npm install
npm run dev       # dev server on http://localhost:5173
npm run build     # production build to client/dist/
npm run lint      # ESLint
npm run preview   # preview production build
```

## Architecture

### Backend (`server/app/`)
Layered: **Models** (SQLAlchemy ORM) → **Schemas** (Pydantic validation) → **Endpoints** (route handlers) → **Services** (business logic).

- `main.py` — FastAPI app init, CORS (allows all origins), table creation on startup
- `core/database.py` — SQLAlchemy engine & session setup
- `models/models.py` — ORM models with FK relationships
- `schemas/schemas.py` — Pydantic request/response schemas
- `api/endpoints.py` — All route handlers (many are stubs returning empty data)
- `api/router.py` — Router orchestration under `/api` prefix
- `services/upload.py` — CSV/XLSX upload processing with pandas; validates required columns and upserts in dependency order (Region → Store → Product → Sale)

### Frontend (`client/src/`)
- `App.jsx` — Router: `/` (Upload), `/sales` (SalesDashboard), `/stores` (StoresDashboard)
- `context/GlobalState.jsx` — Context API for shared filter state (dateRange, brand, category, region); fetches filter options from backend on mount
- `components/layout/` — Layout shell with sidebar navigation and FilterBar
- `components/dashboard/` — Reusable chart/KPI components (KPICard, ChartCard, SectionCard, trend/region/brand charts)
- `pages/` — SalesDashboard, StoresDashboard, UploadPage
- `services/` — Empty, prepared for API utility layer

### API Endpoints (all under `/api`)
- `POST /api/data/upload` — CSV/XLSX file upload
- `GET /api/sales/{total,yoy,by-region,by-category,top-products,trend}` — Sales metrics with query param filters
- `GET /api/stores/active/{,yoy,by-region,trend}` — Active store metrics
- `GET /api/filters/{brands,categories,regions,date-range}` — Filter option lists

## Key Details

- Upload expects columns: Product Name, Brand, Category, Region, Store ID, Date, Quantity, Value
- Frontend hardcodes API base URL to `http://localhost:5000` — should be updated to match backend port or use env vars
- CSS custom properties in `client/src/index.css` define the design system (Magenta #ba0d59, Dark Navy #1d2b36)
- DB sessions use FastAPI dependency injection via `Depends(get_db)`
- Specs documents: `REQUIREMENT.md` (functional specs), `UI_SPECS.md` (design/layout specs)
