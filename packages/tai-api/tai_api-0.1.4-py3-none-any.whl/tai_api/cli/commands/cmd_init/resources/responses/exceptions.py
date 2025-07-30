"""
Excepciones personalizadas para tai-api.

Este módulo define excepciones específicas que se pueden lanzar en los endpoints
y que serán manejadas por el sistema de respuestas.
"""

from typing import Any, Optional, Dict
from enum import Enum

class ErrorCode(str, Enum):
    """Códigos de error estandardizados."""
    # Errores de validación
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    
    # Errores de base de datos
    DATABASE_ERROR = "DATABASE_ERROR"
    RECORD_NOT_FOUND = "RECORD_NOT_FOUND"
    DUPLICATE_RECORD = "DUPLICATE_RECORD"
    FOREIGN_KEY_VIOLATION = "FOREIGN_KEY_VIOLATION"
    
    # Errores de negocio
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Errores del sistema
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"

class APIException(Exception):
    """Excepción base para API"""
    
    def __init__(
        self, 
        message: str, 
        error_code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
        field: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details
        self.field = field
        super().__init__(message)

class ValidationException(APIException):
    """Excepción para errores de validación."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            field=field
        )

class RecordNotFoundException(APIException):
    """Excepción para cuando no se encuentra un registro."""
    
    def __init__(self, resource: str = "Registro"):
        super().__init__(
            message=f"{resource} no encontrado",
            error_code=ErrorCode.RECORD_NOT_FOUND
        )

class DatabaseException(APIException):
    """Excepción para errores de base de datos."""
    
    def __init__(self, message: str = "Error en la base de datos"):
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_ERROR
        )

class DuplicateRecordException(APIException):
    """Excepción para registros duplicados."""
    
    def __init__(self, message: str = "El registro ya existe"):
        super().__init__(
            message=message,
            error_code=ErrorCode.DUPLICATE_RECORD
        )

class ForeignKeyViolationException(APIException):
    """Excepción para violaciones de clave foránea."""
    
    def __init__(self, message: str = "Violación de clave foránea"):
        super().__init__(
            message=message,
            error_code=ErrorCode.FOREIGN_KEY_VIOLATION
        )

class BusinessRuleViolationException(APIException):
    """Excepción para violaciones de reglas de negocio."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code=ErrorCode.BUSINESS_RULE_VIOLATION
        )
