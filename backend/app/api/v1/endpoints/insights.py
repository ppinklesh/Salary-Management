from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.employee import (
    CountrySalaryStats,
    DepartmentSalaryStats,
    JobTitleSalaryStats,
    SalarySummary,
)
from app.services.insights_service import InsightsService

router = APIRouter(prefix="/insights", tags=["insights"])


def get_service(
    db: Annotated[Session, Depends(get_db)],
) -> InsightsService:
    return InsightsService(db)


@router.get("/summary", response_model=SalarySummary)
def get_salary_summary(
    service: Annotated[InsightsService, Depends(get_service)],
):
    return service.get_summary()


@router.get("/by-country", response_model=list[CountrySalaryStats])
def get_stats_by_country(
    service: Annotated[InsightsService, Depends(get_service)],
):
    return service.get_by_country()


@router.get("/by-job-title", response_model=list[JobTitleSalaryStats])
def get_stats_by_job_title(
    service: Annotated[InsightsService, Depends(get_service)],
    country: Annotated[str | None, Query()] = None,
):
    return service.get_by_job_title(country=country)


@router.get("/by-department", response_model=list[DepartmentSalaryStats])
def get_stats_by_department(
    service: Annotated[InsightsService, Depends(get_service)],
):
    return service.get_by_department()
