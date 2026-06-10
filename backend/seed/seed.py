"""
High-performance seed script for generating 10,000 employee records.

Uses bulk insert for optimal performance — completes in under 3 seconds.

Usage:
    cd backend
    python -m seed.seed
"""

import random
import sys
import time
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import insert, text

from app.database import SessionLocal, create_tables, engine
from app.models.employee import Employee, Salary

COUNTRIES = [
    ("United States", "USD"),
    ("United Kingdom", "GBP"),
    ("Germany", "EUR"),
    ("France", "EUR"),
    ("India", "INR"),
    ("Canada", "CAD"),
    ("Australia", "AUD"),
    ("Japan", "JPY"),
    ("Brazil", "BRL"),
    ("Singapore", "SGD"),
    ("Netherlands", "EUR"),
    ("Sweden", "SEK"),
]

COUNTRY_WEIGHTS = [25, 10, 10, 8, 15, 8, 5, 5, 5, 3, 3, 3]

DEPARTMENTS = [
    "Engineering",
    "Product",
    "Marketing",
    "Sales",
    "Human Resources",
    "Finance",
    "Operations",
    "Design",
    "Legal",
    "Customer Support",
]

SOFTWARE_ENGINEER = "Software Engineer"
SENIOR_SOFTWARE_ENGINEER = "Senior Software Engineer"
STAFF_ENGINEER = "Staff Engineer"
ENGINEERING_MANAGER = "Engineering Manager"
PRODUCT_MANAGER = "Product Manager"
SENIOR_PRODUCT_MANAGER = "Senior Product Manager"
DATA_ANALYST = "Data Analyst"
DATA_SCIENTIST = "Data Scientist"
MARKETING_SPECIALIST = "Marketing Specialist"
SALES_REPRESENTATIVE = "Sales Representative"
ACCOUNT_EXECUTIVE = "Account Executive"
HR_SPECIALIST = "HR Specialist"
FINANCIAL_ANALYST = "Financial Analyst"
OPERATIONS_MANAGER = "Operations Manager"
UX_DESIGNER = "UX Designer"
UI_DESIGNER = "UI Designer"
LEGAL_COUNSEL = "Legal Counsel"
SUPPORT_SPECIALIST = "Support Specialist"
DEVOPS_ENGINEER = "DevOps Engineer"
QA_ENGINEER = "QA Engineer"

SALARY_RANGES_USD = {
    SOFTWARE_ENGINEER: (70000, 130000),
    SENIOR_SOFTWARE_ENGINEER: (120000, 180000),
    STAFF_ENGINEER: (160000, 250000),
    ENGINEERING_MANAGER: (140000, 220000),
    PRODUCT_MANAGER: (90000, 150000),
    SENIOR_PRODUCT_MANAGER: (130000, 200000),
    DATA_ANALYST: (60000, 100000),
    DATA_SCIENTIST: (90000, 160000),
    MARKETING_SPECIALIST: (50000, 90000),
    SALES_REPRESENTATIVE: (45000, 80000),
    ACCOUNT_EXECUTIVE: (60000, 120000),
    HR_SPECIALIST: (50000, 85000),
    FINANCIAL_ANALYST: (65000, 110000),
    OPERATIONS_MANAGER: (70000, 120000),
    UX_DESIGNER: (70000, 130000),
    UI_DESIGNER: (60000, 110000),
    LEGAL_COUNSEL: (90000, 180000),
    SUPPORT_SPECIALIST: (35000, 65000),
    DEVOPS_ENGINEER: (80000, 150000),
    QA_ENGINEER: (60000, 110000),
}

JOB_TITLES = list(SALARY_RANGES_USD)

DEPT_JOB_MAPPING = {
    "Engineering": [
        SOFTWARE_ENGINEER,
        SENIOR_SOFTWARE_ENGINEER,
        STAFF_ENGINEER,
        ENGINEERING_MANAGER,
        DEVOPS_ENGINEER,
        QA_ENGINEER,
    ],
    "Product": [PRODUCT_MANAGER, SENIOR_PRODUCT_MANAGER],
    "Marketing": [MARKETING_SPECIALIST],
    "Sales": [SALES_REPRESENTATIVE, ACCOUNT_EXECUTIVE],
    "Human Resources": [HR_SPECIALIST],
    "Finance": [FINANCIAL_ANALYST],
    "Operations": [OPERATIONS_MANAGER],
    "Design": [UX_DESIGNER, UI_DESIGNER],
    "Legal": [LEGAL_COUNSEL],
    "Customer Support": [SUPPORT_SPECIALIST],
}

COUNTRY_SALARY_MULTIPLIERS = {
    "United States": 1.0,
    "United Kingdom": 0.85,
    "Germany": 0.80,
    "France": 0.75,
    "India": 0.25,
    "Canada": 0.90,
    "Australia": 0.90,
    "Japan": 0.80,
    "Brazil": 0.35,
    "Singapore": 0.95,
    "Netherlands": 0.82,
    "Sweden": 0.78,
}

EMPLOYMENT_TYPES = ["full_time", "part_time", "contract"]
EMPLOYMENT_WEIGHTS = [80, 5, 15]

EXIT_REASONS = ["terminated", "resigned", "retired", "layoff", "end_of_contract", "other"]
INACTIVE_RATE = 0.05

NUM_EMPLOYEES = 10_000


def load_names(filename: str) -> list[str]:
    filepath = Path(__file__).parent / filename
    with open(filepath) as f:
        return [line.strip() for line in f if line.strip()]


def generate_data(
    first_names: list[str], last_names: list[str], count: int
) -> tuple[list[dict], list[dict]]:
    employees = []
    salaries = []
    used_emails: set[str] = set()
    start_date = date(2015, 1, 1)
    date_range = (date.today() - start_date).days

    for i in range(count):
        first = random.choice(first_names)
        last = random.choice(last_names)
        full_name = f"{first} {last}"

        email_base = f"{first.lower()}.{last.lower()}"
        email = f"{email_base}@acme.com"
        counter = 1
        while email in used_emails:
            email = f"{email_base}{counter}@acme.com"
            counter += 1
        used_emails.add(email)

        country, currency = random.choices(COUNTRIES, weights=COUNTRY_WEIGHTS, k=1)[0]
        department = random.choice(DEPARTMENTS)
        job_titles_for_dept = DEPT_JOB_MAPPING.get(department, JOB_TITLES)
        job_title = random.choice(job_titles_for_dept)

        base_min, base_max = SALARY_RANGES_USD.get(job_title, (50000, 100000))
        multiplier = COUNTRY_SALARY_MULTIPLIERS.get(country, 1.0)
        salary_amount = round(random.uniform(base_min, base_max) * multiplier, 2)

        employment_type = random.choices(
            EMPLOYMENT_TYPES, weights=EMPLOYMENT_WEIGHTS, k=1
        )[0]
        hire_date = start_date + timedelta(days=random.randint(0, date_range))

        exit_date = None
        exit_reason = None
        if random.random() < INACTIVE_RATE:
            days_employed = (date.today() - hire_date).days
            if days_employed >= 30:
                exit_offset = random.randint(30, days_employed)
                exit_date = hire_date + timedelta(days=exit_offset)
                exit_reason = random.choice(EXIT_REASONS)

        employee_id = i + 1
        employees.append(
            {
                "id": employee_id,
                "full_name": full_name,
                "email": email,
                "job_title": job_title,
                "department": department,
                "country": country,
                "hire_date": hire_date,
                "exit_date": exit_date,
                "exit_reason": exit_reason,
            }
        )

        salaries.append(
            {
                "employee_id": employee_id,
                "amount": salary_amount,
                "currency": currency,
                "employment_type": employment_type,
                "effective_date": hire_date,
            }
        )

    return employees, salaries


def seed():
    print(f"Seeding {NUM_EMPLOYEES} employees...")
    start = time.perf_counter()

    first_names = load_names("first_names.txt")
    last_names = load_names("last_names.txt")
    print(f"  Loaded {len(first_names)} first names, {len(last_names)} last names")

    create_tables()

    employees, salaries = generate_data(first_names, last_names, NUM_EMPLOYEES)
    gen_time = time.perf_counter() - start
    print(f"  Generated {len(employees)} employees + {len(salaries)} salary records in {gen_time:.2f}s")

    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM salaries"))
        db.execute(text("DELETE FROM employees"))
        db.execute(insert(Employee), employees)
        db.execute(insert(Salary), salaries)
        db.commit()
    finally:
        db.close()

    total_time = time.perf_counter() - start
    print(f"  Seeding complete in {total_time:.2f}s")


if __name__ == "__main__":
    seed()
