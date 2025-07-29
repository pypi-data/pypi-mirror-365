# FernetKeyGen

FernetKeyGen is a Python package that generates unique key for encrypting and decrypting content or file using the Fernet cryptography package. It provides a simple interface for deriving secure key from passphrase.

## Features

- Generate cryptographically secure key from passphrase
- Manage salt for consistent key generation
- Compatible with Fernet encryption
- Simple and easy-to-use API

## Installation

### From PyPI (not yet available)

```bash
pip install FernetKeyGen
```

### Local Installation

1. Clone the repository:
```bash
git clone https://github.com/kvcrajan/FernetKeyGenerator.git
cd FernetKeyGenerator
```

2. Install the package locally:
```bash
pip install -e .
```

### Uninstalling Local Installation

To uninstall the locally installed package:
```bash
pip uninstall FernetKeyGen
```

## Usage

### Basic Usage

```python
from FernetKeyGen.main import derive_key

# Generate a key with a new salt
passphrase = b"my secure passphrase"
key = derive_key(passphrase, generate_salt=True)
print(key)  # This is your Fernet key

# Later, to generate the same key (using the stored salt)
same_key = derive_key(passphrase, generate_salt=False)
print(same_key)  # This should match the previous key
```

### Using with Fernet

```python
from cryptography.fernet import Fernet
from FernetKeyGen.main import derive_key

# Generate a key
passphrase = b"my secure passphrase"
key = derive_key(passphrase, generate_salt=True)

# Create a Fernet instance
f = Fernet(key)

# Encrypt data
token = f.encrypt(b"Secret message")
print(token)

# Decrypt data
decrypted = f.decrypt(token)
print(decrypted)  # b"Secret message"
```

## Building the Package for Distribution

### Prerequisites

Make sure you have the required tools:

```bash
pip install build twine
```

### Building the Package

1. Update the package metadata in `pyproject.toml` if needed.

2. Build the package:
```bash
python -m build
```

This will create two files in the `dist/` directory:
- A source distribution (`.tar.gz`)
- A wheel distribution (`.whl`)

### Installing from Local Distribution

```bash
pip install dist/fernetkeygen-1.0.0-py3-none-any.whl
```

### Publishing to PyPI (if desired)

```bash
python -m twine upload dist/*
```

## How It Works

FernetKeyGen uses PBKDF2HMAC (Password-Based Key Derivation Function 2) with HMAC as the pseudorandom function. The process is:

1. A salt is either generated (16 random bytes) or read from a file
2. The passphrase is processed through PBKDF2HMAC with:
   - SHA256 hashing algorithm
   - 1000 iterations
   - 32 bytes output length
3. The resulting key is encoded in URL-safe base64 format, ready for use with Fernet

The salt is stored in a file (default: `.salt` in the current directory) to ensure the same key can be regenerated with the same passphrase.

## Requirements

- Python >= 3.13
- cryptography >= 45.0.5
- cffi >= 1.17.1
- pycparser >= 2.22