from __future__ import annotations

import math

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    def __init__(self, db: Session):
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

        return {
            "data": employees,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if total > 0 else 0,
        }

    def create_employee(self, data: EmployeeCreate) -> Employee:
        existing = self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Employee with email {data.email} already exists",
            )

        employee = Employee(**data.model_dump())
        return self.repo.create(employee)

    def update_employee(self, employee_id: int, data: EmployeeUpdate) -> Employee:
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

        return self.repo.update(employee, update_data)

    def delete_employee(self, employee_id: int) -> None:
        employee = self.get_employee(employee_id)
        self.repo.delete(employee)
