"""
Sistema de respuestas estandarizadas para tai-api.

Este módulo proporciona clases para manejar respuestas exitosas y de error
de manera consistente en toda la API.
"""

from typing import Any, Optional, Dict, List, Union, Generic, TypeVar
from pydantic import BaseModel
from enum import Enum

T = TypeVar('T')

class ResponseStatus(str, Enum):
    """Estados posibles de una respuesta de la API."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

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

class APIError(BaseModel):
    """Modelo para representar errores en la API."""
    code: ErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None
    field: Optional[str] = None

class PaginationMeta(BaseModel):
    """Metadatos de paginación."""
    total: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    has_next: Optional[bool] = None
    has_prev: Optional[bool] = None

class APIResponse(BaseModel, Generic[T]):
    """Respuesta estandardizada de la API."""
    status: ResponseStatus
    data: Optional[T] = None
    message: Optional[str] = None
    errors: Optional[List[APIError]] = None
    meta: Optional[Dict[str, Any]] = None

    @classmethod
    def success(
        cls, 
        data: T, 
        message: Optional[str] = None, 
        meta: Optional[Dict[str, Any]] = None
    ) -> 'APIResponse[T]':
        """Crea una respuesta exitosa."""
        return cls(
            status=ResponseStatus.SUCCESS,
            data=data,
            message=message,
            meta=meta
        )

    @classmethod
    def error(
        cls, 
        errors: Union[APIError, List[APIError]], 
        message: Optional[str] = None
    ) -> 'APIResponse[None]':
        """Crea una respuesta de error."""
        if isinstance(errors, APIError):
            errors = [errors]
        
        return cls(
            status=ResponseStatus.ERROR,
            data=None,
            message=message or "Se ha producido un error",
            errors=errors
        )

    @classmethod
    def not_found(cls, resource: str = "Registro") -> 'APIResponse[None]':
        """Crea una respuesta para recurso no encontrado."""
        return cls.error(
            APIError(
                code=ErrorCode.RECORD_NOT_FOUND,
                message=f"{resource} no encontrado"
            ),
            message=f"{resource} no encontrado"
        )

    @classmethod
    def validation_error(cls, field: str, message: str) -> 'APIResponse[None]':
        """Crea una respuesta de error de validación."""
        return cls.error(
            APIError(
                code=ErrorCode.VALIDATION_ERROR,
                message=message,
                field=field
            ),
            message="Error de validación"
        )

    @classmethod
    def database_error(cls, message: Optional[str] = None) -> 'APIResponse[None]':
        """Crea una respuesta de error de base de datos."""
        return cls.error(
            APIError(
                code=ErrorCode.DATABASE_ERROR,
                message=message or "Error en la base de datos"
            ),
            message="Error interno del servidor"
        )

class PaginatedResponse(APIResponse[List[T]]):
    """Respuesta paginada."""
    
    @classmethod
    def success_paginated(
        cls,
        data: List[T],
        total: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        message: Optional[str] = None
    ) -> 'PaginatedResponse[T]':
        """Crea una respuesta exitosa paginada."""
        pagination_meta = PaginationMeta(
            total=total,
            limit=limit,
            offset=offset,
            has_next=None if total is None or limit is None or offset is None 
                     else (offset + limit) < total,
            has_prev=None if offset is None else offset > 0
        )
        
        return cls(
            status=ResponseStatus.SUCCESS,
            data=data,
            message=message,
            meta={"pagination": pagination_meta.dict()}
        )

# Importar excepciones y manejadores
from .exceptions import (
    APIException,
    ValidationException,
    RecordNotFoundException,
    DatabaseException,
    DuplicateRecordException,
    ForeignKeyViolationException,
    BusinessRuleViolationException
)

from .handlers import setup_exception_handlers

__all__ = [
    # Clases de respuesta
    "ResponseStatus",
    "ErrorCode", 
    "APIError",
    "PaginationMeta",
    "APIResponse",
    "PaginatedResponse",
    
    # Excepciones
    "APIException",
    "ValidationException", 
    "RecordNotFoundException",
    "DatabaseException",
    "DuplicateRecordException",
    "ForeignKeyViolationException",
    "BusinessRuleViolationException",
    
    # Manejadores
    "setup_exception_handlers"
]
