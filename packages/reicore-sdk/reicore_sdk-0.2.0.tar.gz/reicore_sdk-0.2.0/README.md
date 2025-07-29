# Rei Core SDK (Python)

A Python SDK for interacting with the Reigent, providing a simple interface for chat completions and agent management.

## Features

- Chat completion functionality
- Agent management

## Installation

Install the package using pip:

```bash
pip install reicore_sdk
```

## Quick Start

```python
from reicore_sdk import ReiCoreSdk

# Initialize the SDK with your Reigent Secret key
rei_agent = ReiCoreSdk("your-reiagent-secret-key")

# Get agent details
agent = rei_agent.get_agent()
print("Agent Details:", agent)

# Send a chat completion request
# Type: Text
message = {
    "messages": [
        {
            "role": "user",
            "content": "Hello world"
        }
    ],
    "tools": []
}

# Type: Image_url
message = {
    "messages": [
        {
            "role": "user",
            "content": [
                { "type": "text", "text": "What is in this image" },
                { "type": "image_url",
                    "image_url": {
                        "url": "https://test.png"
                    }
                }
            ]
        }
    ],
    "tools": []
}
response = rei_agent.chat.completion(message)
print("Chat Completion:", response)
```

## Error Handling

The SDK includes built-in error handling for API requests. All methods will raise exceptions with descriptive messages if there are any issues with the API calls.

## Requirements

- Python >= 3.6
- requests >= 2.25.1

## License

MIT License

## Support

For support, please contact rei.analoglabs@proton.me
