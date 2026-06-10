from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator


class EmployeeBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., max_length=255)
    job_title: str = Field(..., min_length=1, max_length=100)
    department: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=1, max_length=100)
    salary: float = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    employment_type: str = Field(..., min_length=1, max_length=20)
    hire_date: date

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.lower().strip()

    @field_validator("employment_type")
    @classmethod
    def validate_employment_type(cls, v: str) -> str:
        allowed = {"full_time", "part_time", "contract"}
        if v not in allowed:
            raise ValueError(f"Must be one of: {', '.join(sorted(allowed))}")
        return v

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        return v.upper().strip()


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=255)
    email: str | None = Field(None, max_length=255)
    job_title: str | None = Field(None, min_length=1, max_length=100)
    department: str | None = Field(None, min_length=1, max_length=100)
    country: str | None = Field(None, min_length=1, max_length=100)
    salary: float | None = Field(None, gt=0)
    currency: str | None = Field(None, min_length=3, max_length=3)
    employment_type: str | None = Field(None, min_length=1, max_length=20)
    hire_date: date | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.lower().strip()

    @field_validator("employment_type")
    @classmethod
    def validate_employment_type(cls, v: str | None) -> str | None:
        if v is None:
            return v
        allowed = {"full_time", "part_time", "contract"}
        if v not in allowed:
            raise ValueError(f"Must be one of: {', '.join(sorted(allowed))}")
        return v

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return v.upper().strip()


class EmployeeResponse(BaseModel):
    id: int
    full_name: str
    email: str
    job_title: str
    department: str
    country: str
    salary: float
    currency: str
    employment_type: str
    hire_date: date
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    data: list[EmployeeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SalarySummary(BaseModel):
    min_salary: float
    max_salary: float
    avg_salary: float
    median_salary: float
    total_employees: int


class CountrySalaryStats(BaseModel):
    country: str
    min_salary: float
    max_salary: float
    avg_salary: float
    employee_count: int


class JobTitleSalaryStats(BaseModel):
    job_title: str
    avg_salary: float
    min_salary: float
    max_salary: float
    employee_count: int


class DepartmentSalaryStats(BaseModel):
    department: str
    min_salary: float
    max_salary: float
    avg_salary: float
    employee_count: int
