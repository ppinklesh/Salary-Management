from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.employee_repository import EmployeeRepository


class InsightsService:
    def __init__(self, db: Session):
        self.repo = EmployeeRepository(db)

    def get_summary(self) -> dict:
        return self.repo.get_salary_summary()

    def get_by_country(self) -> list[dict]:
        return self.repo.get_stats_by_country()

    def get_by_job_title(self, country: str | None = None) -> list[dict]:
        return self.repo.get_stats_by_job_title(country=country)

    def get_by_department(self) -> list[dict]:
        return self.repo.get_stats_by_department()
