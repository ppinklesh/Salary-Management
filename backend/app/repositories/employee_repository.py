from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.employee import Employee


class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, employee_id: int) -> Employee | None:
        return self.db.get(Employee, employee_id)

    def get_by_email(self, email: str) -> Employee | None:
        stmt = select(Employee).where(Employee.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        country: str | None = None,
        department: str | None = None,
        job_title: str | None = None,
        sort_by: str = "id",
        sort_order: str = "asc",
    ) -> tuple[list[Employee], int]:
        stmt = select(Employee)
        count_stmt = select(func.count(Employee.id))

        if search:
            search_filter = Employee.full_name.ilike(f"%{search}%")
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        if country:
            stmt = stmt.where(Employee.country == country)
            count_stmt = count_stmt.where(Employee.country == country)

        if department:
            stmt = stmt.where(Employee.department == department)
            count_stmt = count_stmt.where(Employee.department == department)

        if job_title:
            stmt = stmt.where(Employee.job_title == job_title)
            count_stmt = count_stmt.where(Employee.job_title == job_title)

        allowed_sort_fields = {
            "id", "full_name", "email", "job_title", "department",
            "country", "salary", "hire_date", "created_at",
        }
        if sort_by not in allowed_sort_fields:
            sort_by = "id"

        sort_column = getattr(Employee, sort_by)
        if sort_order == "desc":
            sort_column = sort_column.desc()

        stmt = stmt.order_by(sort_column)
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        total = self.db.execute(count_stmt).scalar() or 0
        employees = list(self.db.execute(stmt).scalars().all())

        return employees, total

    def create(self, employee: Employee) -> Employee:
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)
        return employee

    def update(self, employee: Employee, data: dict) -> Employee:
        for key, value in data.items():
            if value is not None:
                setattr(employee, key, value)
        self.db.commit()
        self.db.refresh(employee)
        return employee

    def delete(self, employee: Employee) -> None:
        self.db.delete(employee)
        self.db.commit()

    def get_salary_summary(self) -> dict:
        stmt = select(
            func.min(Employee.salary).label("min_salary"),
            func.max(Employee.salary).label("max_salary"),
            func.avg(Employee.salary).label("avg_salary"),
            func.count(Employee.id).label("total_employees"),
        )
        result = self.db.execute(stmt).one()

        median = self._get_median_salary()

        return {
            "min_salary": round(float(result.min_salary or 0), 2),
            "max_salary": round(float(result.max_salary or 0), 2),
            "avg_salary": round(float(result.avg_salary or 0), 2),
            "median_salary": round(float(median), 2),
            "total_employees": result.total_employees,
        }

    def _get_median_salary(self) -> float:
        count_stmt = select(func.count(Employee.id))
        total = self.db.execute(count_stmt).scalar() or 0

        if total == 0:
            return 0.0

        mid = total // 2
        stmt = select(Employee.salary).order_by(Employee.salary)

        if total % 2 == 1:
            stmt = stmt.offset(mid).limit(1)
            return float(self.db.execute(stmt).scalar() or 0)
        else:
            stmt = stmt.offset(mid - 1).limit(2)
            values = [float(row[0]) for row in self.db.execute(stmt).all()]
            return sum(values) / 2

    def get_stats_by_country(self) -> list[dict]:
        stmt = (
            select(
                Employee.country,
                func.min(Employee.salary).label("min_salary"),
                func.max(Employee.salary).label("max_salary"),
                func.avg(Employee.salary).label("avg_salary"),
                func.count(Employee.id).label("employee_count"),
            )
            .group_by(Employee.country)
            .order_by(func.count(Employee.id).desc())
        )
        results = self.db.execute(stmt).all()
        return [
            {
                "country": row.country,
                "min_salary": round(float(row.min_salary), 2),
                "max_salary": round(float(row.max_salary), 2),
                "avg_salary": round(float(row.avg_salary), 2),
                "employee_count": row.employee_count,
            }
            for row in results
        ]

    def get_stats_by_job_title(self, country: str | None = None) -> list[dict]:
        stmt = select(
            Employee.job_title,
            func.avg(Employee.salary).label("avg_salary"),
            func.min(Employee.salary).label("min_salary"),
            func.max(Employee.salary).label("max_salary"),
            func.count(Employee.id).label("employee_count"),
        )

        if country:
            stmt = stmt.where(Employee.country == country)

        stmt = stmt.group_by(Employee.job_title).order_by(
            func.avg(Employee.salary).desc()
        )
        results = self.db.execute(stmt).all()
        return [
            {
                "job_title": row.job_title,
                "avg_salary": round(float(row.avg_salary), 2),
                "min_salary": round(float(row.min_salary), 2),
                "max_salary": round(float(row.max_salary), 2),
                "employee_count": row.employee_count,
            }
            for row in results
        ]

    def get_stats_by_department(self) -> list[dict]:
        stmt = (
            select(
                Employee.department,
                func.min(Employee.salary).label("min_salary"),
                func.max(Employee.salary).label("max_salary"),
                func.avg(Employee.salary).label("avg_salary"),
                func.count(Employee.id).label("employee_count"),
            )
            .group_by(Employee.department)
            .order_by(func.avg(Employee.salary).desc())
        )
        results = self.db.execute(stmt).all()
        return [
            {
                "department": row.department,
                "min_salary": round(float(row.min_salary), 2),
                "max_salary": round(float(row.max_salary), 2),
                "avg_salary": round(float(row.avg_salary), 2),
                "employee_count": row.employee_count,
            }
            for row in results
        ]

    def get_distinct_countries(self) -> list[str]:
        stmt = select(Employee.country).distinct().order_by(Employee.country)
        return [row[0] for row in self.db.execute(stmt).all()]

    def get_distinct_departments(self) -> list[str]:
        stmt = select(Employee.department).distinct().order_by(Employee.department)
        return [row[0] for row in self.db.execute(stmt).all()]

    def get_distinct_job_titles(self) -> list[str]:
        stmt = select(Employee.job_title).distinct().order_by(Employee.job_title)
        return [row[0] for row in self.db.execute(stmt).all()]
