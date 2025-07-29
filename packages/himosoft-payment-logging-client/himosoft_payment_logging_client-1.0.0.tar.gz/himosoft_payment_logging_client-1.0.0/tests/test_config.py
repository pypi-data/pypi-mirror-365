"""
Unit tests for the PaymentLoggerConfig class.
"""

import os
import pytest
from unittest.mock import patch

from himosoft_payment_logging_client.config import PaymentLoggerConfig
from himosoft_payment_logging_client.exceptions import PaymentLoggerConfigError


class TestPaymentLoggerConfig:
    """Test cases for PaymentLoggerConfig class."""
    
    def test_config_with_parameters(self):
        """Test configuration with direct parameters."""
        config = PaymentLoggerConfig(
            server_url="http://test-server.com",
            api_key="test-api-key"
        )
        
        assert config.server_url == "http://test-server.com"
        assert config.api_key == "test-api-key"
        assert config.get_api_endpoint() == "http://test-server.com/api/save/test-api-key/"
    
    def test_config_removes_trailing_slash(self):
        """Test that trailing slash is removed from server URL."""
        config = PaymentLoggerConfig(
            server_url="http://test-server.com/",
            api_key="test-api-key"
        )
        
        assert config.server_url == "http://test-server.com"
        assert config.get_api_endpoint() == "http://test-server.com/api/save/test-api-key/"
    
    def test_config_from_environment(self):
        """Test configuration loading from environment variables."""
        with patch.dict(os.environ, {
            'PAYMENT_RECORD_SERVER_URL': 'http://env-server.com',
            'PAYMENT_RECORD_PLATFORM_API_KEY': 'env-api-key'
        }):
            config = PaymentLoggerConfig()
            
            assert config.server_url == "http://env-server.com"
            assert config.api_key == "env-api-key"
            assert config.get_api_endpoint() == "http://env-server.com/api/save/env-api-key/"
    
    def test_config_parameters_override_environment(self):
        """Test that parameters override environment variables."""
        with patch.dict(os.environ, {
            'PAYMENT_RECORD_SERVER_URL': 'http://env-server.com',
            'PAYMENT_RECORD_PLATFORM_API_KEY': 'env-api-key'
        }):
            config = PaymentLoggerConfig(
                server_url="http://param-server.com",
                api_key="param-api-key"
            )
            
            assert config.server_url == "http://param-server.com"
            assert config.api_key == "param-api-key"
            assert config.get_api_endpoint() == "http://param-server.com/api/save/param-api-key/"
    
    def test_config_validation_empty_server_url(self):
        """Test validation error when server URL is empty."""
        with pytest.raises(PaymentLoggerConfigError) as exc_info:
            PaymentLoggerConfig(server_url="", api_key="test-api-key")
        
        assert "Server URL cannot be empty" in str(exc_info.value)
    
    def test_config_validation_empty_api_key(self):
        """Test validation error when API key is empty."""
        with pytest.raises(PaymentLoggerConfigError) as exc_info:
            PaymentLoggerConfig(server_url="http://test-server.com", api_key="")
        
        assert "API key cannot be empty" in str(exc_info.value)
    
    def test_config_validation_invalid_url(self):
        """Test validation error when URL is invalid."""
        with pytest.raises(PaymentLoggerConfigError) as exc_info:
            PaymentLoggerConfig(
                server_url="invalid-url",
                api_key="test-api-key"
            )
        
        assert "Server URL must start with http:// or https://" in str(exc_info.value)
    
    def test_config_validation_ftp_url(self):
        """Test validation error when URL uses FTP protocol."""
        with pytest.raises(PaymentLoggerConfigError) as exc_info:
            PaymentLoggerConfig(
                server_url="ftp://test-server.com",
                api_key="test-api-key"
            )
        
        assert "Server URL must start with http:// or https://" in str(exc_info.value)
    
    def test_config_missing_server_url_env(self):
        """Test error when server URL environment variable is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(PaymentLoggerConfigError) as exc_info:
                PaymentLoggerConfig()
            
            assert "PAYMENT_RECORD_SERVER_URL environment variable is required" in str(exc_info.value)
    
    def test_config_missing_api_key_env(self):
        """Test error when API key environment variable is missing."""
        with patch.dict(os.environ, {
            'PAYMENT_RECORD_SERVER_URL': 'http://test-server.com'
        }):
            with pytest.raises(PaymentLoggerConfigError) as exc_info:
                PaymentLoggerConfig()
            
            assert "PAYMENT_RECORD_PLATFORM_API_KEY environment variable is required" in str(exc_info.value)
    
    def test_get_api_endpoint_with_trailing_slash(self):
        """Test get_api_endpoint with trailing slash in server URL."""
        config = PaymentLoggerConfig(
            server_url="http://test-server.com/",
            api_key="test-api-key"
        )
        
        endpoint = config.get_api_endpoint()
        assert endpoint == "http://test-server.com/api/save/test-api-key/"
    
    def test_get_api_endpoint_without_trailing_slash(self):
        """Test get_api_endpoint without trailing slash in server URL."""
        config = PaymentLoggerConfig(
            server_url="http://test-server.com",
            api_key="test-api-key"
        )
        
        endpoint = config.get_api_endpoint()
        assert endpoint == "http://test-server.com/api/save/test-api-key/"
    
    def test_config_with_https_url(self):
        """Test configuration with HTTPS URL."""
        config = PaymentLoggerConfig(
            server_url="https://secure-server.com",
            api_key="test-api-key"
        )
        
        assert config.server_url == "https://secure-server.com"
        assert config.get_api_endpoint() == "https://secure-server.com/api/save/test-api-key/"
    
    def test_config_with_port_in_url(self):
        """Test configuration with port in URL."""
        config = PaymentLoggerConfig(
            server_url="http://test-server.com:8080",
            api_key="test-api-key"
        )
        
        assert config.server_url == "http://test-server.com:8080"
        assert config.get_api_endpoint() == "http://test-server.com:8080/api/save/test-api-key/"
    
    def test_config_with_path_in_url(self):
        """Test configuration with path in URL."""
        config = PaymentLoggerConfig(
            server_url="http://test-server.com/api/v1",
            api_key="test-api-key"
        )
        
        assert config.server_url == "http://test-server.com/api/v1"
        assert config.get_api_endpoint() == "http://test-server.com/api/v1/api/save/test-api-key/" 