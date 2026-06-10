# Trade-Off Explanations

Each decision below is documented with the alternatives considered and the reasoning for the choice made.

---

## 1. SQLite vs PostgreSQL

**Decision:** SQLite

**Alternatives:** PostgreSQL, MySQL

**Reasoning:**
- SQLite requires zero configuration — no database server to install or manage
- Reviewers can clone the repo and run immediately with `python -m uvicorn`
- 10,000 rows is well within SQLite's optimal range (it handles millions)
- Single-user application means no concurrent write contention
- In-memory SQLite makes tests extremely fast

**Consequences:**
- (+) Simplest possible setup for reviewers and deployment
- (+) No external dependencies — the database is a single file
- (-) Would not scale to concurrent multi-user writes in production
- (-) No advanced PostgreSQL features (full-text search, JSON operators, CTEs with LATERAL)

**When to switch:** If the tool grows to support multiple concurrent HR users, migrate to PostgreSQL.

---

## 2. Synchronous vs Asynchronous SQLAlchemy

**Decision:** Synchronous SQLAlchemy

**Alternatives:** Async SQLAlchemy with `aiosqlite`

**Reasoning:**
- SQLite is an in-process database — there are no network round-trips to benefit from async
- Sync code is simpler to read, debug, and test
- Async adds complexity (session management, connection pools) without measurable benefit for SQLite
- FastAPI supports sync route handlers seamlessly

**Consequences:**
- (+) Simpler codebase, fewer async pitfalls
- (+) Easier testing — no need for `pytest-asyncio` or async fixtures
- (-) If migrating to PostgreSQL later, would need to refactor to async

---

## 3. Server-Side vs Client-Side Pagination

**Decision:** Server-side pagination

**Alternatives:** Client-side pagination (load all 10k rows), virtual scrolling

**Reasoning:**
- 10,000 rows of employee data (~1-2MB JSON) is too large to send in a single response
- Server-side pagination keeps API responses small (~20 records, <10KB)
- URL-based pagination (`?page=5&page_size=20`) makes views bookmarkable and shareable
- Database `LIMIT/OFFSET` is efficient with proper indexes

**Consequences:**
- (+) Fast API responses regardless of dataset size
- (+) Low browser memory usage
- (+) Shareable URLs with pagination state
- (-) Each page change requires a network request
- (-) Server must handle pagination logic

**Alternative considered — Virtual scrolling:**
Would provide a smoother UX for browsing, but adds significant frontend complexity and still requires loading all data or implementing windowed fetching. Server-side pagination is the simpler, proven approach.

---

## 4. Layered Architecture vs Flat Structure

**Decision:** Three-layer architecture (endpoints → services → repositories)

**Alternatives:** Flat structure (endpoints directly query the database), two-layer (endpoints → repository)

**Reasoning:**
- Demonstrates clean code principles and separation of concerns
- Each layer is independently testable
- Services can be tested without HTTP context, repositories without business logic
- Makes the codebase navigable — a new developer knows exactly where to find business logic vs database queries
- Aligns with Incubyte's emphasis on software craftsmanship

**Consequences:**
- (+) Highly testable — mock any layer boundary
- (+) Clear responsibilities — easy to navigate and maintain
- (+) Swappable components — change database without touching business logic
- (-) More files and boilerplate than a flat approach
- (-) For a small app, may feel over-engineered — but the assessment values this pattern

---

## 5. shadcn/ui vs Material UI vs Ant Design

**Decision:** shadcn/ui

**Alternatives:** Material UI (MUI), Ant Design, Chakra UI

**Reasoning:**
- shadcn/ui copies components into the project — full code ownership, no version lock-in
- Built on Radix UI primitives — accessible out of the box
- Styled with Tailwind CSS — consistent with the rest of the frontend
- Lighter bundle size than MUI or Ant Design
- Modern industry standard for React dashboards in 2025-2026

**Consequences:**
- (+) Full control over every component — can customize without fighting the library
- (+) No dependency updates to manage — components are part of the codebase
- (+) Clean, professional look suitable for internal tools
- (-) Need to add each component individually (vs MUI's comprehensive install)
- (-) Less out-of-the-box than MUI for complex components like date pickers

---

## 6. Monorepo vs Separate Repositories

**Decision:** Monorepo in `assignment/` with `backend/` and `frontend/` subdirectories

**Alternatives:** Two separate repositories (one for backend, one for frontend)

**Reasoning:**
- Single repository is easier for reviewers to clone and evaluate
- Docker Compose can reference both services from one `docker-compose.yml`
- Shared documentation lives alongside the code
- The assessment asks to "commit your code to a Git repository" (singular)

**Consequences:**
- (+) One `git clone` to get everything
- (+) Single Docker Compose orchestrates both services
- (+) Documentation artifacts live alongside the code
- (-) Frontend and backend share git history (minor; clear commit scoping mitigates this)

---

## 7. No Authentication vs Simple Auth

**Decision:** No authentication

**Alternatives:** Basic auth, JWT tokens, session-based auth

**Reasoning:**
- The assessment describes a single-user tool for "the HR Manager"
- Authentication adds significant complexity (login page, token management, session handling, protected routes) without contributing to the core salary management features
- In production, this tool would sit behind an organization's SSO/corporate auth layer (Okta, Azure AD, etc.)
- Time spent on auth is time not spent on the features that demonstrate engineering quality

**Consequences:**
- (+) Simpler codebase — no auth middleware, no token management, no login page
- (+) More time to focus on core features, tests, and UX polish
- (-) Not production-ready as-is — would need auth before real deployment

---

## 8. TanStack Table vs Custom Table Implementation

**Decision:** TanStack Table v8

**Alternatives:** Custom HTML table with manual sorting/pagination, AG Grid, react-table v7

**Reasoning:**
- Headless library — provides logic without enforcing styling
- Works seamlessly with server-side pagination
- Handles sorting, filtering, and column management
- Well-maintained, widely used, excellent TypeScript support
- Pairs naturally with shadcn/ui Table components

**Consequences:**
- (+) Production-grade table behavior with minimal code
- (+) Server-side operations are a first-class feature
- (-) Learning curve for the headless API pattern
- (-) More setup than AG Grid's batteries-included approach

---

## 9. Recharts vs Chart.js vs D3

**Decision:** Recharts

**Alternatives:** Chart.js (via react-chartjs-2), D3.js, Nivo

**Reasoning:**
- React-native composable API — charts are JSX components
- Lightweight (~40KB gzipped vs Chart.js ~60KB)
- Integrates well with shadcn/ui theming and Tailwind colors
- Sufficient for the bar charts and summary visualizations needed
- Simple API — no canvas manipulation or complex configuration

**Consequences:**
- (+) Quick to implement — declarative JSX syntax
- (+) Responsive and themeable
- (-) Less customizable than D3 for exotic visualizations
- (-) Limited animation options compared to Chart.js
