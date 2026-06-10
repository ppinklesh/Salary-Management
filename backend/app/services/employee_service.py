from __future__ import annotations

import math

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.employee import Employee, Salary
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = EmployeeRepository(db)

    def get_employee(self, employee_id: int) -> Employee:
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
        sort_by: str = "id",
        sort_order: str = "asc",
    ) -> dict:
        page_size = min(page_size, 100)
        page = max(page, 1)

        employees, total = self.repo.list(
            page=page,
            page_size=page_size,
            search=search,
            country=country,
            department=department,
            job_title=job_title,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        data = []
        for emp in employees:
            emp_dict = {
                "id": emp.id,
                "full_name": emp.full_name,
                "email": emp.email,
                "job_title": emp.job_title,
                "department": emp.department,
                "country": emp.country,
                "hire_date": emp.hire_date,
                "created_at": emp.created_at,
                "updated_at": emp.updated_at,
                "salary": None,
                "currency": None,
                "employment_type": None,
            }
            current = emp.current_salary
            if current:
                emp_dict["salary"] = float(current.amount)
                emp_dict["currency"] = current.currency
                emp_dict["employment_type"] = current.employment_type
            data.append(emp_dict)

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
        employee = self.get_employee(employee_id)

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
            from datetime import date as date_type
            new_salary = Salary(
                employee_id=employee.id,
                amount=salary_updates.get("salary", current.amount),
                currency=salary_updates.get("currency", current.currency),
                employment_type=salary_updates.get("employment_type", current.employment_type),
                effective_date=date_type.today(),
            )
            self.repo.add_salary(new_salary)

        self.db.expire_all()
        employee = self.repo.get_by_id(employee_id)
        return self._to_response(employee, employee.current_salary if employee else None)

    def delete_employee(self, employee_id: int) -> None:
        employee = self.get_employee(employee_id)
        self.repo.delete(employee)

    def _to_response(self, employee: Employee, salary: Salary | None) -> dict:
        return {
            "id": employee.id,
            "full_name": employee.full_name,
            "email": employee.email,
            "job_title": employee.job_title,
            "department": employee.department,
            "country": employee.country,
            "hire_date": employee.hire_date,
            "created_at": employee.created_at,
            "updated_at": employee.updated_at,
            "salary": float(salary.amount) if salary else None,
            "currency": salary.currency if salary else None,
            "employment_type": salary.employment_type if salary else None,
        }
