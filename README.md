# Employee Salary Management Tool

A full-stack web application for managing employee salary data across a 10,000-person organization. Built for the HR Manager persona to replace Excel-based workflows.

## Quick Start

### Option 1: Docker Compose (recommended)

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Local Development

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -e ".[dev]"
python -m seed.seed             # Seed 10,000 employees
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
cp .env.example .env.local      # Configure API URL
npm run dev
```

### Run Tests

```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2.x, SQLite |
| Frontend | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui |
| Charts | Recharts |
| Data Table | TanStack Table (server-side pagination) |
| Testing | pytest (43 tests, <1s) |

## Features

- **Employee CRUD**: Add, view, edit, offboard, and rehire employees with validation
- **Salary Dashboard**: KPI cards, bar charts by country/department/job title
- **Search & Filter**: Name search with debounce, country/department/title filters
- **Pagination**: Server-side pagination for 10,000 records
- **Seed Script**: High-performance bulk insert (10k records in ~0.15s)

## Project Structure

```
asignment/
├── docs/                  # Requirements, architecture, trade-offs, AI usage
├── backend/               # FastAPI + SQLite
│   ├── app/               # Application code (layered architecture)
│   ├── tests/             # pytest test suite
│   └── seed/              # 10k employee seed script
├── frontend/              # Next.js + shadcn/ui
│   └── src/               # App Router pages and components
├── docker-compose.yml     # One-command startup
└── README.md              # This file
```

## Documentation

- [Requirements](docs/REQUIREMENTS.md) — Scope, features, and deliberate exclusions
- [Architecture](docs/ARCHITECTURE.md) — System design and technology choices
- [Planning](docs/PLANNING.md) — Development phases and design decisions
- [Trade-offs](docs/TRADE_OFFS.md) — Key decisions with alternatives considered
- [Performance](docs/PERFORMANCE.md) — Optimization strategies
- [AI Usage](docs/AI_USAGE.md) — How AI tools were used in development
