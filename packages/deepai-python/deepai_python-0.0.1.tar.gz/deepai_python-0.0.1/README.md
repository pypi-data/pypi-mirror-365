# DeepAI Python Client

[![PyPI version](https://badge.fury.io/py/deepai-python.svg)](https://badge.fury.io/py/deepai-python)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ⚠️ Educational Purpose Notice

**This package is created solely for educational and learning purposes.** It is designed to help developers understand API integration, Python package development, and programming concepts. 

If you represent any organization or service and have concerns about this educational project, please feel free to reach out to us politely. We are committed to resolving any issues through friendly communication and will gladly address your concerns or remove the package if requested. No legal proceedings are necessary - just send us a message!

---

A comprehensive Python client for the DeepAI API, providing easy access to chat completions, text-to-speech, speech-to-text, and image generation services.

## 🚀 Features

- **Chat Completions**: OpenAI-compatible interface with multiple models (`standard`, `online`, `math`)
- **Character Chat Styles**: Over 50+ character styles including `goku`, `gojo_9`, `ai-code`, `mathematics`
- **Text-to-Speech (TTS)**: Convert text to natural speech
- **Speech-to-Text (STT)**: Transcribe audio files to text
- **Image Generation**: Create images from text descriptions
- **Async Support**: Full async/await support for all operations
- **Session Management**: Automatic chat history management
- **File Uploads**: Support for multipart file uploads
- **Type Safety**: Full TypeScript-style type hints

## 📦 Installation

```bash
pip install deepai-python
```

For development:
```bash
pip install deepai-python[dev]
```

## 🔧 Quick Start

### Basic Chat Completion

```python
from deepai import DeepAI

client = DeepAI()

response = client.chat.completions.create(
    model="standard",
    chat_style="chatgpt-alternative",
    messages=[{"role": "user", "content": "Hello, how are you?"}]
)

print(response['choices'][0]['message']['content'])
```

### Character Chat (Anime Style)

```python
response = client.chat.completions.create(
    model="standard",
    chat_style="goku",  # Dragon Ball Z Goku style
    messages=[{"role": "user", "content": "Tell me about your training!"}]
)
```

### Math Problems

```python
from deepai import ChatMath

math_client = ChatMath(api_key="your-api-key")
response = math_client.create(
    messages=[{"role": "user", "content": "What is 25 × 35? Show steps."}],
    model="math"
)
```

### Text-to-Speech

```python
from deepai import TextToSpeech

tts = TextToSpeech(api_key="your-api-key")
audio_response = tts.speak(
    text="Hello, this is a test of text to speech!",
    voice="en-US-AriaNeural"
)

# Save audio file
with open("output.wav", "wb") as f:
    f.write(audio_response['audio_data'])
```

### Async Usage

```python
import asyncio
from deepai import AsyncDeepAI

async def main():
    client = AsyncDeepAI()
    
    response = await client.chat.completions.create(
        model="online",
        chat_style="ai-code",
        messages=[{"role": "user", "content": "Latest AI news?"}]
    )
    
    print(response['choices'][0]['message']['content'])

asyncio.run(main())
```

## 📚 Documentation

- [API Reference](docs/api-reference.md)
- [Examples](examples/)
- [Chat Styles Guide](docs/chat-styles.md)
- [Async Usage](docs/async-usage.md)

## 🛠️ Available Models

- **standard**: General-purpose chat model
- **online**: Web-enabled model with real-time information
- **math**: Specialized model for mathematical problems

## 🎭 Popular Chat Styles

- `chatgpt-alternative`: Standard AI assistant
- `goku`: Dragon Ball Z Goku personality
- `gojo_9`: Jujutsu Kaisen Gojo Satoru
- `ai-code`: Programming-focused responses
- `mathematics`: Math-oriented explanations
- And 50+ more characters and styles!

## 📁 Project Structure

```
deepai-package/
├── src/deepai/                 # Main package
│   ├── clients/               # Client implementations
│   │   ├── sync.py           # Synchronous clients
│   │   ├── async_client.py   # Asynchronous clients
│   │   └── specialized.py    # Specialized clients
│   ├── utils/                # Utility modules
│   │   ├── types.py         # Type definitions
│   │   └── helpers.py       # Helper functions
│   └── __init__.py          # Package exports
├── tests/                    # Test suite
├── examples/                 # Usage examples
├── docs/                    # Documentation
└── pyproject.toml          # Project configuration
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src/deepai

# Run specific test
pytest tests/test_chat.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `pytest`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [DeepAI API Documentation](https://deepai.org/apis)
- [GitHub Repository](https://github.com/yourusername/deepai-python)
- [PyPI Package](https://pypi.org/project/deepai-python/)

## 💡 Support

If you encounter any issues or have questions, please:
1. Check the [documentation](docs/)
2. Look through existing [issues](https://github.com/yourusername/deepai-python/issues)
3. Create a new issue with detailed information

---

Made with ❤️ for the AI community
