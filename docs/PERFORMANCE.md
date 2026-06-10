# Performance Considerations

## 1. Seed Script Performance

The assessment states: "Assume that engineers run this script regularly, and performance of the script matters."

### Approach: Bulk Insert

**Instead of:**
```python
# Slow: 10,000 individual INSERT statements
for employee_data in employees:
    employee = Employee(**employee_data)
    session.add(employee)
session.commit()
```

**We use:**
```python
# Fast: Single INSERT with 10,000 value sets
from sqlalchemy import insert
session.execute(insert(Employee), list_of_employee_dicts)
session.commit()
```

### Why This Is Faster
- **Single SQL statement** vs 10,000 individual statements
- **No ORM overhead** per row (no object instantiation, no identity map tracking)
- **Single transaction** — one commit instead of per-row or batched commits
- **SQLite optimization** — SQLite handles bulk inserts efficiently when wrapped in a single transaction

### Other Optimizations
- Name files (`first_names.txt`, `last_names.txt`) loaded into memory once, not re-read per record
- Random data generation uses `random.choice()` on pre-loaded arrays — O(1) per pick
- Email uniqueness ensured by combining name with a counter, avoiding collision retries
- Target execution time: under 3 seconds for 10,000 records

### Idempotency
The seed script truncates the table before inserting, making it safe to run repeatedly without accumulating duplicate data.

---

## 2. Database Query Performance

### Index Strategy

Indexes are placed on columns that appear in WHERE clauses, ORDER BY, and GROUP BY:

| Column | Used For |
|--------|----------|
| `full_name` | Search (`WHERE full_name LIKE '%john%'`) |
| `country` | Filter + GROUP BY for insights |
| `job_title` | Filter + GROUP BY for insights |
| `department` | Filter + GROUP BY for insights |
| `email` | UNIQUE constraint (implicit index) |

### SQL-Level Aggregation

Salary insights (min, max, avg) are computed in SQL, not in Python:

**Instead of:**
```python
# Slow: Load all rows into Python, then compute
employees = session.query(Employee).all()
avg_salary = sum(e.salary for e in employees) / len(employees)
```

**We use:**
```python
# Fast: Database computes the aggregate
from sqlalchemy import func
result = session.query(
    func.min(Employee.salary),
    func.max(Employee.salary),
    func.avg(Employee.salary),
    func.count(Employee.id)
).filter(Employee.country == country).first()
```

### Why This Matters
- SQL aggregation processes data in the database engine — no serialization or network transfer of 10k rows
- SQLite's query optimizer uses indexes for GROUP BY operations
- Memory-efficient: only the aggregate results are returned, not all rows

### Pagination with LIMIT/OFFSET

```sql
SELECT * FROM employees
WHERE country = 'Germany'
ORDER BY id
LIMIT 20 OFFSET 40
```

- Returns only 20 rows per request regardless of total dataset size
- With an index on the filter column, the database can efficiently skip to the offset
- For very large offsets (page 500+), keyset pagination would be better — but OFFSET is sufficient for 10k rows

---

## 3. API Performance

### Response Size
- Paginated list responses return ~20 records (~5-10KB JSON) instead of all 10,000 (~2MB)
- Insight endpoints return aggregate data — a few dozen rows at most
- No N+1 query problems — each endpoint makes exactly 1-2 database queries

### Serialization
- Pydantic v2 uses Rust-based validation — significantly faster than v1
- Response models include only the fields needed by the frontend (no over-fetching)

### CORS
- Configured to allow the frontend origin only — no wildcard in production

---

## 4. Frontend Performance

### Server Components by Default
- Next.js App Router renders layout, navigation, and static content on the server
- Only interactive elements (tables, charts, forms) are client components
- Reduces JavaScript sent to the browser

### Client-Side Optimizations
- **Debounced search**: Search input waits 300ms after the user stops typing before making an API call — prevents flooding the backend with requests on every keystroke
- **Skeleton loading states**: Show placeholder UI while data loads — the page feels responsive even before data arrives
- **Optimistic UI**: Toast notifications provide instant feedback for CRUD operations
- **No client-side data caching of stale data**: After a create/update/delete, the table refetches to ensure accuracy

### Bundle Size
- shadcn/ui components are tree-shakeable — only imported components are bundled
- Recharts is loaded only on the dashboard page, not on the employee management page
- No unnecessary dependencies (no axios, no lodash, no moment.js)

---

## 5. UX Performance (Perceived Speed)

Performance isn't just about milliseconds — it's about how fast the app *feels*:

| Pattern | Effect |
|---------|--------|
| Skeleton loaders | Page structure appears instantly; data fills in |
| Toast notifications | Immediate confirmation of actions without page reload |
| Debounced search | Typing feels smooth; no input lag |
| Server-side pagination | Page transitions are fast (small payloads) |
| Form validation | Errors appear as the user types, not after submit |
| Loading spinners on buttons | User knows their click was registered |

These patterns ensure the HR Manager never wonders "did that work?" or "is this broken?" — the app provides constant, clear feedback.
