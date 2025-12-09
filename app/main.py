import os
import logging
from typing import Optional
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import Base, engine
from app.routers.talent import router as talent_router
from app.routers.projects import router as project_router
from app.routers.project_outcomes import router as outcome_router
from app.routers import matching
from app.routers.auth import router as auth_router
from app.routers.dashboard import router as dashboard_router
from app.routers.payments import router as payments_router



from app.security.firebase import init_firebase
from app.middleware.rate_limit import RateLimitMiddleware

from fastapi import FastAPI
from app.routers import auth

app = FastAPI()

app.include_router(auth.router)

# ---------------------------------------------------------
# Create the FastAPI app (ONLY ONCE)
# ---------------------------------------------------------
app = FastAPI(
    title="Somahorse Nexus API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ---------------------------------------------------------
# Add middleware
# ---------------------------------------------------------
app.add_middleware(RateLimitMiddleware)

# ---------------------------------------------------------
# Include routers
# ---------------------------------------------------------
app.include_router(talent_router)
app.include_router(project_router)
app.include_router(outcome_router)
app.include_router(matching.router)
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(payments_router)

# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("somahorse-backend")


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

from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Somahorse Nexus API",
        version="1.0.0",
        description="API documentation for Somahorse",
        routes=app.routes,
    )
    
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
from app.routers import matching
app.include_router(matching.router)
