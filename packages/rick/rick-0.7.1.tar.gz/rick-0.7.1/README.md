# rick

[![Tests](https://github.com/oddbit-project/rick/workflows/Tests/badge.svg?branch=master)](https://github.com/oddbit-project/rick/actions)
[![pypi](https://img.shields.io/pypi/v/rick.svg)](https://pypi.org/project/rick/)
[![Python](https://img.shields.io/pypi/pyversions/rick.svg)](https://pypi.org/project/rick/)
[![license](https://img.shields.io/pypi/l/rick.svg)](https://git.oddbit.org/OddBit/rick/src/branch/master/LICENSE)

Python plumbing library for building microframework-based applications

Rick provides essential building blocks and utilities for constructing robust Python applications 
using your preferred microframework.


## Features

### Core Components
- **Dependency Injection** - Flexible DI container with singleton/factory patterns
- **Service Registry** - Dynamic class registration and factory loading
- **Container Classes** - Type-safe configuration and data containers

### Validation & Forms
- **Comprehensive Validators** - 30+ built-in validators including new `int` and `idlist` validators
- **Form Processing** - Request validation with nested records and custom error messages
- **Input Filters** - Transform and sanitize input data

### Security
- **Cryptography** - Secure password hashing with BCrypt and Fernet256 encryption
- **Redis Cache Security** - Built-in encryption support for sensitive cached data
- **Security Policy** - Comprehensive security guidelines and best practices

### Resource Management
- **Configuration Loading** - Environment variables and JSON file configuration
- **Redis Integration** - Full-featured cache facade with optional encryption
- **Stream Processing** - Multipart stream reader with seek support
- **Console Utilities** - Colored console output helpers

## Installation

```bash
pip install rick
```

## Quick Start

### Basic Dependency Injection

```python
from rick.base import Di

# Register dependencies
di = Di()
di.add(MyService)
di.add('config', {'api_key': 'secret'})

# Retrieve instances
service = di.get(MyService)
config = di.get('config')
```

### Form Validation

```python
from rick.form import RequestRecord, Field

class UserForm(RequestRecord):
    fields = {
        'username': Field(validators='required|string|min:3|max:20'),
        'email': Field(validators='required|email'),
        'age': Field(validators='required|int|min:18'),
        'friend_ids': Field(validators='idlist')  # New validator
    }

form = UserForm()
if form.is_valid(request_data):
    user_data = form.get_data()
else:
    errors = form.get_errors()
```

### Secure Redis Cache

```python
from rick.resource.redis import CryptRedisCache

# Encrypted cache for sensitive data
cache = CryptRedisCache(
    key='your-64-char-encryption-key',
    host='localhost',
    port=6379
)

cache.set('user:123', sensitive_data, ttl=3600)
data = cache.get('user:123')
```

## Development

### Requirements
- Python 3.8+
- Redis (for cache features)
- Docker (for running tests with testcontainers)

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://git.oddbit.org/OddBit/rick.git
cd rick

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=rick

# Run linting
flake8 rick/ tests/
```

### Running Tests with Tox

```bash
# Run all tests
tox

# Run specific Python version
tox -e py310

# Run linting only
tox -e flake
```

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.
