# Requirements Document — Employee Salary Management Tool

## Goal

Build a web-based employee salary management tool for ACME org, replacing the current Excel-based workflow. The tool enables the HR Manager to manage salary data for 10,000 employees across multiple countries and answer compensation-related questions through an intuitive interface.

## User Persona

**HR Manager at ACME org**

- Manages salary data for ~10,000 employees across multiple countries
- Currently relies on Excel spreadsheets — tedious, error-prone, and hard to get aggregate insights
- Needs to quickly look up, update, and analyze employee compensation data
- Wants to answer questions like: "What's the average salary for engineers in Germany?" or "Which country has the highest average pay?"

## In-Scope Features

### 1. Employee Management (CRUD)

- **Add** new employees via a web form with validation
- **View** employees in a searchable, filterable, paginated data table
- **Update** existing employee records through an edit form
- **Delete** employees with a confirmation step

**Employee data captured:**

| Field | Rationale |
|-------|-----------|
| Full Name | Required — primary identifier for HR |
| Email | Unique business identifier; essential for any employee system |
| Job Title | Required — drives salary benchmarking and insights |
| Department | Groups employees for organizational analysis |
| Country | Required — multi-country salary comparison is a core use case |
| Salary | Required — the central data point of the tool |
| Currency | Multi-country means multi-currency; avoids ambiguity in salary interpretation |
| Employment Type | Full-time vs part-time vs contract affects salary context |
| Hire Date | Standard HR data; enables future tenure-based analysis |

### 2. Salary Insights

- Minimum, maximum, and average salary by country
- Average salary for a given job title within a country
- Additional meaningful metrics:
  - Global salary summary (min, max, average, median, total headcount)
  - Salary breakdown by department
  - Headcount distribution across countries
  - Top-paying job titles

### 3. Data Seeding

- Seed script generating 10,000 realistic employee records
- Names generated from provided `first_names.txt` and `last_names.txt`
- Performance-optimized for repeated execution

### 4. Search, Filter, and Pagination

- Full-text search on employee name
- Filter by country, department, and job title
- Server-side pagination for smooth handling of 10,000 records

## Deliberately Out of Scope

| Feature | Reasoning |
|---------|-----------|
| **Authentication / RBAC** | This is a single-user internal tool for one HR Manager. Adding auth would increase complexity without delivering value for this scope. In production, this would be behind an SSO/corporate auth layer. |
| **Salary History UI** | The data model supports salary history (separate Salary table with effective_date), but the UI focuses on current-state management. A salary history view per employee is a natural iteration-2 feature. |
| **Payroll Processing / Tax Calculations** | This tool manages salary *data*, not payroll *execution*. Tax rules vary by country and change frequently — this is a separate domain that specialized payroll software handles. |
| **Multi-Currency Conversion** | Exchange rates fluctuate daily. Rather than building unreliable conversion, we store the explicit currency per employee and display salaries in their local currency. Conversion can be added later with a reliable rate API. |
| **Export to Excel/CSV** | A natural next step given the user persona's Excel background, but not part of the core requirements. Can be added as a thin endpoint returning CSV. |
| **Bulk Import from Excel** | Migration from Excel is a one-time setup concern, not core ongoing functionality. The seed script demonstrates the data loading pattern. |
| **Email Notifications** | No workflow triggers or alerts are needed for a data management tool. |
| **Employee Photos / Documents** | Adds file storage complexity (S3/local) without contributing to salary management. |

## Non-Functional Requirements

- **Performance**: API responses under 200ms for list and insight queries
- **Usability**: Intuitive UI that an HR Manager can use without training
- **Responsiveness**: Works on laptop and tablet screen sizes
- **Data Handling**: Smooth experience with 10,000 employee records (no UI freezing or long waits)
- **Developer Experience**: One-command setup for new developers via Docker Compose
