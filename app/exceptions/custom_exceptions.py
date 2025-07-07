from fastapi import HTTPException
from typing import Optional, Dict, Any


class SMSException(Exception):
    """Base exception for SMS application."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)
    
    @property
    def detail(self) -> str:
        return self.message


class ValidationException(SMSException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details
        )


class AuthenticationException(SMSException):
    """Exception for authentication errors."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationException(SMSException):
    """Exception for authorization errors."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR"
        )


class NotFoundException(SMSException):
    """Exception for resource not found errors."""
    
    def __init__(self, resource: str, identifier: str = ""):
        message = f"{resource} not found"
        if identifier:
            message += f" with identifier: {identifier}"
        
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND"
        )


class ConflictException(SMSException):
    """Exception for conflict errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT_ERROR",
            details=details
        )


class BusinessLogicException(SMSException):
    """Exception for business logic errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="BUSINESS_LOGIC_ERROR",
            details=details
        )


class DatabaseException(SMSException):
    """Exception for database errors."""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR"
        )


class ExternalServiceException(SMSException):
    """Exception for external service errors."""
    
    def __init__(self, service_name: str, message: str = "External service error"):
        super().__init__(
            message=f"{service_name}: {message}",
            status_code=503,
            error_code="EXTERNAL_SERVICE_ERROR"
        )


# User-specific exceptions
class UserNotFoundException(NotFoundException):
    """Exception for user not found."""
    
    def __init__(self, user_id: str = ""):
        super().__init__("User", user_id)


class UserAlreadyExistsException(ConflictException):
    """Exception for user already exists."""
    
    def __init__(self, email: str):
        super().__init__(f"User with email {email} already exists")


class InvalidCredentialsException(AuthenticationException):
    """Exception for invalid credentials."""
    
    def __init__(self):
        super().__init__("Invalid email or password")


class InactiveUserException(AuthenticationException):
    """Exception for inactive user."""
    
    def __init__(self):
        super().__init__("User account is inactive")


# Quiz-specific exceptions
class QuizNotFoundException(NotFoundException):
    """Exception for quiz not found."""
    
    def __init__(self, quiz_id: str = ""):
        super().__init__("Quiz", quiz_id)


class QuizNotPublishedException(BusinessLogicException):
    """Exception for quiz not published."""
    
    def __init__(self):
        super().__init__("Quiz is not published")


class QuizAttemptLimitExceededException(BusinessLogicException):
    """Exception for quiz attempt limit exceeded."""
    
    def __init__(self, max_attempts: int):
        super().__init__(f"Maximum number of attempts ({max_attempts}) exceeded")


class QuizAlreadyCompletedException(BusinessLogicException):
    """Exception for quiz already completed."""
    
    def __init__(self):
        super().__init__("Quiz has already been completed")


class QuizTimeExpiredException(BusinessLogicException):
    """Exception for quiz time expired."""
    
    def __init__(self):
        super().__init__("Quiz time limit has expired")


# Class-specific exceptions
class ClassNotFoundException(NotFoundException):
    """Exception for class not found."""
    
    def __init__(self, class_id: str = ""):
        super().__init__("Class", class_id)


class StudentNotEnrolledException(BusinessLogicException):
    """Exception for student not enrolled in class."""
    
    def __init__(self):
        super().__init__("Student is not enrolled in this class")


class StudentAlreadyEnrolledException(ConflictException):
    """Exception for student already enrolled."""
    
    def __init__(self):
        super().__init__("Student is already enrolled in this class")


# Permission-specific exceptions
class InsufficientPermissionsException(AuthorizationException):
    """Exception for insufficient permissions."""
    
    def __init__(self, action: str):
        super().__init__(f"Insufficient permissions to {action}")


class RoleNotAllowedException(AuthorizationException):
    """Exception for role not allowed."""
    
    def __init__(self, role: str, action: str):
        super().__init__(f"Role '{role}' is not allowed to {action}")


# File upload exceptions
class FileUploadException(SMSException):
    """Exception for file upload errors."""
    
    def __init__(self, message: str = "File upload failed"):
        super().__init__(
            message=message,
            status_code=400,
            error_code="FILE_UPLOAD_ERROR"
        )


class InvalidFileTypeException(FileUploadException):
    """Exception for invalid file type."""
    
    def __init__(self, file_type: str, allowed_types: list):
        message = f"Invalid file type '{file_type}'. Allowed types: {', '.join(allowed_types)}"
        super().__init__(message)


class FileSizeExceededException(FileUploadException):
    """Exception for file size exceeded."""
    
    def __init__(self, size: int, max_size: int):
        message = f"File size ({size} bytes) exceeds maximum allowed size ({max_size} bytes)"
        super().__init__(message)
