# app/main.py
import os
import logging
import time
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import APIKey, APIKeyIn, SecuritySchemeType
from fastapi.security import HTTPBearer
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import Base, engine
from app.routers.talent import router as talent_router
from app.routers.projects import router as project_router
from app.routers.project_outcomes import router as outcome_router

from app.security.firebase import init_firebase
from app.middleware.rate_limit import RateLimitMiddleware


app = FastAPI(
    title="Somahorse Nexus API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
app.include_router(matching.router)
app.add_middleware(RateLimitMiddleware)
# -------------------------
# Basic logging
# -------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("somahorse-backend")

# -------------------------
# App & config
# -------------------------
app = FastAPI(
    title="Somahorse Nexus API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Read CORS origin from env (set FRONTEND_URL to your frontend host in production)
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")

# -------------------------
# Middleware: CORS
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL] if FRONTEND_URL != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Simple request logging middleware (useful for staging)
# -------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f">>> {request.method} {request.url.path}")
    try:
        response = await call_next(request)
    except Exception as exc:
        # Let global exception handler deal with it
        raise
    process_time = (time.time() - start_time) * 1000
    logger.info(f"<<< {request.method} {request.url.path} completed_in={process_time:.2f}ms status={response.status_code}")
    response.headers["X-Process-Time-ms"] = str(f"{process_time:.2f}")
    return response

# -------------------------
# Startup: DB tables + Firebase init
# -------------------------
@app.on_event("startup")
def on_startup():
    # Create DB tables in dev; in prod use Alembic migrations
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ensured.")
    except Exception as e:
        logger.exception("Failed to create DB tables on startup: %s", e)

    # Initialize Firebase Admin SDK (optional in dev)
    try:
        init_firebase()
        logger.info("Firebase Admin initialized.")
    except Exception as e:
        # Don't hard-fail startup for local development; log warning
        logger.warning("Firebase initialization failed or not configured: %s", e)

# -------------------------
# OpenAPI / Swagger: add Bearer auth scheme
# -------------------------
# We'll add a "bearerAuth" scheme into the generated OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = app.openapi()
    # Add bearerAuth security scheme if not present
    security_scheme = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    if "securitySchemes" not in openapi_schema["components"]:
        openapi_schema["components"]["securitySchemes"] = {}
    openapi_schema["components"]["securitySchemes"]["bearerAuth"] = security_scheme

    # Optionally require bearerAuth globally for all endpoints in the docs UI (comment out if not)
    # openapi_schema["security"] = [{"bearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# -------------------------
# Global error handlers
# -------------------------
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "detail": exc.detail,
        },
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "detail": "Internal server error",
        },
    )

# -------------------------
# Health / metadata endpoints
# -------------------------
@app.get("/healthz", tags=["Health"])
def healthz():
    return {"status": "ok"}

@app.get("/", tags=["Health"])
def root():
    return {"message": "Somahorse Nexus API is running"}

# -------------------------
# Routers
# -------------------------
app.include_router(talent_router)
app.include_router(project_router)
app.include_router(outcome_router)
from app.routes import matching
app.include_router(matching.router)
