from __future__ import annotations

import math
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.currency import COUNTRY_CURRENCY
from app.models.employee import Employee, Salary
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeOffboard, EmployeeUpdate


class EmployeeService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = EmployeeRepository(db)

    def get_employee(self, employee_id: int) -> dict:
        employee = self._get_or_404(employee_id)
        return self._to_response(employee, employee.current_salary)

    def _get_or_404(self, employee_id: int) -> Employee:
        employee = self.repo.get_by_id(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with id {employee_id} not found",
            )
        return employee

    def list_employees(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        country: str | None = None,
        department: str | None = None,
        job_title: str | None = None,
        status: str = "active",
        sort_by: str = "id",
        sort_order: str = "asc",
    ) -> dict:
        if status not in {"active", "inactive", "all"}:
            status = "active"

        page_size = min(page_size, 100)
        page = max(page, 1)

        employees, total = self.repo.list(
            page=page,
            page_size=page_size,
            search=search,
            country=country,
            department=department,
            job_title=job_title,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        data = [self._to_response(emp, emp.current_salary) for emp in employees]

        return {
            "data": data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if total > 0 else 0,
        }

    def create_employee(self, data: EmployeeCreate) -> dict:
        existing = self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Employee with email {data.email} already exists",
            )

        employee = Employee(
            full_name=data.full_name,
            email=data.email,
            job_title=data.job_title,
            department=data.department,
            country=data.country,
            hire_date=data.hire_date,
        )
        employee = self.repo.create(employee)

        self._validate_salary_currency(data.country, data.currency)

        salary = Salary(
            employee_id=employee.id,
            amount=data.salary,
            currency=data.currency,
            employment_type=data.employment_type,
            effective_date=data.hire_date,
        )
        self.repo.add_salary(salary)

        return self._to_response(employee, salary)

    def update_employee(self, employee_id: int, data: EmployeeUpdate) -> dict:
        employee = self._get_or_404(employee_id)

        if not employee.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update an inactive employee. Rehire them first.",
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        if "email" in update_data and update_data["email"] != employee.email:
            existing = self.repo.get_by_email(update_data["email"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Email {update_data['email']} is already in use",
                )

        salary_fields = {"salary", "currency", "employment_type"}
        salary_updates = {k: update_data.pop(k) for k in salary_fields if k in update_data}

        if update_data:
            self.repo.update(employee, update_data)

        current = employee.current_salary
        if salary_updates and current:
            country = update_data.get("country", employee.country)
            currency = salary_updates.get("currency", current.currency)
            self._validate_salary_currency(country, currency)

            new_salary = Salary(
                employee_id=employee.id,
                amount=salary_updates.get("salary", current.amount),
                currency=currency,
                employment_type=salary_updates.get(
                    "employment_type", current.employment_type
                ),
                effective_date=date.today(),
            )
            self.repo.add_salary(new_salary)

        self.db.expire_all()
        employee = self.repo.get_by_id(employee_id)
        return self._to_response(employee, employee.current_salary if employee else None)

    def offboard_employee(self, employee_id: int, data: EmployeeOffboard) -> dict:
        employee = self._get_or_404(employee_id)

        if not employee.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee is already inactive",
            )

        if data.exit_date < employee.hire_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exit date cannot be before hire date",
            )

        employee = self.repo.offboard(employee, data.exit_date, data.exit_reason)
        return self._to_response(employee, employee.current_salary)

    def rehire_employee(self, employee_id: int) -> dict:
        employee = self._get_or_404(employee_id)

        if employee.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee is already active",
            )

        employee = self.repo.rehire(employee)
        return self._to_response(employee, employee.current_salary)

    def _to_response(self, employee: Employee, salary: Salary | None) -> dict:
        return {
            "id": employee.id,
            "full_name": employee.full_name,
            "email": employee.email,
            "job_title": employee.job_title,
            "department": employee.department,
            "country": employee.country,
            "hire_date": employee.hire_date,
            "exit_date": employee.exit_date,
            "exit_reason": employee.exit_reason,
            "is_active": employee.is_active,
            "created_at": employee.created_at,
            "updated_at": employee.updated_at,
            "salary": float(salary.amount) if salary else None,
            "currency": salary.currency if salary else None,
            "employment_type": salary.employment_type if salary else None,
        }

    @staticmethod
    def _validate_salary_currency(country: str, currency: str) -> None:
        expected = COUNTRY_CURRENCY.get(country)
        if expected and currency != expected:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Salary currency must be {expected} for employees in {country}",
            )
