# Monkey Coder SDK

Python SDK for interacting with the Monkey Coder API.

## Installation

```bash
pip install monkey-coder-sdk
```

## Usage

```python
from monkey_coder_sdk import MonkeyCoderClient

client = MonkeyCoderClient(api_key="your-api-key")

# Execute a coding task
result = client.execute(
    task_type="code_generation",
    prompt="Create a function to calculate fibonacci numbers",
    files=[]
)

print(result)
```

## Features

- Easy API integration
- Type hints and validation
- Async support
- Error handling

## License

MIT License
