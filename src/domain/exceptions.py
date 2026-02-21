class DomainException(Exception):
    def __init__(self, message: str, error_code: str = "DOMAIN_ERROR"):
        """Base class for domain exceptions."""
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class InvalidEntityStateException(DomainException):
    """Raised when an entity is in an invalid state."""
    def __init__(self, message: str):
        super().__init__(message, error_code="INVALID_ENTITY_STATE")

class BusinessRuleViolationException(DomainException):
    """Raised when a business rule is violated."""
    def __init__(self, message: str):
        super().__init__(message, error_code= "BUSINESS_RULE_VIOLATION")
