"""
Main client class for the Himosoft Payment Logging Client package.
"""

import json
import requests
from typing import Dict, Any, Optional, Union
from decimal import Decimal

from .config import PaymentLoggerConfig
from .exceptions import (
    PaymentLoggerError,
    PaymentLoggerValidationError,
    PaymentLoggerAPIError,
    PaymentLoggerNetworkError
)


class PaymentLogger:
    """
    Client for logging payments to the Himosoft Payment Logging API.
    """
    
    VALID_STATUSES = {'paid', 'failed', 'canceled', 'refunded'}
    
    def __init__(self, server_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the PaymentLogger client.
        
        Args:
            server_url: Payment server URL (optional, will use env var if not provided)
            api_key: Platform API key (optional, will use env var if not provided)
        """
        self.config = PaymentLoggerConfig(server_url, api_key)
    
    def log_payment(
        self,
        user: str,
        package: str,
        amount: Union[float, Decimal, str],
        status: str,
        trx_id: Optional[str] = None,
        payment_method: Optional[str] = None,
        gateway_name: Optional[str] = None,
        gateway_log: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log a payment transaction to the API.
        
        Args:
            user: User identifier (email, username, or phone)
            package: Package or plan name
            amount: Payment amount (positive number)
            status: Payment status ('paid', 'failed', 'canceled', 'refunded')
            trx_id: Transaction ID (required for 'paid' and 'refunded' status)
            payment_method: Payment method used (e.g., 'credit_card', 'paypal')
            gateway_name: Payment gateway name (e.g., 'Stripe', 'PayPal')
            gateway_log: Complete gateway response (JSON object)
            
        Returns:
            Dict containing the API response
            
        Raises:
            PaymentLoggerValidationError: If input validation fails
            PaymentLoggerAPIError: If the API returns an error
            PaymentLoggerNetworkError: If there's a network error
        """
        # Validate inputs
        self._validate_payment_data(
            user, package, amount, status, trx_id, 
            payment_method, gateway_name, gateway_log
        )
        
        # Prepare request data
        request_data = {
            "user": user,
            "package": package,
            "amount": float(amount),
            "status": status,
            "payment_method": payment_method or "unknown",
            "gateway_name": gateway_name or "unknown",
            "gateway_log": gateway_log or {}
        }
        
        # Add trx_id if provided
        if trx_id:
            request_data["trx_id"] = trx_id
        
        # Make API request
        return self._make_api_request(request_data)
    
    def _validate_payment_data(
        self,
        user: str,
        package: str,
        amount: Union[float, Decimal, str],
        status: str,
        trx_id: Optional[str],
        payment_method: Optional[str],
        gateway_name: Optional[str],
        gateway_log: Optional[Dict[str, Any]]
    ):
        """Validate payment data before sending to API."""
        errors = []
        
        # Validate required fields
        if not user or not user.strip():
            errors.append("user is required")
        
        if not package or not package.strip():
            errors.append("package is required")
        
        # Validate amount
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                errors.append("amount must be a positive number")
        except (ValueError, TypeError):
            errors.append("amount must be a valid number")
        
        # Validate status
        if status not in self.VALID_STATUSES:
            errors.append(f"status must be one of: {', '.join(self.VALID_STATUSES)}")
        
        # Validate trx_id for paid/refunded status
        if status in {'paid', 'refunded'} and not trx_id:
            errors.append(f"trx_id is required for '{status}' status")
        
        # Validate gateway_log
        if gateway_log is not None and not isinstance(gateway_log, dict):
            errors.append("gateway_log must be a dictionary")
        
        if errors:
            raise PaymentLoggerValidationError(f"Validation errors: {'; '.join(errors)}")
    
    def _make_api_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make the actual API request."""
        try:
            response = requests.post(
                self.config.get_api_endpoint(),
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            # Parse response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                raise PaymentLoggerAPIError(
                    f"Invalid JSON response from server: {response.text}",
                    status_code=response.status_code
                )
            
            # Handle different status codes
            if response.status_code == 200:
                return response_data
            elif response.status_code == 400:
                raise PaymentLoggerValidationError(
                    response_data.get('message', 'Validation error'),
                    response_data.get('errors', {})
                )
            elif response.status_code == 401:
                raise PaymentLoggerAPIError(
                    "Invalid platform key or platform is disabled",
                    status_code=response.status_code,
                    response_data=response_data
                )
            elif response.status_code == 403:
                raise PaymentLoggerAPIError(
                    "IP address not in allowed list",
                    status_code=response.status_code,
                    response_data=response_data
                )
            elif response.status_code == 404:
                raise PaymentLoggerAPIError(
                    "Platform not found",
                    status_code=response.status_code,
                    response_data=response_data
                )
            else:
                raise PaymentLoggerAPIError(
                    f"API error: {response_data.get('message', 'Unknown error')}",
                    status_code=response.status_code,
                    response_data=response_data
                )
                
        except requests.exceptions.Timeout:
            raise PaymentLoggerNetworkError("Request timeout")
        except requests.exceptions.ConnectionError:
            raise PaymentLoggerNetworkError("Connection error")
        except requests.exceptions.RequestException as e:
            raise PaymentLoggerNetworkError(f"Network error: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test the connection to the payment server.
        
        Returns:
            True if connection is successful
            
        Raises:
            PaymentLoggerError: If connection fails
        """
        try:
            # Try to make a minimal request to test connection
            response = requests.get(
                f"{self.config.server_url}/api/",
                timeout=10
            )
            return response.status_code < 500  # Any non-server error is OK for connection test
        except requests.exceptions.RequestException as e:
            raise PaymentLoggerNetworkError(f"Connection test failed: {str(e)}") 