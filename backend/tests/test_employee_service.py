from datetime import date

import pytest
from fastapi import HTTPException

from app.models.employee import Employee
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.services.employee_service import EmployeeService


class TestEmployeeServiceCreate:
    def test_create_employee(self, db):
        service = EmployeeService(db)
        data = EmployeeCreate(
            full_name="Test User",
            email="test@example.com",
            job_title="Engineer",
            department="Engineering",
            country="United States",
            salary=90000,
            currency="USD",
            employment_type="full_time",
            hire_date=date(2023, 1, 1),
        )

        result = service.create_employee(data)

        assert result.id is not None
        assert result.full_name == "Test User"
        assert result.email == "test@example.com"

    def test_create_duplicate_email_raises(self, db):
        service = EmployeeService(db)
        data = EmployeeCreate(
            full_name="User One",
            email="same@example.com",
            job_title="Engineer",
            department="Engineering",
            country="US",
            salary=80000,
            currency="USD",
            employment_type="full_time",
            hire_date=date(2023, 1, 1),
        )
        service.create_employee(data)

        data2 = EmployeeCreate(
            full_name="User Two",
            email="same@example.com",
            job_title="Manager",
            department="Product",
            country="US",
            salary=90000,
            currency="USD",
            employment_type="full_time",
            hire_date=date(2023, 1, 1),
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create_employee(data2)
        assert exc_info.value.status_code == 409


class TestEmployeeServiceGet:
    def test_get_existing_employee(self, db):
        service = EmployeeService(db)
        data = EmployeeCreate(
            full_name="Find Me",
            email="findme@example.com",
            job_title="Analyst",
            department="Analytics",
            country="UK",
            salary=60000,
            currency="GBP",
            employment_type="full_time",
            hire_date=date(2022, 6, 1),
        )
        created = service.create_employee(data)

        result = service.get_employee(created.id)

        assert result.full_name == "Find Me"

    def test_get_nonexistent_employee_raises(self, db):
        service = EmployeeService(db)

        with pytest.raises(HTTPException) as exc_info:
            service.get_employee(99999)
        assert exc_info.value.status_code == 404


class TestEmployeeServiceUpdate:
    def test_update_salary(self, db):
        service = EmployeeService(db)
        data = EmployeeCreate(
            full_name="Update Me",
            email="update@example.com",
            job_title="Junior Dev",
            department="Engineering",
            country="US",
            salary=60000,
            currency="USD",
            employment_type="full_time",
            hire_date=date(2023, 1, 1),
        )
        created = service.create_employee(data)

        update = EmployeeUpdate(salary=75000, job_title="Mid-Level Dev")
        result = service.update_employee(created.id, update)

        assert result.salary == 75000
        assert result.job_title == "Mid-Level Dev"

    def test_update_with_no_fields_raises(self, db):
        service = EmployeeService(db)
        data = EmployeeCreate(
            full_name="No Update",
            email="noupdate@example.com",
            job_title="Dev",
            department="Eng",
            country="US",
            salary=50000,
            currency="USD",
            employment_type="full_time",
            hire_date=date(2023, 1, 1),
        )
        created = service.create_employee(data)

        with pytest.raises(HTTPException) as exc_info:
            service.update_employee(created.id, EmployeeUpdate())
        assert exc_info.value.status_code == 400


class TestEmployeeServiceDelete:
    def test_delete_employee(self, db):
        service = EmployeeService(db)
        data = EmployeeCreate(
            full_name="Delete Me",
            email="delete@example.com",
            job_title="Temp",
            department="HR",
            country="US",
            salary=40000,
            currency="USD",
            employment_type="contract",
            hire_date=date(2023, 6, 1),
        )
        created = service.create_employee(data)

        service.delete_employee(created.id)

        with pytest.raises(HTTPException) as exc_info:
            service.get_employee(created.id)
        assert exc_info.value.status_code == 404


class TestEmployeeServiceList:
    def test_list_with_pagination(self, db):
        service = EmployeeService(db)
        for i in range(25):
            service.create_employee(
                EmployeeCreate(
                    full_name=f"Employee {i}",
                    email=f"emp{i}@example.com",
                    job_title="Dev",
                    department="Eng",
                    country="US",
                    salary=50000 + i * 1000,
                    currency="USD",
                    employment_type="full_time",
                    hire_date=date(2023, 1, 1),
                )
            )

        result = service.list_employees(page=1, page_size=10)

        assert result["total"] == 25
        assert len(result["data"]) == 10
        assert result["total_pages"] == 3
        assert result["page"] == 1

    def test_list_with_search(self, db):
        service = EmployeeService(db)
        service.create_employee(
            EmployeeCreate(
                full_name="Alice Wonderland",
                email="alice@example.com",
                job_title="Dev",
                department="Eng",
                country="US",
                salary=80000,
                currency="USD",
                employment_type="full_time",
                hire_date=date(2023, 1, 1),
            )
        )
        service.create_employee(
            EmployeeCreate(
                full_name="Bob Builder",
                email="bob@example.com",
                job_title="Dev",
                department="Eng",
                country="US",
                salary=75000,
                currency="USD",
                employment_type="full_time",
                hire_date=date(2023, 1, 1),
            )
        )

        result = service.list_employees(search="alice")

        assert result["total"] == 1
        assert result["data"][0].full_name == "Alice Wonderland"
