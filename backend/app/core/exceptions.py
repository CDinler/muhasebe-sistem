"""Custom exception classes for the application"""

class AppException(Exception):
    """Base exception for application errors"""
    def __init__(self, message: str, code: str = "APP_ERROR", details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class BusinessException(AppException):
    """Exception for business logic violations"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "BUSINESS_ERROR", details)


class NotFoundException(AppException):
    """Exception for resource not found errors"""
    def __init__(self, resource: str, identifier: any):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, "NOT_FOUND", {"resource": resource, "identifier": identifier})


class ValidationException(AppException):
    """Exception for validation errors"""
    def __init__(self, message: str, field: str = None, details: dict = None):
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(message, "VALIDATION_ERROR", details)


class UnauthorizedException(AppException):
    """Exception for unauthorized access"""
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, "UNAUTHORIZED")


class DatabaseException(AppException):
    """Exception for database errors"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "DATABASE_ERROR", details)
