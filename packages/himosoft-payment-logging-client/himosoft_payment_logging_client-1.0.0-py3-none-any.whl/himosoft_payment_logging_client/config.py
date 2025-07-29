"""
Configuration management for the Himosoft Payment Logging Client package.
"""

import os
from typing import Optional
from decouple import config
from .exceptions import PaymentLoggerConfigError


class PaymentLoggerConfig:
    """Configuration class for PaymentLogger."""
    
    def __init__(self, server_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            server_url: Payment server URL (optional, will use env var if not provided)
            api_key: Platform API key (optional, will use env var if not provided)
        """
        # Set server_url - use provided value or get from environment
        if server_url is not None:
            self.server_url = server_url.rstrip('/')
        else:
            self.server_url = self._get_server_url()
        
        # Set api_key - use provided value or get from environment
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = self._get_api_key()
        
        # Validate configuration
        self._validate_config()
    
    def _get_server_url(self) -> str:
        """Get server URL from environment variable."""
        server_url = config('PAYMENT_RECORD_SERVER_URL', default=None)
        if not server_url:
            raise PaymentLoggerConfigError(
                "PAYMENT_RECORD_SERVER_URL environment variable is required. "
                "Please set it to your payment server URL."
            )
        return server_url.rstrip('/')
    
    def _get_api_key(self) -> str:
        """Get API key from environment variable."""
        api_key = config('PAYMENT_RECORD_PLATFORM_API_KEY', default=None)
        if not api_key:
            raise PaymentLoggerConfigError(
                "PAYMENT_RECORD_PLATFORM_API_KEY environment variable is required. "
                "Please set it to your platform API key."
            )
        return api_key
    
    def _validate_config(self):
        """Validate configuration values."""
        if not self.server_url:
            raise PaymentLoggerConfigError("Server URL cannot be empty")
        
        if not self.api_key:
            raise PaymentLoggerConfigError("API key cannot be empty")
        
        # Basic URL validation
        if not (self.server_url.startswith('http://') or self.server_url.startswith('https://')):
            raise PaymentLoggerConfigError("Server URL must start with http:// or https://")
    
    def get_api_endpoint(self) -> str:
        """Get the full API endpoint URL."""
        return f"{self.server_url}/api/save/{self.api_key}/" 