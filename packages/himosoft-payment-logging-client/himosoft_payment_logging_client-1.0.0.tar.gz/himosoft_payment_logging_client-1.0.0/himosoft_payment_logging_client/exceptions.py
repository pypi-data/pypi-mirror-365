"""
Custom exceptions for the Himosoft Payment Logging Client package.
"""


class PaymentLoggerError(Exception):
    """Base exception for all payment logger errors."""
    pass


class PaymentLoggerConfigError(PaymentLoggerError):
    """Raised when there's a configuration error."""
    pass


class PaymentLoggerValidationError(PaymentLoggerError):
    """Raised when input validation fails."""
    pass


class PaymentLoggerAPIError(PaymentLoggerError):
    """Raised when the API returns an error response."""
    
    def __init__(self, message, status_code=None, response_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class PaymentLoggerNetworkError(PaymentLoggerError):
    """Raised when there's a network-related error."""
    pass 