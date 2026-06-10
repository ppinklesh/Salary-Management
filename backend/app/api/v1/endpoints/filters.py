from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.employee_repository import EmployeeRepository

router = APIRouter(prefix="/filters", tags=["filters"])


@router.get("/countries", response_model=list[str])
def get_countries(db: Session = Depends(get_db)):
    repo = EmployeeRepository(db)
    return repo.get_distinct_countries()


@router.get("/departments", response_model=list[str])
def get_departments(db: Session = Depends(get_db)):
    repo = EmployeeRepository(db)
    return repo.get_distinct_departments()


@router.get("/job-titles", response_model=list[str])
def get_job_titles(db: Session = Depends(get_db)):
    repo = EmployeeRepository(db)
    return repo.get_distinct_job_titles()
