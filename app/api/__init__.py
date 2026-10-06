from fastapi import APIRouter

from app.api.admin import router as admin_router
from app.api.admin_auth import router as admin_auth_router
from app.api.departments import router as departments_router
from app.api.participants import router as participants_router
from app.api.questions import router as questions_router
from app.api.results import router as results_router
from app.api.sorting import router as sorting_router

api_router = APIRouter(prefix="/api")

api_router.include_router(departments_router)
api_router.include_router(questions_router)
api_router.include_router(participants_router)
api_router.include_router(sorting_router)
api_router.include_router(results_router)
api_router.include_router(admin_auth_router)
api_router.include_router(admin_router)
