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
from app.models.employee import Employee

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

JOB_TITLES = [
    "Software Engineer",
    "Senior Software Engineer",
    "Staff Engineer",
    "Engineering Manager",
    "Product Manager",
    "Senior Product Manager",
    "Data Analyst",
    "Data Scientist",
    "Marketing Specialist",
    "Sales Representative",
    "Account Executive",
    "HR Specialist",
    "Financial Analyst",
    "Operations Manager",
    "UX Designer",
    "UI Designer",
    "Legal Counsel",
    "Support Specialist",
    "DevOps Engineer",
    "QA Engineer",
]

DEPT_JOB_MAPPING = {
    "Engineering": [
        "Software Engineer", "Senior Software Engineer", "Staff Engineer",
        "Engineering Manager", "DevOps Engineer", "QA Engineer",
    ],
    "Product": ["Product Manager", "Senior Product Manager"],
    "Marketing": ["Marketing Specialist"],
    "Sales": ["Sales Representative", "Account Executive"],
    "Human Resources": ["HR Specialist"],
    "Finance": ["Financial Analyst"],
    "Operations": ["Operations Manager"],
    "Design": ["UX Designer", "UI Designer"],
    "Legal": ["Legal Counsel"],
    "Customer Support": ["Support Specialist"],
}

SALARY_RANGES_USD = {
    "Software Engineer": (70000, 130000),
    "Senior Software Engineer": (120000, 180000),
    "Staff Engineer": (160000, 250000),
    "Engineering Manager": (140000, 220000),
    "Product Manager": (90000, 150000),
    "Senior Product Manager": (130000, 200000),
    "Data Analyst": (60000, 100000),
    "Data Scientist": (90000, 160000),
    "Marketing Specialist": (50000, 90000),
    "Sales Representative": (45000, 80000),
    "Account Executive": (60000, 120000),
    "HR Specialist": (50000, 85000),
    "Financial Analyst": (65000, 110000),
    "Operations Manager": (70000, 120000),
    "UX Designer": (70000, 130000),
    "UI Designer": (60000, 110000),
    "Legal Counsel": (90000, 180000),
    "Support Specialist": (35000, 65000),
    "DevOps Engineer": (80000, 150000),
    "QA Engineer": (60000, 110000),
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

NUM_EMPLOYEES = 10_000


def load_names(filename: str) -> list[str]:
    filepath = Path(__file__).parent / filename
    with open(filepath) as f:
        return [line.strip() for line in f if line.strip()]


def generate_employees(
    first_names: list[str], last_names: list[str], count: int
) -> list[dict]:
    employees = []
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
        salary = round(random.uniform(base_min, base_max) * multiplier, 2)

        employment_type = random.choices(
            EMPLOYMENT_TYPES, weights=EMPLOYMENT_WEIGHTS, k=1
        )[0]
        hire_date = start_date + timedelta(days=random.randint(0, date_range))

        employees.append(
            {
                "full_name": full_name,
                "email": email,
                "job_title": job_title,
                "department": department,
                "country": country,
                "salary": salary,
                "currency": currency,
                "employment_type": employment_type,
                "hire_date": hire_date,
            }
        )

    return employees


def seed():
    print(f"Seeding {NUM_EMPLOYEES} employees...")
    start = time.perf_counter()

    first_names = load_names("first_names.txt")
    last_names = load_names("last_names.txt")
    print(f"  Loaded {len(first_names)} first names, {len(last_names)} last names")

    create_tables()

    employees = generate_employees(first_names, last_names, NUM_EMPLOYEES)
    gen_time = time.perf_counter() - start
    print(f"  Generated {len(employees)} records in {gen_time:.2f}s")

    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM employees"))
        db.execute(insert(Employee), employees)
        db.commit()
    finally:
        db.close()

    total_time = time.perf_counter() - start
    print(f"  Seeding complete in {total_time:.2f}s")


if __name__ == "__main__":
    seed()
