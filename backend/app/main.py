"""
FastAPI application entry point.
Production-ready API with CORS, error handling, and structured logging.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.database import close_db, engine, Base
from app.core.exceptions import EKYCBaseException

# Import all models to register them with Base
from app.models import api_client, customer, verification_result, document
from app.models import beneficial_owner, audit_log, verification_log, workflow

# Setup logging before anything else
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Starting E-KYC Check API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Provider: {settings.verification_provider}")
    
    # Create database tables
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    
    yield
    logger.info("Shutting down E-KYC Check API")
    close_db()


# Create FastAPI application
app = FastAPI(
    title="E-KYC Check API",
    description="Compliance-as-a-Service platform for Nigerian financial institutions",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Global exception handlers
@app.exception_handler(EKYCBaseException)
async def ekyc_exception_handler(request: Request, exc: EKYCBaseException):
    """Handle custom E-KYC exceptions."""
    logger.warning(
        f"E-KYC exception: {exc.error_code} - {exc.message}",
        extra={"error_code": exc.error_code, "status_code": exc.status_code}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Invalid request data",
            "details": {"errors": exc.errors()}
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    # Don't leak internal errors in production
    if settings.is_production:
        message = "An internal error occurred"
    else:
        message = str(exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_ERROR",
            "message": message
        }
    )


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for load balancers."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0"
    }


@app.get("/", tags=["System"])
async def root():
    """Root endpoint."""
    return {
        "service": "E-KYC Check API",
        "version": "1.0.0",
        "status": "operational"
    }


# Import and include routers
from app.api.external.v1 import verification, reports

app.include_router(verification.router, prefix="/api/v1", tags=["Verification"])
app.include_router(reports.router, prefix="/api/v1", tags=["Reports"])

# TODO: Internal routers for workflow and client management
# from app.api.internal import workflow, clients
# app.include_router(workflow.router, prefix="/internal", tags=["Workflow"])
# app.include_router(clients.router, prefix="/internal", tags=["Clients"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level=settings.log_level.lower()
    )
