from fastapi import Request, Response, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import uuid
import structlog
from typing import Callable

from app.core.security import decode_access_token
from app.core.config import settings

logger = structlog.get_logger()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Start timer
        start_time = time.time()
        
        # Log request
        logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown")
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            "Request completed",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time=round(process_time, 4)
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for certain paths
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        current_time = time.time()
        
        # Clean up old entries
        self.clients = {
            ip: calls for ip, calls in self.clients.items()
            if current_time - calls[0] < self.period
        }
        
        # Check rate limit
        if client_ip in self.clients:
            calls_list = self.clients[client_ip]
            # Remove old calls
            calls_list = [call_time for call_time in calls_list if current_time - call_time < self.period]
            
            if len(calls_list) >= self.calls:
                logger.warning("Rate limit exceeded", client_ip=client_ip)
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"}
                )
            
            calls_list.append(current_time)
            self.clients[client_ip] = calls_list
        else:
            self.clients[client_ip] = [current_time]
        
        return await call_next(request)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Add Content Security Policy
        if not settings.DEBUG:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "connect-src 'self'"
            )
        
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for global error handling"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Log the error
            logger.error(
                "Unhandled exception",
                error=str(e),
                error_type=type(e).__name__,
                request_id=getattr(request.state, 'request_id', 'unknown'),
                method=request.method,
                url=str(request.url)
            )
            
            # Return generic error response
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "request_id": getattr(request.state, 'request_id', 'unknown')
                }
            )

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for authentication (optional - can be handled in dependencies)"""
    
    def __init__(self, app, skip_paths: list = None):
        super().__init__(app)
        self.skip_paths = skip_paths or [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/auth/login",
            "/api/auth/register",
            "/"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip authentication for certain paths
        if any(request.url.path.startswith(path) for path in self.skip_paths):
            return await call_next(request)
        
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"}
            )
        
        try:
            # Extract token
            token = auth_header.split(" ")[1]
            
            # Decode token (this would validate the token)
            payload = decode_access_token(token)
            
            # Add user info to request state
            request.state.user_id = payload.get("user_id")
            request.state.user_role = payload.get("role")
            
        except Exception as e:
            logger.warning("Authentication failed", error=str(e))
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid authentication token"}
            )
        
        return await call_next(request)

class CORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware (alternative to FastAPI's built-in)"""
    
    def __init__(self, app, allow_origins: list = None, allow_methods: list = None):
        super().__init__(app)
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Max-Age"] = "86400"
            return response
        
        # Process request
        response = await call_next(request)
        
        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        
        return response
