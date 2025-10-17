"""
Base Service
Base class for all services with common functionality
"""
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class BaseService(ABC):
    """Base service class with common functionality"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize base service with logger"""
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def log_operation(self, operation: str, details: Dict[str, Any] = None, level: str = "info"):
        """Log service operations with structured data"""
        log_data = {
            "service": self.__class__.__name__,
            "operation": operation,
            **(details or {})
        }

        log_method = getattr(self.logger, level, self.logger.info)
        log_method(f"Service operation: {operation}", extra=log_data)

    def handle_error(self, operation: str, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle and log service errors"""
        error_data = {
            "service": self.__class__.__name__,
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error),
            **(context or {})
        }

        self.logger.error(f"Service error in {operation}", extra=error_data)

        return {
            "success": False,
            "error": str(error),
            "error_type": type(error).__name__
        }

    def success_response(self, data: Any = None, message: str = "Operation completed successfully") -> Dict[str, Any]:
        """Create standardized success response"""
        response = {
            "success": True,
            "message": message
        }

        if data is not None:
            response["data"] = data

        return response

    def error_response(self, message: str, error_type: str = "ServiceError", details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create standardized error response"""
        response = {
            "success": False,
            "error": message,
            "error_type": error_type
        }

        if details:
            response["details"] = details

        return response


class ServiceManager:
    """Manager for all application services"""

    def __init__(self):
        self._services = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def register_service(self, name: str, service: BaseService):
        """Register a service instance"""
        self._services[name] = service
        self.logger.info(f"Registered service: {name}")

    def get_service(self, name: str) -> Optional[BaseService]:
        """Get a registered service"""
        return self._services.get(name)

    def list_services(self) -> list:
        """List all registered services"""
        return list(self._services.keys())

    def health_check(self) -> Dict[str, Any]:
        """Check health status of all services"""
        health_status = {
            "status": "healthy",
            "services": {}
        }

        for name, service in self._services.items():
            try:
                # If service has health_check method, use it
                if hasattr(service, 'health_check'):
                    service_health = service.health_check()
                else:
                    service_health = {"status": "healthy"}

                health_status["services"][name] = service_health

                # If any service is unhealthy, mark overall as unhealthy
                if service_health.get("status") != "healthy":
                    health_status["status"] = "degraded"

            except Exception as e:
                health_status["services"][name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["status"] = "degraded"

        return health_status


# Global service manager instance
service_manager = ServiceManager()
