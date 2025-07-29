# Himosoft Payment Client

A Python client library for integrating with the Himosoft Payment Logging API. This package provides a simple and robust way to log payment transactions from your applications to a centralized payment monitoring system.

## Features

- **Simple Integration**: Easy-to-use client library for logging payments
- **Comprehensive Validation**: Built-in validation for all payment data
- **Error Handling**: Detailed error handling with custom exceptions
- **Environment Configuration**: Support for environment variable configuration
- **Multiple Data Types**: Support for float, Decimal, and string amounts
- **Connection Testing**: Built-in connection testing functionality
- **Django Integration**: Ready-to-use Django integration examples
- **Comprehensive Testing**: Full test coverage with pytest

## Installation

### Using pip

```bash
pip install himosoft-payment-logging-client
```

### From source

```bash
git clone https://github.com/Swe-HimelRana/payment-logging-client.git
cd payment-client
pip install -e .
```

## Quick Start

### 1. Set up environment variables

```bash
export PAYMENT_RECORD_SERVER_URL="http://your-payment-server.com"
export PAYMENT_RECORD_PLATFORM_API_KEY="your-platform-api-key-here"
```

### 2. Basic usage

```python
from himosoft_payment_client import PaymentLogger

# Initialize the client
logger = PaymentLogger()

# Log a successful payment
result = logger.log_payment(
    user="john.doe@example.com",
    package="Premium Plan",
    amount=99.99,
    status="paid",
    trx_id="TXN123456789",
    payment_method="credit_card",
    gateway_name="Stripe",
    gateway_log={
        "payment_intent_id": "pi_1234567890",
        "charge_id": "ch_1234567890",
        "amount": 9999,
        "currency": "usd",
        "status": "succeeded"
    }
)

print(f"Payment logged: {result}")
```

## Configuration

### Environment Variables

The package uses the following environment variables:

- `PAYMENT_RECORD_SERVER_URL`: The URL of your payment logging server
- `PAYMENT_RECORD_PLATFORM_API_KEY`: Your platform's API key

### Manual Configuration

You can also pass configuration directly to the client:

```python
logger = PaymentLogger(
    server_url="http://your-server.com",
    api_key="your-api-key"
)
```

## API Reference

### PaymentLogger Class

#### Constructor

```python
PaymentLogger(server_url=None, api_key=None)
```

**Parameters:**
- `server_url` (str, optional): Payment server URL
- `api_key` (str, optional): Platform API key

If not provided, these values will be read from environment variables.

#### Methods

##### log_payment()

```python
log_payment(
    user,
    package,
    amount,
    status,
    trx_id=None,
    payment_method=None,
    gateway_name=None,
    gateway_log=None
)
```

**Parameters:**
- `user` (str): User identifier (email, username, or phone)
- `package` (str): Package or plan name
- `amount` (float/Decimal/str): Payment amount (positive number)
- `status` (str): Payment status ('paid', 'failed', 'canceled', 'refunded')
- `trx_id` (str, optional): Transaction ID (required for 'paid' and 'refunded' status)
- `payment_method` (str, optional): Payment method used
- `gateway_name` (str, optional): Payment gateway name
- `gateway_log` (dict, optional): Complete gateway response

**Returns:**
- `dict`: API response containing status and message

**Raises:**
- `PaymentLoggerValidationError`: If input validation fails
- `PaymentLoggerAPIError`: If the API returns an error
- `PaymentLoggerNetworkError`: If there's a network error

##### test_connection()

```python
test_connection()
```

**Returns:**
- `bool`: True if connection is successful

**Raises:**
- `PaymentLoggerNetworkError`: If connection fails

## Payment Statuses

The following payment statuses are supported:

- `paid`: Payment was successful (requires trx_id)
- `failed`: Payment failed
- `canceled`: Payment was canceled
- `refunded`: Payment was refunded (requires trx_id)

## Error Handling

The package provides several custom exceptions for different error types:

### PaymentLoggerError
Base exception for all payment logger errors.

### PaymentLoggerValidationError
Raised when input validation fails.

```python
try:
    logger.log_payment(
        user="",
        package="Basic Plan",
        amount=19.99,
        status="paid"
    )
except PaymentLoggerValidationError as e:
    print(f"Validation error: {e}")
```

### PaymentLoggerAPIError
Raised when the API returns an error response.

```python
try:
    result = logger.log_payment(...)
except PaymentLoggerAPIError as e:
    print(f"API error: {e}")
    print(f"Status code: {e.status_code}")
    print(f"Response data: {e.response_data}")
```

### PaymentLoggerNetworkError
Raised when there's a network-related error.

```python
try:
    result = logger.log_payment(...)
except PaymentLoggerNetworkError as e:
    print(f"Network error: {e}")
```

### PaymentLoggerConfigError
Raised when there's a configuration error.

```python
try:
    logger = PaymentLogger()
except PaymentLoggerConfigError as e:
    print(f"Configuration error: {e}")
```

## Examples

### Basic Usage

```python
from himosoft_payment_client import PaymentLogger

logger = PaymentLogger()

# Successful payment
result = logger.log_payment(
    user="user@example.com",
    package="Premium Plan",
    amount=99.99,
    status="paid",
    trx_id="TXN123456",
    payment_method="credit_card",
    gateway_name="Stripe",
    gateway_log={"charge_id": "ch_123"}
)

# Failed payment
result = logger.log_payment(
    user="user@example.com",
    package="Basic Plan",
    amount=19.99,
    status="failed",
    payment_method="credit_card",
    gateway_name="Stripe",
    gateway_log={"error": "card_declined"}
)
```

### Django Integration

```python
# settings.py
PAYMENT_RECORD_SERVER_URL = 'http://your-payment-server.com'
PAYMENT_RECORD_PLATFORM_API_KEY = 'your-api-key-here'

# views.py
from himosoft_payment_client import PaymentLogger
from django.conf import settings

def process_payment(request):
    logger = PaymentLogger(
        server_url=settings.PAYMENT_RECORD_SERVER_URL,
        api_key=settings.PAYMENT_RECORD_PLATFORM_API_KEY
    )
    
    try:
        result = logger.log_payment(
            user=request.user.email,
            package="Premium Plan",
            amount=99.99,
            status="paid",
            trx_id=transaction_id,
            payment_method="credit_card",
            gateway_name="Stripe",
            gateway_log=gateway_response
        )
        return JsonResponse({"status": "success", "result": result})
    except PaymentLoggerError as e:
        return JsonResponse({"status": "error", "message": str(e)})
```

### Testing Connection

```python
logger = PaymentLogger()

try:
    if logger.test_connection():
        print("Connection successful")
    else:
        print("Connection failed")
except PaymentLoggerNetworkError as e:
    print(f"Connection error: {e}")
```

## Validation Rules

The package enforces the following validation rules:

1. **User**: Required, cannot be empty
2. **Package**: Required, cannot be empty
3. **Amount**: Required, must be a positive number
4. **Status**: Must be one of: 'paid', 'failed', 'canceled', 'refunded'
5. **TRX ID**: Required for 'paid' and 'refunded' statuses
6. **Gateway Log**: Must be a dictionary if provided

## Development

### Setting up development environment

```bash
# Clone the repository
git clone https://github.com/Swe-HimelRana/payment-logging-client.git
cd payment-logging-client

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install package in development mode
pip install -e .
```

### Running tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=payment-logging-client

# Run specific test file
pytest tests/test_client.py

# Run tests with verbose output
pytest -v
```

### Code formatting

```bash
# Format code with black
black payment-logging-client/ tests/ examples/

# Check code style with flake8
flake8 payment-logging-client/ tests/ examples/
```

### Running examples

```bash
# Run basic usage example
python examples/basic_usage.py

# Run Django integration example (requires Django)
python examples/django_integration.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for any API changes
- Ensure all tests pass before submitting a PR

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- Check the [documentation](https://github.com/Swe-HimelRana/payment-logging-client#readme)
- Review the [examples](examples/) directory
- Open an issue on GitHub
- Contact support@himosoft.com

## Changelog

### Version 1.0.0
- Initial release
- Basic payment logging functionality
- Comprehensive validation
- Error handling with custom exceptions
- Environment variable configuration
- Django integration examples
- Full test coverage

## Acknowledgments

- Built for the Himosoft Payment Logging System
- Inspired by modern Python package development practices
- Thanks to all contributors and users 