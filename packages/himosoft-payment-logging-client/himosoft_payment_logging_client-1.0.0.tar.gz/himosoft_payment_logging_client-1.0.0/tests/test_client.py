"""
Unit tests for the PaymentLogger client.
"""

import pytest
import requests
import responses
from decimal import Decimal

from himosoft_payment_logging_client import PaymentLogger
from himosoft_payment_logging_client.exceptions import (
    PaymentLoggerError,
    PaymentLoggerValidationError,
    PaymentLoggerAPIError,
    PaymentLoggerNetworkError
)


class TestPaymentLogger:
    """Test cases for PaymentLogger class."""
    
    def test_successful_payment_logging(self):
        """Test successful payment logging."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                "http://test-server.com/api/save/test-api-key/",
                json={"status": "success", "message": "Payment logged successfully"},
                status=200
            )
            
            logger = PaymentLogger("http://test-server.com", "test-api-key")
            result = logger.log_payment(
                user="test@example.com",
                package="Test Package",
                amount=99.99,
                status="paid",
                trx_id="TXN123",
                gateway_log={"test": True}
            )
            
            assert result["status"] == "success"
            assert result["message"] == "Payment logged successfully"
    
    def test_validation_missing_user(self):
        """Test validation error when user is missing."""
        logger = PaymentLogger("http://test-server.com", "test-api-key")
        
        with pytest.raises(PaymentLoggerValidationError) as exc_info:
            logger.log_payment(
                user="",
                package="Test Package",
                amount=99.99,
                status="paid",
                trx_id="TXN123",
                gateway_log={"test": True}
            )
        
        assert "user is required" in str(exc_info.value)
    
    def test_validation_missing_package(self):
        """Test validation error when package is missing."""
        logger = PaymentLogger("http://test-server.com", "test-api-key")
        
        with pytest.raises(PaymentLoggerValidationError) as exc_info:
            logger.log_payment(
                user="test@example.com",
                package="",
                amount=99.99,
                status="paid",
                trx_id="TXN123",
                gateway_log={"test": True}
            )
        
        assert "package is required" in str(exc_info.value)
    
    def test_validation_invalid_amount(self):
        """Test validation error when amount is invalid."""
        logger = PaymentLogger("http://test-server.com", "test-api-key")
        
        with pytest.raises(PaymentLoggerValidationError) as exc_info:
            logger.log_payment(
                user="test@example.com",
                package="Test Package",
                amount=-10,
                status="paid",
                trx_id="TXN123",
                gateway_log={"test": True}
            )
        
        assert "amount must be a positive number" in str(exc_info.value)
    
    def test_validation_invalid_status(self):
        """Test validation error when status is invalid."""
        logger = PaymentLogger("http://test-server.com", "test-api-key")
        
        with pytest.raises(PaymentLoggerValidationError) as exc_info:
            logger.log_payment(
                user="test@example.com",
                package="Test Package",
                amount=99.99,
                status="invalid_status",
                trx_id="TXN123",
                gateway_log={"test": True}
            )
        
        assert "status must be one of" in str(exc_info.value)
    
    def test_validation_missing_trx_id_for_paid(self):
        """Test validation error when trx_id is missing for paid status."""
        logger = PaymentLogger("http://test-server.com", "test-api-key")
        
        with pytest.raises(PaymentLoggerValidationError) as exc_info:
            logger.log_payment(
                user="test@example.com",
                package="Test Package",
                amount=99.99,
                status="paid",
                gateway_log={"test": True}
            )
        
        assert "trx_id is required for 'paid' status" in str(exc_info.value)
    
    def test_validation_missing_trx_id_for_refunded(self):
        """Test validation error when trx_id is missing for refunded status."""
        logger = PaymentLogger("http://test-server.com", "test-api-key")
        
        with pytest.raises(PaymentLoggerValidationError) as exc_info:
            logger.log_payment(
                user="test@example.com",
                package="Test Package",
                amount=99.99,
                status="refunded",
                gateway_log={"test": True}
            )
        
        assert "trx_id is required for 'refunded' status" in str(exc_info.value)
    
    def test_api_error_400(self):
        """Test API error with 400 status code."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                "http://test-server.com/api/save/test-api-key/",
                json={"message": "Validation error", "errors": {"field": "error"}},
                status=400
            )
            
            logger = PaymentLogger("http://test-server.com", "test-api-key")
            
            with pytest.raises(PaymentLoggerValidationError) as exc_info:
                logger.log_payment(
                    user="test@example.com",
                    package="Test Package",
                    amount=99.99,
                    status="paid",
                    trx_id="TXN123",
                    gateway_log={"test": True}
                )
            
            assert "Validation error" in str(exc_info.value)
    
    def test_api_error_401(self):
        """Test API error with 401 status code."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                "http://test-server.com/api/save/test-api-key/",
                json={"message": "Invalid platform key"},
                status=401
            )
            
            logger = PaymentLogger("http://test-server.com", "test-api-key")
            
            with pytest.raises(PaymentLoggerAPIError) as exc_info:
                logger.log_payment(
                    user="test@example.com",
                    package="Test Package",
                    amount=99.99,
                    status="paid",
                    trx_id="TXN123",
                    gateway_log={"test": True}
                )
            
            assert "Invalid platform key" in str(exc_info.value)
            assert exc_info.value.status_code == 401
    
    def test_api_error_403(self):
        """Test API error with 403 status code."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                "http://test-server.com/api/save/test-api-key/",
                json={"message": "IP not allowed"},
                status=403
            )
            
            logger = PaymentLogger("http://test-server.com", "test-api-key")
            
            with pytest.raises(PaymentLoggerAPIError) as exc_info:
                logger.log_payment(
                    user="test@example.com",
                    package="Test Package",
                    amount=99.99,
                    status="paid",
                    trx_id="TXN123",
                    gateway_log={"test": True}
                )
            
            assert "IP address not in allowed list" in str(exc_info.value)
            assert exc_info.value.status_code == 403
    
    def test_api_error_404(self):
        """Test API error with 404 status code."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                "http://test-server.com/api/save/test-api-key/",
                json={"message": "Platform not found"},
                status=404
            )
            
            logger = PaymentLogger("http://test-server.com", "test-api-key")
            
            with pytest.raises(PaymentLoggerAPIError) as exc_info:
                logger.log_payment(
                    user="test@example.com",
                    package="Test Package",
                    amount=99.99,
                    status="paid",
                    trx_id="TXN123",
                    gateway_log={"test": True}
                )
            
            assert "Platform not found" in str(exc_info.value)
            assert exc_info.value.status_code == 404
    
    def test_api_error_500(self):
        """Test API error with 500 status code."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                "http://test-server.com/api/save/test-api-key/",
                json={"message": "Internal server error"},
                status=500
            )
            
            logger = PaymentLogger("http://test-server.com", "test-api-key")
            
            with pytest.raises(PaymentLoggerAPIError) as exc_info:
                logger.log_payment(
                    user="test@example.com",
                    package="Test Package",
                    amount=99.99,
                    status="paid",
                    trx_id="TXN123",
                    gateway_log={"test": True}
                )
            
            assert "Internal server error" in str(exc_info.value)
            assert exc_info.value.status_code == 500
    
    def test_network_timeout(self):
        """Test network timeout error."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                "http://test-server.com/api/save/test-api-key/",
                body=requests.exceptions.Timeout()
            )
            
            logger = PaymentLogger("http://test-server.com", "test-api-key")
            
            with pytest.raises(PaymentLoggerNetworkError) as exc_info:
                logger.log_payment(
                    user="test@example.com",
                    package="Test Package",
                    amount=99.99,
                    status="paid",
                    trx_id="TXN123",
                    gateway_log={"test": True}
                )
            
            assert "Request timeout" in str(exc_info.value)
    
    def test_network_connection_error(self):
        """Test network connection error."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                "http://test-server.com/api/save/test-api-key/",
                body=requests.exceptions.ConnectionError()
            )
            
            logger = PaymentLogger("http://test-server.com", "test-api-key")
            
            with pytest.raises(PaymentLoggerNetworkError) as exc_info:
                logger.log_payment(
                    user="test@example.com",
                    package="Test Package",
                    amount=99.99,
                    status="paid",
                    trx_id="TXN123",
                    gateway_log={"test": True}
                )
            
            assert "Connection error" in str(exc_info.value)
    
    def test_different_amount_types(self):
        """Test that different amount types work correctly."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                "http://test-server.com/api/save/test-api-key/",
                json={"status": "success"},
                status=200
            )
            
            logger = PaymentLogger("http://test-server.com", "test-api-key")
            
            # Test float
            result1 = logger.log_payment(
                user="test@example.com",
                package="Test Package",
                amount=99.99,
                status="paid",
                trx_id="TXN123",
                gateway_log={"test": True}
            )
            assert result1["status"] == "success"
            
            # Test Decimal
            result2 = logger.log_payment(
                user="test@example.com",
                package="Test Package",
                amount=Decimal("99.99"),
                status="paid",
                trx_id="TXN123",
                gateway_log={"test": True}
            )
            assert result2["status"] == "success"
            
            # Test string
            result3 = logger.log_payment(
                user="test@example.com",
                package="Test Package",
                amount="99.99",
                status="paid",
                trx_id="TXN123",
                gateway_log={"test": True}
            )
            assert result3["status"] == "success"
    
    def test_test_connection_success(self):
        """Test successful connection test."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "http://test-server.com/api/",
                status=200
            )
            
            logger = PaymentLogger("http://test-server.com", "test-api-key")
            assert logger.test_connection() is True
    
    def test_test_connection_failure(self):
        """Test failed connection test."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "http://test-server.com/api/",
                status=500
            )
            
            logger = PaymentLogger("http://test-server.com", "test-api-key")
            assert logger.test_connection() is False
    
    def test_test_connection_network_error(self):
        """Test connection test with network error."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "http://test-server.com/api/",
                body=requests.exceptions.ConnectionError()
            )
            
            logger = PaymentLogger("http://test-server.com", "test-api-key")
            
            with pytest.raises(PaymentLoggerNetworkError):
                logger.test_connection() 