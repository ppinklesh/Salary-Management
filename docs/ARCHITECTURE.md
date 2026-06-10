# Architecture Document

## System Overview

The application follows a standard three-tier architecture: a React-based frontend communicates with a Python API backend, which persists data in a SQLite database.

```
┌─────────────────────┐
│   Browser (Client)  │
│   Next.js 15 + UI   │
└────────┬────────────┘
         │ HTTP/JSON (REST)
         ▼
┌─────────────────────┐
│   FastAPI Backend    │
│   Python 3.12+      │
└────────┬────────────┘
         │ SQLAlchemy ORM
         ▼
┌─────────────────────┐
│      SQLite DB      │
│   (salary_mgmt.db)  │
└─────────────────────┘
```

## Backend Layered Architecture

The backend follows a strict layered architecture where each layer has a single responsibility:

```
HTTP Request
    │
    ▼
┌──────────────────────────────┐
│  API Endpoints (Thin Layer)  │  ← Parse request, call service, return response
│  app/api/v1/endpoints/       │     No business logic here
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  Service Layer               │  ← Business logic, validation, orchestration
│  app/services/               │     Testable without HTTP context
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  Repository Layer            │  ← Database access, raw queries
│  app/repositories/           │     Single responsibility: CRUD + aggregations
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  Models + Schemas            │  ← SQLAlchemy ORM models (DB shape)
│  app/models/ + app/schemas/  │     Pydantic schemas (API shape)
└──────────────────────────────┘
```

**Why this separation:**
- Endpoints can be tested with a TestClient without needing real business logic
- Services can be tested by mocking the repository — no database required
- Repositories can be tested against a real in-memory SQLite — fast and deterministic
- Swapping the database (e.g., SQLite → PostgreSQL) only affects the repository layer

## Technology Choices

### Backend: FastAPI + Python

| Factor | Reasoning |
|--------|-----------|
| **Auto-generated API docs** | Swagger/OpenAPI docs at `/docs` — zero effort, great for reviewers |
| **Pydantic integration** | Request/response validation built-in; shared type system with SQLAlchemy |
| **Modern Python** | Type hints, dataclasses, async support — clean, readable code |
| **Industry standard** | Most popular Python API framework; large ecosystem and community |
| **Testing** | `TestClient` makes integration tests trivial |

### Database: SQLite

| Factor | Reasoning |
|--------|-----------|
| **Zero configuration** | No database server to install or configure |
| **Portable** | Single file — reviewers can clone and run immediately |
| **Sufficient scale** | 10,000 rows is well within SQLite's sweet spot (handles millions) |
| **Fast** | In-process database; no network round-trips |
| **Easy testing** | In-memory SQLite for tests — fast and isolated |

For a production system with concurrent writes, PostgreSQL would be the right choice. For this assessment's requirements (single-user, 10k rows, easy reviewer setup), SQLite is the pragmatic choice.

### ORM: SQLAlchemy 2.x

| Factor | Reasoning |
|--------|-----------|
| **Type-safe** | `Mapped[]` annotations provide IDE support and type checking |
| **Mature** | Industry standard Python ORM with 15+ years of production use |
| **Raw SQL escape hatch** | Can drop to raw SQL for complex aggregation queries |
| **Migration support** | Alembic integration for schema evolution (not used here for simplicity) |

### Frontend: Next.js 15 + shadcn/ui

| Factor | Reasoning |
|--------|-----------|
| **App Router** | Server components by default — fast initial loads |
| **TypeScript** | Type safety across the frontend codebase |
| **shadcn/ui** | Copy-paste component model — full code ownership, no dependency lock-in |
| **Tailwind CSS** | Utility-first styling — fast development, tiny bundles |
| **TanStack Table** | Headless table library — handles 10k+ rows with server-side pagination |
| **Recharts** | Composable charts that integrate well with shadcn/ui theming |

## Data Model

The data model separates **Employee** (identity & work info) from **Salary** (compensation data). This enables salary history tracking and follows proper normalization — salary is a first-class entity in a salary management tool, not just a column.

### Employee Entity

```
employees
├── id              INTEGER   PRIMARY KEY, AUTO INCREMENT
├── full_name       VARCHAR   NOT NULL, INDEXED (search)
├── email           VARCHAR   NOT NULL, UNIQUE
├── job_title       VARCHAR   NOT NULL, INDEXED (filter + insights)
├── department      VARCHAR   NOT NULL, INDEXED (filter + insights)
├── country         VARCHAR   NOT NULL, INDEXED (filter + insights)
├── hire_date       DATE      NOT NULL
├── exit_date       DATE      NULL (NULL = active employee)
├── exit_reason     VARCHAR   NULL (terminated, resigned, retired, layoff, end_of_contract, other)
├── created_at      DATETIME  DEFAULT NOW
└── updated_at      DATETIME  ON UPDATE NOW
```

### Salary Entity

```
salaries
├── id              INTEGER   PRIMARY KEY, AUTO INCREMENT
├── employee_id     INTEGER   NOT NULL, FK → employees.id, INDEXED
├── amount          NUMERIC   NOT NULL (12,2 precision)
├── currency        VARCHAR   NOT NULL (ISO 4217, e.g., USD, EUR, INR)
├── employment_type VARCHAR   NOT NULL (full_time, part_time, contract)
├── effective_date  DATE      NOT NULL, INDEXED
└── created_at      DATETIME  DEFAULT NOW
```

**Relationship:** One Employee → Many Salaries. The "current salary" is the record with the latest `effective_date`. When a salary update occurs, a new record is inserted rather than updating in place — this preserves salary history.

**Employment lifecycle:** Employees are never hard-deleted. Offboarding sets `exit_date` and `exit_reason`. Active employees have `exit_date IS NULL`. Salary insights and default list views include active employees only.

**Index strategy:** Indexes on `full_name`, `job_title`, `department`, and `country` support the primary query patterns (search, filter, aggregation). Indexes on `employee_id` and `effective_date` in the salaries table support efficient latest-salary lookups.

## API Design

RESTful API versioned under `/api/v1/`:

### Employee CRUD
- `GET    /api/v1/employees`                    — List with pagination, search, filter, status
- `GET    /api/v1/employees/{id}`               — Get single employee
- `POST   /api/v1/employees`                    — Create employee
- `PUT    /api/v1/employees/{id}`               — Update active employee
- `POST   /api/v1/employees/{id}/offboard`      — Offboard employee (soft exit)
- `POST   /api/v1/employees/{id}/rehire`        — Rehire offboarded employee

### Salary Insights
- `GET /api/v1/insights/summary`        — Global min/max/avg/median + headcount
- `GET /api/v1/insights/by-country`     — Salary stats per country
- `GET /api/v1/insights/by-job-title`   — Avg salary per job title (optional country filter)
- `GET /api/v1/insights/by-department`  — Salary stats per department

All list responses use a consistent envelope:
```json
{
  "data": [...],
  "total": 10000,
  "page": 1,
  "page_size": 20,
  "total_pages": 500
}
```

## Folder Structure

```
asignment/
├── docs/                        # All documentation artifacts
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app creation + middleware
│   │   ├── config.py            # Pydantic Settings
│   │   ├── database.py          # Engine, session, Base
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic request/response
│   │   ├── api/v1/endpoints/    # Route handlers (thin)
│   │   ├── services/            # Business logic
│   │   └── repositories/        # Database access
│   ├── tests/                   # pytest test suite
│   ├── seed/                    # Seed script + name files
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router pages
│   │   ├── components/          # UI components (shadcn + custom)
│   │   └── lib/                 # API client, utilities
│   └── package.json
├── docker-compose.yml           # One-command startup
└── README.md                    # Getting started guide
```
