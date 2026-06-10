import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_TEST_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_employee_data():
    return {
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "job_title": "Software Engineer",
        "department": "Engineering",
        "country": "United States",
        "salary": 95000.00,
        "currency": "USD",
        "employment_type": "full_time",
        "hire_date": "2023-01-15",
    }


@pytest.fixture
def sample_employees_data():
    return [
        {
            "full_name": "Alice Johnson",
            "email": "alice@example.com",
            "job_title": "Software Engineer",
            "department": "Engineering",
            "country": "United States",
            "salary": 95000.00,
            "currency": "USD",
            "employment_type": "full_time",
            "hire_date": "2022-03-01",
        },
        {
            "full_name": "Bob Smith",
            "email": "bob@example.com",
            "job_title": "Product Manager",
            "department": "Product",
            "country": "United States",
            "salary": 110000.00,
            "currency": "USD",
            "employment_type": "full_time",
            "hire_date": "2021-06-15",
        },
        {
            "full_name": "Clara Mueller",
            "email": "clara@example.com",
            "job_title": "Software Engineer",
            "department": "Engineering",
            "country": "Germany",
            "salary": 75000.00,
            "currency": "EUR",
            "employment_type": "full_time",
            "hire_date": "2023-01-10",
        },
        {
            "full_name": "Dev Patel",
            "email": "dev@example.com",
            "job_title": "Data Analyst",
            "department": "Analytics",
            "country": "India",
            "salary": 1200000.00,
            "currency": "INR",
            "employment_type": "full_time",
            "hire_date": "2022-09-01",
        },
        {
            "full_name": "Eva Schmidt",
            "email": "eva@example.com",
            "job_title": "Designer",
            "department": "Design",
            "country": "Germany",
            "salary": 65000.00,
            "currency": "EUR",
            "employment_type": "contract",
            "hire_date": "2023-04-20",
        },
    ]
