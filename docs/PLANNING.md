# Planning & Design Notes

## Development Phases

The solution is built in deliberate phases, each producing a working increment:

### Phase 1: Think Before Code
Write requirements, architecture, and design documentation. This ensures clarity on scope, deliberate exclusions, and technical decisions before any code is written.

### Phase 2: Backend Foundation
Build the data layer first — model, repository, service, endpoints — each with tests. This establishes the API contract that the frontend will consume.

### Phase 3: Seed Script
Create the 10k employee seed script. This provides realistic data to test both backend performance and frontend UX with real-world volumes.

### Phase 4: Frontend
Build the UI against the established API. Dashboard first (insights), then employee management (CRUD). This order matches the user persona's primary need: answering salary questions.

### Phase 5: Polish & Deploy
Docker Compose for one-command startup, final documentation, README with setup instructions.

## Data Modeling Decisions

### Why These Fields?

The assessment requires "full name, job title, country, salary, along with any other meaningful data." Here's the reasoning for each additional field:

| Field | Why It's Meaningful |
|-------|---------------------|
| **email** | Every employee system needs a unique business identifier. Full names can collide; emails don't. |
| **department** | Enables department-level salary analysis — a natural question for HR ("How does Engineering compare to Marketing?"). |
| **currency** | With employees across countries, salary "100,000" is ambiguous without knowing if it's USD, EUR, or INR. Storing currency explicitly prevents misinterpretation. |
| **employment_type** | A part-time employee earning 50k vs a full-time employee earning 50k are very different data points. This context matters for salary analysis. |
| **hire_date** | Standard HR data. Enables future features like tenure-based analysis or new-hire salary trends. |

### What Was Excluded from the Model

- **Employee ID / Badge Number**: Not needed for salary management; database ID serves as identifier
- **Manager / Reporting Structure**: Adds hierarchy complexity; not needed for salary insights
- **Address / Phone**: Personal data that doesn't contribute to salary management
- **Performance Rating**: Would enable performance-salary correlation, but adds significant scope
- **Benefits / Bonus**: Different data domain; salary is the focus

## API Design Approach

### RESTful Conventions
- Resources are nouns (`/employees`, not `/getEmployees`)
- HTTP verbs for actions (GET, POST, PUT, DELETE)
- Versioned under `/api/v1/` for future evolution
- Consistent error responses with meaningful messages

### Pagination Strategy
- Server-side pagination with `page` and `page_size` query parameters
- Default page size: 20, maximum: 100
- Response includes `total`, `page`, `page_size`, `total_pages` for client navigation
- Why server-side: 10,000 rows is too many to send to the client at once

### Filter and Search
- Filters via query parameters: `?country=Germany&department=Engineering`
- Search via `?search=john` — matches against full name
- Filters and search are combinable
- All filtering and searching happens in SQL, not in Python

### Insights as Separate Resource
Insights are at `/api/v1/insights/` rather than nested under `/employees` because:
- They represent aggregate data, not individual employee records
- Different caching strategies apply (insights change less frequently)
- Clearer API surface for the frontend

## UI/UX Design Decisions

### Dashboard-First Landing
The home page shows salary insights, not the employee list. Reasoning:
- The HR Manager's primary question is "How does our org pay people?" — insights answer this
- The employee list is a management tool; the dashboard is the analytical tool
- Matches the assessment's emphasis on "able to answer questions about how the org pays people"

### Data Table for Employees
Using TanStack Table with server-side operations because:
- 10,000 rows cannot be loaded into the browser at once
- Server-side pagination keeps responses small (~20 records)
- URL-based pagination/filters make views shareable and bookmarkable
- Column sorting, search, and filters provide the "Excel-like" experience the HR Manager is used to

### Form Validation
- Client-side validation with Zod schemas for instant feedback
- Server-side validation in Pydantic for data integrity
- Clear error messages next to the field that failed
- Required fields marked visually

### Confirmation Before Delete
Delete actions show a confirmation dialog because:
- Deletion is irreversible in this system (no soft delete)
- The HR Manager is dealing with real employee data — accidental deletion is costly
- Standard UX practice for destructive actions

## Seed Data Strategy

### Name Generation
- Load `first_names.txt` and `last_names.txt` into memory arrays
- Generate full names by combining random first + last names
- This produces realistic-looking names with natural distribution

### Realistic Data Distribution
- **Countries**: 10-15 countries with weighted distribution (more employees in larger markets)
- **Departments**: 8-10 departments (Engineering, Marketing, Sales, HR, Finance, Operations, Legal, Product, Design, Support)
- **Job Titles**: 15-20 titles distributed across seniority levels
- **Salaries**: Ranges vary by country and job title (a Senior Engineer in the US earns differently than in India)
- **Currency**: Mapped to country (US→USD, Germany→EUR, India→INR, etc.)
- **Employment Type**: ~80% full-time, ~15% contract, ~5% part-time
- **Hire Dates**: Distributed over the past 10 years

### Performance
- Bulk insert using `session.execute(insert(Employee), list_of_dicts)` — one SQL statement for all 10k rows
- Name files loaded once into memory, not re-read per record
- Target: under 3 seconds for full seed

## Testing Strategy

### What Gets Tested

| Layer | What's Tested | How |
|-------|---------------|-----|
| **Repository** | SQL queries return correct data | In-memory SQLite, real queries |
| **Service** | Business logic, validation rules | Mocked repository |
| **Endpoints** | HTTP status codes, request/response shapes | FastAPI TestClient + in-memory SQLite |
| **Insights** | Aggregation accuracy (min, max, avg) | Known test data with predictable results |

### What's NOT Tested (and why)
- **Frontend components**: Would require Vitest + JSDOM setup; backend is the higher-value test target
- **Database migrations**: No migrations used (tables created on startup for SQLite)
- **External integrations**: No external services to mock

### Test Design Principles
- **Fast**: All tests use in-memory SQLite — no disk I/O, no network
- **Deterministic**: Fixed seed data in fixtures — same input, same output, every time
- **Isolated**: Each test gets a fresh database session — no test interdependence
- **Readable**: Test names describe the behavior being verified, not the implementation
