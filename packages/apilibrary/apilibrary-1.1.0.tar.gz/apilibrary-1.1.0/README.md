# API Library

A simple and secure Python library for storing and retrieving API keys with automatic provider detection.

## Features

- 🔐 **Secure Storage**: API keys are encrypted before storage
- 🤖 **Auto-Detection**: Automatically detects API provider from key format
- 🚀 **Direct Commands**: Use `storekey` and `fetchkey` commands directly
- 🔒 **Local Storage**: Keys stored locally in encrypted format
- 🌐 **Multi-Provider**: Supports OpenAI, Claude, Google AI, Hugging Face, and more

## Installation

### From PyPI (Recommended)
```bash
pip install apilib
```

### From Source
```bash
git clone https://github.com/lokeshpantangi/apilib.git
cd apilib
pip install .
```

## Usage

### Store an API Key

```bash
storekey openai "sk-1234567890abcdef..."
storekey claude "sk-ant-api03-1234567890abcdef..."
storekey google "AIza1234567890abcdef..."
```

Specify the provider name and the API key. The library will store the key securely with the specified provider.

### Retrieve API Keys

```bash
fetchkey openai
```

This will display all stored API keys for the specified provider (keys are masked for security).

### Supported Providers

- **OpenAI**: `sk-...` format
- **Claude (Anthropic)**: `sk-ant-...` format
- **Google AI**: `AIza...` format
- **Hugging Face**: `hf_...` format
- **Cohere**: 40-character alphanumeric
- **Replicate**: `r8_...` format
- **Stability AI**: `sk-...` format (32 chars)

## Examples

```bash
# Store different API keys
storekey openai "sk-1234567890abcdef1234567890abcdef1234567890abcdef"
storekey claude "sk-ant-api03-1234567890abcdef..."
storekey google "AIza1234567890abcdef1234567890abcdef123"
storekey huggingface "hf_1234567890abcdef..."
storekey customapi "your-custom-api-key-here"

# Retrieve keys by provider
fetchkey openai
fetchkey claude
fetchkey google
fetchkey huggingface
fetchkey customapi
```

## Security

- API keys are encrypted using Fernet (symmetric encryption)
- Keys are stored locally in `~/.apilib/keys.json`
- Encryption key is derived from system-specific information
- Keys are masked when displayed for security

## Development

### Project Structure

```
apilib/
├── apilib/
│   ├── __init__.py      # Package initialization
│   ├── commands.py      # CLI command handlers
│   ├── core.py          # Main API key manager
│   ├── crypto.py        # Encryption/decryption
│   ├── detector.py      # API provider detection
│   └── storage.py       # File storage operations
├── setup.py             # Package configuration
└── README.md           # This file
```

### Dependencies

- `cryptography>=3.4.8` - For encryption
- `click>=8.0.0` - For CLI interface

## License

MIT License