from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, Numeric, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    job_title: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    exit_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    exit_reason: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )

    salaries: Mapped[list["Salary"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan", order_by="Salary.effective_date.desc()"
    )

    __table_args__ = (
        Index("ix_employees_full_name", "full_name"),
        Index("ix_employees_country", "country"),
        Index("ix_employees_job_title", "job_title"),
        Index("ix_employees_department", "department"),
        Index(
            "uq_employees_email_active",
            "email",
            unique=True,
            sqlite_where=text("exit_date IS NULL"),
        ),
    )

    @property
    def is_active(self) -> bool:
        return self.exit_date is None

    @property
    def current_salary(self) -> "Salary | None":
        return self.salaries[0] if self.salaries else None

    def __repr__(self) -> str:
        return f"<Employee(id={self.id}, name='{self.full_name}', country='{self.country}')>"


class Salary(Base):
    __tablename__ = "salaries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    employment_type: Mapped[str] = mapped_column(String(20), nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    employee: Mapped[Employee] = relationship(back_populates="salaries")

    __table_args__ = (
        Index("ix_salaries_employee_id", "employee_id"),
        Index("ix_salaries_effective_date", "effective_date"),
    )

    def __repr__(self) -> str:
        return f"<Salary(id={self.id}, employee_id={self.employee_id}, amount={self.amount})>"
