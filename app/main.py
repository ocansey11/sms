from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import time
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.database import init_db
from app.api.routes import auth, admin, teacher, student, guardian, tenant
from app.exceptions.custom_exceptions import SMSException

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="School Management System API",
    description="A comprehensive school management system with FastAPI and PostgreSQL",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    # allow_origins=settings.CORS_ORIGINS,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handler
@app.exception_handler(SMSException)
async def sms_exception_handler(request: Request, exc: SMSException):
    logger.error("SMS Exception occurred", error=str(exc), status_code=exc.status_code)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": exc.error_code}
    )

# Request/Response logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host if request.client else "unknown"
    )
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=round(process_time, 4)
    )
    
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.ENV}

# # Initialize database on startup
# @app.on_event("startup")
# async def startup_event():
#     logger.info("Starting up SMS API", environment=settings.ENV)
#     await init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    logger.info("Starting up SMS API", environment=settings.ENV)
    await init_db()
    yield
    # Shutdown code (optional)
    logger.info("Shutting down SMS API")

app = FastAPI(lifespan=lifespan)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(teacher.router, prefix="/api/teacher", tags=["Teacher"])
app.include_router(student.router, prefix="/api/student", tags=["Student"])
app.include_router(guardian.router, prefix="/api/guardian", tags=["Guardian"])
app.include_router(tenant.router, prefix="/api/tenant", tags=["Tenant"])
# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "School Management System API",
        "version": "1.0.0",
        "environment": settings.ENV,
        "docs_url": "/docs" if settings.DEBUG else "Documentation disabled in production"
    }
