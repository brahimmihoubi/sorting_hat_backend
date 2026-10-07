import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api import api_router
from app.core.config import settings

# Configure structured application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("sdg_sorting_hat")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    description="REST API backend for SDG Sorting Hat questionnaire and house sorting experience.",
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1|0\.0\.0\.0)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include main API router
app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up SDG Sorting Hat API backend...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database engine configured: SQLite ({settings.DATABASE_URL})")


@app.get("/health", tags=["Health"])
@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify backend operational status."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "scoring_version": settings.SCORING_VERSION,
        "database": "sqlite",
    }


@app.get("/docs", include_in_schema=False)
@app.get("/redoc", include_in_schema=False)
def redirect_to_swagger():
    """Convenience redirect from /docs to /api/docs."""
    return RedirectResponse(url=f"{settings.API_V1_STR}/docs")


@app.get("/", tags=["Root"])
def root():
    """Root endpoint pointing to Swagger docs."""
    return {
        "message": "Welcome to SDG Sorting Hat API",
        "docs": f"{settings.API_V1_STR}/docs",
        "health": "/health",
    }
