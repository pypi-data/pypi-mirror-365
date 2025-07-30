"""
DeepAI Python Client

A comprehensive Python client for the DeepAI API with support for:
- Chat completions with multiple models
- Character-based chat styles
- Text-to-speech (TTS)
- Speech-to-text (STT)
- Image generation
- Async/await support
- Session management
"""

from .clients.sync import DeepAI
from .clients.async_client import AsyncDeepAI
from .clients.specialized import (
    ChatMath,
    ChatCode,
    TextToSpeech,
    ImageGeneration,
    SpeechToText,
    ChatStyleManager,
    EnhancedDeepAI,
    AsyncChatMath,
    AsyncChatCode,
    AsyncTextToSpeech,
    AsyncImageGeneration,
    AsyncSpeechToText,
    AsyncChatStyleManager,
    AsyncEnhancedDeepAI,
)
from .utils.types import (
    ChatCompletion,
    ChatCompletionChoice,
    ChatCompletionMessage,
    ChatCompletionWithSummary,
    TTSResponse,
    STTResponse,
    ImageResponse,
    ChatStyle,
    ErrorResponse,
)

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "A Python client for the DeepAI API"

__all__ = [
    # Main clients
    "DeepAI",
    "AsyncDeepAI",
    
    # Specialized clients
    "ChatMath",
    "ChatCode", 
    "TextToSpeech",
    "ImageGeneration",
    "SpeechToText",
    "ChatStyleManager",
    "EnhancedDeepAI",
    
    # Async specialized clients
    "AsyncChatMath",
    "AsyncChatCode",
    "AsyncTextToSpeech", 
    "AsyncImageGeneration",
    "AsyncSpeechToText",
    "AsyncChatStyleManager",
    "AsyncEnhancedDeepAI",
    
    # Types
    "ChatCompletion",
    "ChatCompletionChoice",
    "ChatCompletionMessage",
    "ChatCompletionWithSummary",
    "TTSResponse",
    "STTResponse", 
    "ImageResponse",
    "ChatStyle",
    "ErrorResponse",
]
