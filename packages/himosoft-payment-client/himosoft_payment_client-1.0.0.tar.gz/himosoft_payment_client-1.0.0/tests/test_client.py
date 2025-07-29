"""
Tests for the PaymentLogger client.
"""

import pytest
import responses
import requests
from decimal import Decimal

from himosoft_payment_client import PaymentLogger
from himosoft_payment_client.exceptions import (
    PaymentLoggerError,
    PaymentLoggerValidationError,
    PaymentLoggerAPIError,
    PaymentLoggerNetworkError,
    PaymentLoggerConfigError
)


class TestPaymentLogger:
    """Test cases for PaymentLogger class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.server_url = "http://test-server.com"
        self.api_key = "test-api-key-123"
        self.logger = PaymentLogger(self.server_url, self.api_key)
        self.api_endpoint = f"{self.server_url}/api/save/{self.api_key}/"
    
    @responses.activate
    def test_successful_payment_log(self):
        """Test successful payment logging."""
        # Mock successful response
        mock_response = {
            "status": "success",
            "message": "Payment log saved successfully",
            "payment_id": 123
        }
        responses.add(
            responses.POST,
            self.api_endpoint,
            json=mock_response,
            status=200
        )
        
        # Test payment logging
        result = self.logger.log_payment(
            user="test@example.com",
            package="Premium Plan",
            amount=99.99,
            status="paid",
            trx_id="TXN123456",
            payment_method="credit_card",
            gateway_name="Stripe",
            gateway_log={"charge_id": "ch_123"}
        )
        
        assert result == mock_response
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == self.api_endpoint
    
    @responses.activate
    def test_payment_log_with_decimal_amount(self):
        """Test payment logging with Decimal amount."""
        mock_response = {"status": "success", "message": "Success"}
        responses.add(
            responses.POST,
            self.api_endpoint,
            json=mock_response,
            status=200
        )
        
        result = self.logger.log_payment(
            user="test@example.com",
            package="Basic Plan",
            amount=Decimal("19.99"),
            status="paid",
            trx_id="TXN123"
        )
        
        assert result == mock_response
    
    @responses.activate
    def test_payment_log_with_string_amount(self):
        """Test payment logging with string amount."""
        mock_response = {"status": "success", "message": "Success"}
        responses.add(
            responses.POST,
            self.api_endpoint,
            json=mock_response,
            status=200
        )
        
        result = self.logger.log_payment(
            user="test@example.com",
            package="Basic Plan",
            amount="19.99",
            status="paid",
            trx_id="TXN123"
        )
        
        assert result == mock_response
    
    def test_validation_user_required(self):
        """Test validation when user is missing."""
        with pytest.raises(PaymentLoggerValidationError) as exc_info:
            self.logger.log_payment(
                user="",
                package="Basic Plan",
                amount=19.99,
                status="paid",
                trx_id="TXN123"
            )
        
        assert "user is required" in str(exc_info.value)
    
    def test_validation_package_required(self):
        """Test validation when package is missing."""
        with pytest.raises(PaymentLoggerValidationError) as exc_info:
            self.logger.log_payment(
                user="test@example.com",
                package="",
                amount=19.99,
                status="paid",
                trx_id="TXN123"
            )
        
        assert "package is required" in str(exc_info.value)
    
    def test_validation_amount_positive(self):
        """Test validation when amount is not positive."""
        with pytest.raises(PaymentLoggerValidationError) as exc_info:
            self.logger.log_payment(
                user="test@example.com",
                package="Basic Plan",
                amount=0,
                status="paid",
                trx_id="TXN123"
            )
        
        assert "amount must be a positive number" in str(exc_info.value)
    
    def test_validation_amount_negative(self):
        """Test validation when amount is negative."""
        with pytest.raises(PaymentLoggerValidationError) as exc_info:
            self.logger.log_payment(
                user="test@example.com",
                package="Basic Plan",
                amount=-10,
                status="paid",
                trx_id="TXN123"
            )
        
        assert "amount must be a positive number" in str(exc_info.value)
    
    def test_validation_invalid_status(self):
        """Test validation when status is invalid."""
        with pytest.raises(PaymentLoggerValidationError) as exc_info:
            self.logger.log_payment(
                user="test@example.com",
                package="Basic Plan",
                amount=19.99,
                status="invalid_status"
            )
        
        assert "status must be one of" in str(exc_info.value)
    
    def test_validation_trx_id_required_for_paid(self):
        """Test validation when trx_id is missing for paid status."""
        with pytest.raises(PaymentLoggerValidationError) as exc_info:
            self.logger.log_payment(
                user="test@example.com",
                package="Basic Plan",
                amount=19.99,
                status="paid"
            )
        
        assert "trx_id is required for 'paid' status" in str(exc_info.value)
    
    def test_validation_trx_id_required_for_refunded(self):
        """Test validation when trx_id is missing for refunded status."""
        with pytest.raises(PaymentLoggerValidationError) as exc_info:
            self.logger.log_payment(
                user="test@example.com",
                package="Basic Plan",
                amount=19.99,
                status="refunded"
            )
        
        assert "trx_id is required for 'refunded' status" in str(exc_info.value)
    
    def test_validation_trx_id_optional_for_failed(self):
        """Test that trx_id is optional for failed status."""
        mock_response = {"status": "success", "message": "Success"}
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                self.api_endpoint,
                json=mock_response,
                status=200
            )
            
            result = self.logger.log_payment(
                user="test@example.com",
                package="Basic Plan",
                amount=19.99,
                status="failed"
            )
            
            assert result == mock_response
    
    def test_validation_gateway_log_must_be_dict(self):
        """Test validation when gateway_log is not a dict."""
        with pytest.raises(PaymentLoggerValidationError) as exc_info:
            self.logger.log_payment(
                user="test@example.com",
                package="Basic Plan",
                amount=19.99,
                status="paid",
                trx_id="TXN123",
                gateway_log="not_a_dict"
            )
        
        assert "gateway_log must be a dictionary" in str(exc_info.value)
    
    @responses.activate
    def test_api_error_400(self):
        """Test handling of 400 API error."""
        error_response = {
            "status": "error",
            "message": "Invalid request data",
            "errors": {"amount": ["This field is required."]}
        }
        responses.add(
            responses.POST,
            self.api_endpoint,
            json=error_response,
            status=400
        )
        
        with pytest.raises(PaymentLoggerValidationError) as exc_info:
            self.logger.log_payment(
                user="test@example.com",
                package="Basic Plan",
                amount=19.99,
                status="paid",
                trx_id="TXN123"
            )
        
        assert "Invalid request data" in str(exc_info.value)
    
    @responses.activate
    def test_api_error_401(self):
        """Test handling of 401 API error."""
        error_response = {
            "status": "error",
            "message": "Invalid platform key or platform is disabled"
        }
        responses.add(
            responses.POST,
            self.api_endpoint,
            json=error_response,
            status=401
        )
        
        with pytest.raises(PaymentLoggerAPIError) as exc_info:
            self.logger.log_payment(
                user="test@example.com",
                package="Basic Plan",
                amount=19.99,
                status="paid",
                trx_id="TXN123"
            )
        
        assert exc_info.value.status_code == 401
        assert "Invalid platform key" in str(exc_info.value)
    
    @responses.activate
    def test_api_error_403(self):
        """Test handling of 403 API error."""
        error_response = {
            "status": "error",
            "message": "IP address not in allowed list"
        }
        responses.add(
            responses.POST,
            self.api_endpoint,
            json=error_response,
            status=403
        )
        
        with pytest.raises(PaymentLoggerAPIError) as exc_info:
            self.logger.log_payment(
                user="test@example.com",
                package="Basic Plan",
                amount=19.99,
                status="paid",
                trx_id="TXN123"
            )
        
        assert exc_info.value.status_code == 403
        assert "IP address not in allowed list" in str(exc_info.value)
    
    @responses.activate
    def test_api_error_404(self):
        """Test handling of 404 API error."""
        error_response = {
            "status": "error",
            "message": "Platform not found"
        }
        responses.add(
            responses.POST,
            self.api_endpoint,
            json=error_response,
            status=404
        )
        
        with pytest.raises(PaymentLoggerAPIError) as exc_info:
            self.logger.log_payment(
                user="test@example.com",
                package="Basic Plan",
                amount=19.99,
                status="paid",
                trx_id="TXN123"
            )
        
        assert exc_info.value.status_code == 404
        assert "Platform not found" in str(exc_info.value)
    
    @responses.activate
    def test_api_error_500(self):
        """Test handling of 500 API error."""
        error_response = {
            "status": "error",
            "message": "Internal server error"
        }
        responses.add(
            responses.POST,
            self.api_endpoint,
            json=error_response,
            status=500
        )
        
        with pytest.raises(PaymentLoggerAPIError) as exc_info:
            self.logger.log_payment(
                user="test@example.com",
                package="Basic Plan",
                amount=19.99,
                status="paid",
                trx_id="TXN123"
            )
        
        assert exc_info.value.status_code == 500
        assert "Internal server error" in str(exc_info.value)
    
    @responses.activate
    def test_invalid_json_response(self):
        """Test handling of invalid JSON response."""
        responses.add(
            responses.POST,
            self.api_endpoint,
            body="Invalid JSON",
            status=200
        )
        
        with pytest.raises(PaymentLoggerAPIError) as exc_info:
            self.logger.log_payment(
                user="test@example.com",
                package="Basic Plan",
                amount=19.99,
                status="paid",
                trx_id="TXN123"
            )
        
        assert "Invalid JSON response" in str(exc_info.value)
    
    @responses.activate
    def test_connection_timeout(self):
        """Test handling of connection timeout."""
        responses.add(
            responses.POST,
            self.api_endpoint,
            body=requests.exceptions.Timeout("Request timeout")
        )
        
        with pytest.raises(PaymentLoggerNetworkError) as exc_info:
            self.logger.log_payment(
                user="test@example.com",
                package="Basic Plan",
                amount=19.99,
                status="paid",
                trx_id="TXN123"
            )
        
        assert "Request timeout" in str(exc_info.value)
    
    @responses.activate
    def test_connection_error(self):
        """Test handling of connection error."""
        responses.add(
            responses.POST,
            self.api_endpoint,
            body=requests.exceptions.ConnectionError("Connection failed")
        )
        
        with pytest.raises(PaymentLoggerNetworkError) as exc_info:
            self.logger.log_payment(
                user="test@example.com",
                package="Basic Plan",
                amount=19.99,
                status="paid",
                trx_id="TXN123"
            )
        
        assert "Connection error" in str(exc_info.value)
    
    @responses.activate
    def test_test_connection_success(self):
        """Test successful connection test."""
        responses.add(
            responses.GET,
            f"{self.server_url}/api/",
            status=200
        )
        
        result = self.logger.test_connection()
        assert result is True
    
    @responses.activate
    def test_test_connection_failure(self):
        """Test failed connection test."""
        responses.add(
            responses.GET,
            f"{self.server_url}/api/",
            body=requests.exceptions.ConnectionError("Connection failed")
        )
        
        with pytest.raises(PaymentLoggerNetworkError) as exc_info:
            self.logger.test_connection()
        
        assert "Connection test failed" in str(exc_info.value) 