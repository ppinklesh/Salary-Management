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
