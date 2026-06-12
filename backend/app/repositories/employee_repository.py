from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.currency import local_to_usd
from app.models.employee import Employee, Salary


class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _apply_employment_status(
        stmt,
        count_stmt,
        status: str,
    ):
        if status == "active":
            condition = Employee.exit_date.is_(None)
            return stmt.where(condition), count_stmt.where(condition)
        if status == "inactive":
            condition = Employee.exit_date.isnot(None)
            return stmt.where(condition), count_stmt.where(condition)
        return stmt, count_stmt

    def get_by_id(self, employee_id: int) -> Employee | None:
        stmt = (
            select(Employee)
            .options(joinedload(Employee.salaries))
            .where(Employee.id == employee_id)
        )
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def get_by_email(self, email: str) -> Employee | None:
        stmt = select(Employee).where(Employee.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_active_by_email(self, email: str) -> Employee | None:
        stmt = select(Employee).where(
            Employee.email == email,
            Employee.exit_date.is_(None),
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_inactive_by_email(self, email: str) -> list[Employee]:
        stmt = select(Employee).where(
            Employee.email == email,
            Employee.exit_date.isnot(None),
        )
        return list(self.db.execute(stmt).scalars().all())

    def list(
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
    ) -> tuple[list[Employee], int]:
        stmt = select(Employee).options(joinedload(Employee.salaries))
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

        stmt, count_stmt = self._apply_employment_status(stmt, count_stmt, status)

        allowed_sort_fields = {
            "id", "full_name", "email", "job_title", "department",
            "country", "hire_date", "exit_date", "created_at",
        }
        if sort_by == "salary":
            latest_salary = (
                select(
                    Salary.employee_id,
                    Salary.amount,
                    func.row_number()
                    .over(partition_by=Salary.employee_id, order_by=Salary.effective_date.desc())
                    .label("rn"),
                )
                .subquery()
            )
            latest = select(latest_salary.c.employee_id, latest_salary.c.amount).where(
                latest_salary.c.rn == 1
            ).subquery()
            stmt = stmt.outerjoin(latest, Employee.id == latest.c.employee_id)
            sort_column = latest.c.amount
            if sort_order == "desc":
                sort_column = sort_column.desc()
            stmt = stmt.order_by(sort_column)
        else:
            if sort_by not in allowed_sort_fields:
                sort_by = "id"
            sort_column = getattr(Employee, sort_by)
            if sort_order == "desc":
                sort_column = sort_column.desc()
            stmt = stmt.order_by(sort_column)

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        total = self.db.execute(count_stmt).scalar() or 0
        employees = list(self.db.execute(stmt).unique().scalars().all())

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

    def offboard(
        self,
        employee: Employee,
        exit_date,
        exit_reason: str,
    ) -> Employee:
        employee.exit_date = exit_date
        employee.exit_reason = exit_reason
        self.db.commit()
        self.db.refresh(employee)
        return employee

    def rehire(self, employee: Employee) -> Employee:
        employee.exit_date = None
        employee.exit_reason = None
        self.db.commit()
        self.db.refresh(employee)
        return employee

    def add_salary(self, salary: Salary) -> Salary:
        self.db.add(salary)
        self.db.commit()
        self.db.refresh(salary)
        return salary

    def get_salary_summary(self) -> dict:
        usd_amounts = self._active_salary_amounts_usd()
        if not usd_amounts:
            return {
                "min_salary": 0.0,
                "max_salary": 0.0,
                "avg_salary": 0.0,
                "median_salary": 0.0,
                "total_employees": 0,
            }

        usd_amounts.sort()
        total = len(usd_amounts)
        mid = total // 2
        if total % 2 == 1:
            median = usd_amounts[mid]
        else:
            median = (usd_amounts[mid - 1] + usd_amounts[mid]) / 2

        return {
            "min_salary": round(min(usd_amounts), 2),
            "max_salary": round(max(usd_amounts), 2),
            "avg_salary": round(sum(usd_amounts) / total, 2),
            "median_salary": round(median, 2),
            "total_employees": total,
        }

    def _active_salary_amounts_usd(self) -> list[float]:
        latest = self._active_employee_latest_salaries()
        stmt = select(latest.c.amount, latest.c.currency)
        rows = self.db.execute(stmt).all()
        return [local_to_usd(float(row.amount), row.currency) for row in rows]

    def _latest_salary_subquery(self):
        """Subquery that returns the most recent salary per employee."""
        ranked = (
            select(
                Salary.employee_id,
                Salary.amount,
                Salary.currency,
                Salary.employment_type,
                func.row_number()
                .over(
                    partition_by=Salary.employee_id,
                    order_by=Salary.effective_date.desc(),
                )
                .label("rn"),
            )
            .subquery()
        )
        return (
            select(
                ranked.c.employee_id,
                ranked.c.amount,
                ranked.c.currency,
                ranked.c.employment_type,
            )
            .where(ranked.c.rn == 1)
            .subquery()
        )

    def _active_employee_latest_salaries(self):
        latest = self._latest_salary_subquery()
        return (
            select(
                latest.c.employee_id,
                latest.c.amount,
                latest.c.currency,
                latest.c.employment_type,
            )
            .join(Employee, Employee.id == latest.c.employee_id)
            .where(Employee.exit_date.is_(None))
            .subquery()
        )

    def _get_median_salary(self, latest_sub) -> float:
        count_stmt = select(func.count(latest_sub.c.employee_id))
        total = self.db.execute(count_stmt).scalar() or 0

        if total == 0:
            return 0.0

        mid = total // 2
        stmt = select(latest_sub.c.amount).order_by(latest_sub.c.amount)

        if total % 2 == 1:
            stmt = stmt.offset(mid).limit(1)
            return float(self.db.execute(stmt).scalar() or 0)
        else:
            stmt = stmt.offset(mid - 1).limit(2)
            values = [float(row[0]) for row in self.db.execute(stmt).all()]
            return sum(values) / 2

    def get_stats_by_country(self) -> list[dict]:
        latest = self._active_employee_latest_salaries()
        stmt = (
            select(
                Employee.country,
                func.min(latest.c.amount).label("min_salary"),
                func.max(latest.c.amount).label("max_salary"),
                func.avg(latest.c.amount).label("avg_salary"),
                func.count(latest.c.employee_id).label("employee_count"),
            )
            .join(latest, Employee.id == latest.c.employee_id)
            .where(Employee.exit_date.is_(None))
            .group_by(Employee.country)
            .order_by(func.count(latest.c.employee_id).desc())
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
        latest = self._active_employee_latest_salaries()
        stmt = (
            select(
                Employee.job_title,
                latest.c.amount,
                latest.c.currency,
            )
            .join(latest, Employee.id == latest.c.employee_id)
            .where(Employee.exit_date.is_(None))
        )

        if country:
            stmt = stmt.where(Employee.country == country)

        rows = self.db.execute(stmt).all()
        grouped: dict[str, list[float]] = {}
        for row in rows:
            usd = local_to_usd(float(row.amount), row.currency)
            grouped.setdefault(row.job_title, []).append(usd)

        return [
            {
                "job_title": title,
                "avg_salary": round(sum(amounts) / len(amounts), 2),
                "min_salary": round(min(amounts), 2),
                "max_salary": round(max(amounts), 2),
                "employee_count": len(amounts),
            }
            for title, amounts in sorted(
                grouped.items(), key=lambda item: sum(item[1]) / len(item[1]), reverse=True
            )
        ]

    def get_stats_by_department(self) -> list[dict]:
        latest = self._active_employee_latest_salaries()
        stmt = (
            select(
                Employee.department,
                latest.c.amount,
                latest.c.currency,
            )
            .join(latest, Employee.id == latest.c.employee_id)
            .where(Employee.exit_date.is_(None))
        )
        rows = self.db.execute(stmt).all()
        grouped: dict[str, list[float]] = {}
        for row in rows:
            usd = local_to_usd(float(row.amount), row.currency)
            grouped.setdefault(row.department, []).append(usd)

        return [
            {
                "department": department,
                "min_salary": round(min(amounts), 2),
                "max_salary": round(max(amounts), 2),
                "avg_salary": round(sum(amounts) / len(amounts), 2),
                "employee_count": len(amounts),
            }
            for department, amounts in sorted(
                grouped.items(), key=lambda item: sum(item[1]) / len(item[1]), reverse=True
            )
        ]

    def get_distinct_countries(self) -> list[str]:
        stmt = (
            select(Employee.country)
            .where(Employee.exit_date.is_(None))
            .distinct()
            .order_by(Employee.country)
        )
        return [row[0] for row in self.db.execute(stmt).all()]

    def get_distinct_departments(self) -> list[str]:
        stmt = (
            select(Employee.department)
            .where(Employee.exit_date.is_(None))
            .distinct()
            .order_by(Employee.department)
        )
        return [row[0] for row in self.db.execute(stmt).all()]

    def get_distinct_job_titles(self) -> list[str]:
        stmt = (
            select(Employee.job_title)
            .where(Employee.exit_date.is_(None))
            .distinct()
            .order_by(Employee.job_title)
        )
        return [row[0] for row in self.db.execute(stmt).all()]
