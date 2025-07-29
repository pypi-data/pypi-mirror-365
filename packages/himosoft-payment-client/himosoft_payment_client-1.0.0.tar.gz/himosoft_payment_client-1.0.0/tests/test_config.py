"""
Tests for the PaymentLoggerConfig class.
"""

import pytest
import os
from unittest.mock import patch

from himosoft_payment_client.config import PaymentLoggerConfig
from himosoft_payment_client.exceptions import PaymentLoggerConfigError


class TestPaymentLoggerConfig:
    """Test cases for PaymentLoggerConfig class."""
    
    def test_valid_config_with_parameters(self):
        """Test configuration with valid parameters."""
        config = PaymentLoggerConfig(
            server_url="http://test-server.com",
            api_key="test-api-key-123"
        )
        
        assert config.server_url == "http://test-server.com"
        assert config.api_key == "test-api-key-123"
        assert config.get_api_endpoint() == "http://test-server.com/api/save/test-api-key-123/"
    
    def test_valid_config_with_https(self):
        """Test configuration with HTTPS URL."""
        config = PaymentLoggerConfig(
            server_url="https://test-server.com",
            api_key="test-api-key-123"
        )
        
        assert config.server_url == "https://test-server.com"
        assert config.get_api_endpoint() == "https://test-server.com/api/save/test-api-key-123/"
    
    def test_config_removes_trailing_slash(self):
        """Test that trailing slash is removed from server URL."""
        config = PaymentLoggerConfig(
            server_url="http://test-server.com/",
            api_key="test-api-key-123"
        )
        
        assert config.server_url == "http://test-server.com"
        assert config.get_api_endpoint() == "http://test-server.com/api/save/test-api-key-123/"
    
    @patch.dict(os.environ, {
        'PAYMENT_RECORD_SERVER_URL': 'http://env-server.com',
        'PAYMENT_RECORD_PLATFORM_API_KEY': 'env-api-key-123'
    })
    def test_config_from_environment(self):
        """Test configuration from environment variables."""
        config = PaymentLoggerConfig()
        
        assert config.server_url == "http://env-server.com"
        assert config.api_key == "env-api-key-123"
        assert config.get_api_endpoint() == "http://env-server.com/api/save/env-api-key-123/"
    
    @patch.dict(os.environ, {
        'PAYMENT_RECORD_SERVER_URL': 'http://env-server.com/',
        'PAYMENT_RECORD_PLATFORM_API_KEY': 'env-api-key-123'
    })
    def test_config_from_environment_removes_trailing_slash(self):
        """Test that trailing slash is removed from environment URL."""
        config = PaymentLoggerConfig()
        
        assert config.server_url == "http://env-server.com"
        assert config.get_api_endpoint() == "http://env-server.com/api/save/env-api-key-123/"
    
    def test_config_validation_empty_server_url(self):
        """Test validation when server URL is empty."""
        with pytest.raises(PaymentLoggerConfigError) as exc_info:
            PaymentLoggerConfig(server_url="", api_key="test-key")
        
        assert "Server URL cannot be empty" in str(exc_info.value)
    
    def test_config_validation_empty_api_key(self):
        """Test validation when API key is empty."""
        with pytest.raises(PaymentLoggerConfigError) as exc_info:
            PaymentLoggerConfig(server_url="http://test.com", api_key="")
        
        assert "API key cannot be empty" in str(exc_info.value)
    
    def test_config_validation_invalid_url_scheme(self):
        """Test validation when URL scheme is invalid."""
        with pytest.raises(PaymentLoggerConfigError) as exc_info:
            PaymentLoggerConfig(server_url="ftp://test.com", api_key="test-key")
        
        assert "Server URL must start with http:// or https://" in str(exc_info.value)
    
    def test_config_validation_invalid_url_format(self):
        """Test validation when URL format is invalid."""
        with pytest.raises(PaymentLoggerConfigError) as exc_info:
            PaymentLoggerConfig(server_url="invalid-url", api_key="test-key")
        
        assert "Server URL must start with http:// or https://" in str(exc_info.value)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_config_missing_server_url_env(self):
        """Test error when server URL environment variable is missing."""
        with pytest.raises(PaymentLoggerConfigError) as exc_info:
            PaymentLoggerConfig()
        
        assert "PAYMENT_RECORD_SERVER_URL environment variable is required" in str(exc_info.value)
    
    @patch.dict(os.environ, {
        'PAYMENT_RECORD_SERVER_URL': 'http://test-server.com'
    }, clear=True)
    def test_config_missing_api_key_env(self):
        """Test error when API key environment variable is missing."""
        with pytest.raises(PaymentLoggerConfigError) as exc_info:
            PaymentLoggerConfig()
        
        assert "PAYMENT_RECORD_PLATFORM_API_KEY environment variable is required" in str(exc_info.value)
    
    @patch.dict(os.environ, {
        'PAYMENT_RECORD_SERVER_URL': '',
        'PAYMENT_RECORD_PLATFORM_API_KEY': 'test-key'
    }, clear=True)
    def test_config_empty_server_url_env(self):
        """Test error when server URL environment variable is empty."""
        with pytest.raises(PaymentLoggerConfigError) as exc_info:
            PaymentLoggerConfig()
        
        assert "PAYMENT_RECORD_SERVER_URL environment variable is required" in str(exc_info.value)
    
    @patch.dict(os.environ, {
        'PAYMENT_RECORD_SERVER_URL': 'http://test-server.com',
        'PAYMENT_RECORD_PLATFORM_API_KEY': ''
    }, clear=True)
    def test_config_empty_api_key_env(self):
        """Test error when API key environment variable is empty."""
        with pytest.raises(PaymentLoggerConfigError) as exc_info:
            PaymentLoggerConfig()
        
        assert "PAYMENT_RECORD_PLATFORM_API_KEY environment variable is required" in str(exc_info.value)
    
    def test_get_api_endpoint(self):
        """Test API endpoint generation."""
        config = PaymentLoggerConfig(
            server_url="http://test-server.com",
            api_key="test-api-key-123"
        )
        
        endpoint = config.get_api_endpoint()
        assert endpoint == "http://test-server.com/api/save/test-api-key-123/"
    
    def test_get_api_endpoint_with_trailing_slash(self):
        """Test API endpoint generation with trailing slash in server URL."""
        config = PaymentLoggerConfig(
            server_url="http://test-server.com/",
            api_key="test-api-key-123"
        )
        
        endpoint = config.get_api_endpoint()
        assert endpoint == "http://test-server.com/api/save/test-api-key-123/" 