from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeOffboard,
    EmployeeResponse,
    EmployeeUpdate,
    PaginatedResponse,
)
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["employees"])


def get_service(
    db: Annotated[Session, Depends(get_db)],
) -> EmployeeService:
    return EmployeeService(db)


@router.get("", response_model=PaginatedResponse)
def list_employees(
    service: Annotated[EmployeeService, Depends(get_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    search: Annotated[str | None, Query()] = None,
    country: Annotated[str | None, Query()] = None,
    department: Annotated[str | None, Query()] = None,
    job_title: Annotated[str | None, Query()] = None,
    status: Annotated[str, Query(pattern="^(active|inactive|all)$")] = "active",
    sort_by: Annotated[str, Query()] = "id",
    sort_order: Annotated[str, Query(pattern="^(asc|desc)$")] = "asc",
):
    return service.list_employees(
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


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    service: Annotated[EmployeeService, Depends(get_service)],
):
    return service.get_employee(employee_id)


@router.post("", response_model=EmployeeResponse, status_code=201)
def create_employee(
    data: EmployeeCreate,
    service: Annotated[EmployeeService, Depends(get_service)],
):
    return service.create_employee(data)


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    data: EmployeeUpdate,
    service: Annotated[EmployeeService, Depends(get_service)],
):
    return service.update_employee(employee_id, data)


@router.post("/{employee_id}/offboard", response_model=EmployeeResponse)
def offboard_employee(
    employee_id: int,
    data: EmployeeOffboard,
    service: Annotated[EmployeeService, Depends(get_service)],
):
    return service.offboard_employee(employee_id, data)


@router.post("/{employee_id}/rehire", response_model=EmployeeResponse)
def rehire_employee(
    employee_id: int,
    service: Annotated[EmployeeService, Depends(get_service)],
):
    return service.rehire_employee(employee_id)
