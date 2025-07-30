"""
Helper functions and utilities for the DeepAI package
"""

import os
import json
import mimetypes
from typing import Any, Dict, Optional, Union, BinaryIO


def validate_api_key(api_key: Optional[str]) -> str:
    """
    Validate and return API key from parameter or environment
    
    Args:
        api_key: API key string or None
        
    Returns:
        Valid API key string
        
    Raises:
        ValueError: If no API key is found
    """
    if api_key:
        return api_key
    
    env_key = os.getenv("DEEPAI_API_KEY")
    if env_key:
        return env_key
    
    raise ValueError(
        "API key is required. Provide it as a parameter or set DEEPAI_API_KEY environment variable."
    )


def prepare_file_for_upload(
    file_input: Union[str, bytes, BinaryIO]
) -> tuple[bytes, str]:
    """
    Prepare file for upload, detecting content type
    
    Args:
        file_input: File path, bytes, or file object
        
    Returns:
        Tuple of (file_data, content_type)
    """
    if isinstance(file_input, str):
        # File path
        with open(file_input, 'rb') as f:
            file_data = f.read()
        content_type, _ = mimetypes.guess_type(file_input)
        return file_data, content_type or 'application/octet-stream'
    
    elif isinstance(file_input, bytes):
        # Binary data
        return file_input, 'application/octet-stream'
    
    else:
        # File object
        file_data = file_input.read()
        filename = getattr(file_input, 'name', '')
        content_type, _ = mimetypes.guess_type(filename)
        return file_data, content_type or 'application/octet-stream'


def format_chat_history(messages: list) -> str:
    """
    Format chat messages for DeepAI API
    
    Args:
        messages: List of chat messages
        
    Returns:
        JSON formatted string
    """
    return json.dumps(messages, ensure_ascii=False)


def parse_response_content(response_data: Dict[str, Any]) -> str:
    """
    Extract content from DeepAI API response
    
    Args:
        response_data: Raw response data from API
        
    Returns:
        Extracted content string
    """
    # Try different possible content keys
    content_keys = ['output', 'text', 'content', 'response']
    
    for key in content_keys:
        if key in response_data:
            return str(response_data[key])
    
    # If no known keys, return string representation
    return str(response_data)


def validate_model(model: str) -> str:
    """
    Validate model name against supported models
    
    Args:
        model: Model name to validate
        
    Returns:
        Validated model name
        
    Raises:
        ValueError: If model is not supported
    """
    supported_models = ['standard', 'online', 'math']
    
    if model not in supported_models:
        raise ValueError(
            f"Unsupported model '{model}'. "
            f"Supported models: {', '.join(supported_models)}"
        )
    
    return model


def validate_chat_style(chat_style: str) -> str:
    """
    Validate chat style format
    
    Args:
        chat_style: Chat style to validate
        
    Returns:
        Validated chat style
    """
    if not chat_style or not isinstance(chat_style, str):
        raise ValueError("Chat style must be a non-empty string")
    
    return chat_style


def safe_get_nested(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    Safely get nested dictionary values
    
    Args:
        data: Dictionary to search
        *keys: Keys to traverse
        default: Default value if key not found
        
    Returns:
        Value at nested key or default
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def create_error_response(error_message: str, error_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Create standardized error response
    
    Args:
        error_message: Error message
        error_code: Optional error code
        
    Returns:
        Standardized error response
    """
    return {
        "error": {
            "message": error_message,
            "code": error_code,
            "type": "api_error"
        }
    }


def is_audio_file(filename: str) -> bool:
    """
    Check if file is an audio file based on extension
    
    Args:
        filename: File name or path
        
    Returns:
        True if audio file, False otherwise
    """
    audio_extensions = {
        '.mp3', '.wav', '.m4a', '.aac', '.ogg', 
        '.flac', '.wma', '.opus', '.aiff'
    }
    
    _, ext = os.path.splitext(filename.lower())
    return ext in audio_extensions


def is_image_file(filename: str) -> bool:
    """
    Check if file is an image file based on extension
    
    Args:
        filename: File name or path
        
    Returns:
        True if image file, False otherwise
    """
    image_extensions = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', 
        '.webp', '.svg', '.tiff', '.ico'
    }
    
    _, ext = os.path.splitext(filename.lower())
    return ext in image_extensions


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length with ellipsis
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."
