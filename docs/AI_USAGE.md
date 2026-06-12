# AI Usage Log

## Tools Used

- **Cursor IDE** with Claude (Anthropic) as the AI assistant
- Used throughout the development process for code generation, architectural planning, and documentation

## How AI Was Used

### 1. Planning & Architecture (Human-Led, AI-Assisted)

**What I did manually:**
- Read and analyzed the assessment requirements
- Made all architectural decisions (tech stack, layer separation, data model design)
- Defined the scope, deliberate exclusions, and their reasoning
- Decided on the commit strategy and development phases

**How AI helped:**
- Generated structured documentation from my decisions (REQUIREMENTS.md, ARCHITECTURE.md, etc.)
- Suggested industry best practices for FastAPI project structure
- Helped articulate trade-offs in a clear, structured format

### 2. Backend Development (AI-Accelerated, Human-Reviewed)

**What I did manually:**
- Designed the two-table data model (`employees` + `salaries`) and chose which fields belong in each
- Defined the API contract (endpoints, request/response shapes)
- Made decisions on pagination strategy, filter approach, and error handling
- Reviewed all generated code for correctness, edge cases, and clean code standards

**How AI helped:**
- Generated boilerplate code (SQLAlchemy models, Pydantic schemas, FastAPI endpoints)
- Wrote repository layer CRUD operations
- Generated test fixtures and test cases
- Helped with SQLAlchemy aggregation queries for salary insights

**What I corrected/adjusted:**
- Verified SQL query correctness for aggregation endpoints
- Ensured proper error handling and edge cases
- Adjusted code structure to follow clean architecture principles

### 3. Seed Script (Collaborative)

**What I did manually:**
- Defined the data distribution strategy (country weights, salary ranges by role)
- Chose bulk insert over per-row ORM for performance

**How AI helped:**
- Generated the seed script with realistic data distributions
- Implemented the bulk insert pattern

### 4. Frontend Development (AI-Accelerated, Human-Designed)

**What I did manually:**
- Designed the page layout and user flow
- Chose shadcn/ui components and their configuration
- Made UX decisions (dashboard-first, confirmation dialogs, toast notifications)

**How AI helped:**
- Generated React components with TypeScript types
- Built the TanStack Table configuration with server-side pagination
- Created chart components with Recharts
- Generated form validation schemas with Zod

### 5. Documentation (Collaborative)

**What I did manually:**
- Defined what to document and the key messages for each artifact
- Made all technical and product decisions documented in the artifacts

**How AI helped:**
- Structured and formatted the documentation
- Ensured consistency across documents

## Sample Prompts Used

These are representative prompts from the assignment work — written roughly how I actually typed them, not cleaned up for presentation.

### Planning & backend setup

> need to build a salary management web app for HR. around 10k employees, multiple countries. thinking fastapi + sqlite for backend and nextjs for frontend. can you help me sketch a layered structure — endpoints, service, repo — before we write code?

> lets keep employee info and salary in separate tables. when salary changes insert a new row with effective date, dont update the old one. api can still return current salary on the employee object

> write pytest tests for employee create/list/update. use in memory sqlite for tests

### Seed data

> seed script needs to create 10000 employees. use first_names.txt and last_names.txt from the seed folder. should run fast if i run it multiple times

### Employee APIs & insights

> GET /employees should support page, page_size, search on name, filters for country department job title, and sort. pagination has to be server side otherwise 10k rows will kill the ui

> need insight endpoints — summary stats (min max avg median headcount), breakdown by country, by department, by job title. only active employees for dashboard numbers

### Frontend

> build employees page with a table, filters at top, add/edit in a dialog. hook it up to the api client we have in lib/api.ts

> dashboard with summary cards and bar charts for country and department. use recharts if thats easiest with shadcn

> offboard button should open a dialog for exit date and reason. inactive employees should still show in the table when i filter status=inactive. rehire for people who resigned

### Dev experience & fixes

> docker compose file for backend + frontend so someone can clone and run docker compose up --build

> getting nested button hydration error in employee table dropdown menu, can you fix without breaking the actions menu

> store salary in local currency based on country. hr enters local amount on the form, show usd as reference only on dashboard

### Testing & edge cases

> add test for duplicate email on create — should return 409

> what edge cases am i missing for employee update? like updating inactive employee, empty body, duplicate email on someone else

> insights tests are failing on salary numbers because of float precision. fix with pytest.approx or whatever is standard

> write tests for offboard — already inactive employee, exit date before hire date, employee not found

> test list employees with search + filters together. also pagination page 2 should return different rows than page 1

> insights summary when db is empty should return zeros not crash

> add endpoint test for rehire — success case and trying to rehire someone who was terminated not resigned

> resigned employee left the company but same email blocks add employee because email is unique. only active employees should block email, resigned people can come back as new record

### Bug fixes & errors

> next build failing — Type error exit_reason string not assignable to union type in offboard dialog. fix it

> sonarqube complaining about nested ternary in employee-table, can you extract it to a helper

> chart bars all showing black/white, need actual colors for country and department charts

> left sidebar scrolls with the page, it should stay fixed only main content scrolls

> fix this error: Prefer String#replaceAll() over String#replace in employee-table

> FormEvent is deprecated in employee-form-dialog handleSubmit, what should i use instead

> Do not perform equality checks with floating point values in test_employee_endpoints — use pytest.approx

## Delegation Strategy

| Task Type | Delegated to AI? | Reasoning |
|-----------|-------------------|-----------|
| Architectural decisions | No | Requires judgment and context about the assessment goals |
| Boilerplate code | Yes | Repetitive, well-defined patterns — high confidence in AI output |
| Business logic | Partially | AI generates, human reviews for correctness |
| Test cases | Partially | AI suggests test scenarios, human verifies coverage and edge cases |
| Documentation structure | Yes | Formatting and structure are well-suited for AI |
| Data model design | No | Requires product thinking about what fields serve the user persona |

## Review Process

Every piece of AI-generated code was reviewed for:
1. **Correctness**: Does it do what it should? Are edge cases handled?
2. **Clean code**: Is it readable? Are names meaningful? Is the structure logical?
3. **Security**: No SQL injection, proper input validation, no hardcoded secrets
4. **Performance**: Efficient queries, proper pagination, no N+1 problems
5. **Consistency**: Does it follow the patterns established in the rest of the codebase?

## Key Takeaway

AI was used as an accelerator, not a replacement for engineering judgment. All design decisions, architectural choices, and quality standards were human-driven. AI excelled at generating boilerplate, structuring documentation, and implementing well-defined patterns — freeing up time to focus on the decisions that matter.
