"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.config import get_settings
from src.core.database import create_tables
from src.core.logging import setup_logging
from src.core.exceptions import StudHelperException

# Import routers
from src.auth.router import router as auth_router
from src.documents.router import router as documents_router
from src.rag.router import router as rag_router
from src.ai.router import router as ai_router
from src.usage.router import router as usage_router

# Setup
settings = get_settings()
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting StudHelper AI Backend")
    await create_tables()
    logger.info("Database tables created/verified")
    
    # Ensure default user exists for single-user mode
    try:
        from src.core.database import get_db
        from src.auth.service import AuthService
        
        async with get_db() as db:
            auth_service = AuthService(db)
            user = await auth_service.get_user_by_email("default@studhelper.local")
            if not user:
                await auth_service.create_user(
                    email="default@studhelper.local",
                    username="default_user",
                    password="default_password_change_me",
                )
                logger.info("Created default user for single-user mode")
    except Exception as e:
        logger.error(f"Failed to create default user: {e}")
    
    logger.info("StudHelper AI Backend startup complete")
    
    yield
    
    # Shutdown
    logger.info("StudHelper AI Backend shutting down")


# Create FastAPI app
app = FastAPI(
    title="StudHelper AI Backend",
    description="AI-powered study assistant with document processing and RAG",
    version="2.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(StudHelperException)
async def studhelper_exception_handler(request: Request, exc: StudHelperException):
    """Handle custom StudHelper exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "status_code": exc.status_code,
            "details": exc.details,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error" if settings.is_production else str(exc),
            "status_code": 500,
        },
    )


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "StudHelper AI Backend",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "StudHelper AI Backend",
        "version": "2.0.0",
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
    }


# Include routers
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

app.include_router(
    documents_router,
    prefix="/api/v1/documents",
    tags=["Documents"],
)

app.include_router(
    rag_router,
    prefix="/api/v1/rag",
    tags=["RAG"],
)

app.include_router(
    ai_router,
    prefix="/api/v1/ai",
    tags=["AI"],
)

app.include_router(
    usage_router,
    prefix="/api/v1/usage",
    tags=["Usage"],
)


# Development middleware
if settings.DEBUG:
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all requests in debug mode."""
        logger.debug(f"{request.method} {request.url}")
        response = await call_next(request)
        logger.debug(f"Response: {response.status_code}")
        return response


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )


