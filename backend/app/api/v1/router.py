from fastapi import APIRouter

from app.api.v1.endpoints.employees import router as employees_router
from app.api.v1.endpoints.filters import router as filters_router
from app.api.v1.endpoints.insights import router as insights_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(employees_router)
api_router.include_router(insights_router)
api_router.include_router(filters_router)
