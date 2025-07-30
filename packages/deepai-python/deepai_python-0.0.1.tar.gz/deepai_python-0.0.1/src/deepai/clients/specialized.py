import requests
import json
import time
import uuid
from typing import Dict, List, Optional, Union, Any, BinaryIO
from ..utils.types import (
    ChatCompletion, 
    ChatCompletionMessage, 
    ChatHistory, 
    TTSResponse, 
    ImageResponse,
    STTResponse,
    ChatStyle,
    ChatCompletionWithSummary
)


class ChatMath:
    """
    Math-focused chat completion client
    
    Optimized for mathematical reasoning and problem solving.
    
    Supported models:
    - 'math': Specialized mathematics model (default)
    - 'standard': General model with math capabilities
    - 'online': Online-aware math model
    
    Default chat_style: 'mathematics'
    
    Example:
        math_client = ChatMath(api_key="your-key")
        response = math_client.create(
            messages=[{"role": "user", "content": "What is 15 + 25?"}],
            model="math"
        )
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepai.org"):
        self.api_key = api_key
        self.base_url = base_url
        self._chat_history = ChatHistory()
        self._default_hacker_is_stinky = "very_stinky"
    
    def create(
        self,
        messages: List[ChatCompletionMessage],
        model: str = "math",
        chat_style: str = "mathematics",
        session_id: Optional[str] = None,
        **kwargs
    ) -> ChatCompletion:
        """Create a math-focused chat completion"""
        
        # Handle session-wise chat history
        if session_id:
            for message in messages:
                self._chat_history.add_message(session_id, message)
            chat_history = self._chat_history.get_history(session_id)
        else:
            chat_history = messages
        
        # Prepare the request data
        data = {
            "chat_style": chat_style,
            "chatHistory": json.dumps(chat_history),
            "model": model,
            "hacker_is_stinky": self._default_hacker_is_stinky
        }
        data.update(kwargs)
        
        # Make the API request
        url = f"{self.base_url}/hacking_is_a_serious_crime"
        headers = {}
        if self.api_key:
            headers["Api-Key"] = self.api_key
        
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        
        # Parse response
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"output": response.text}
        
        # Create standardized response
        completion = ChatCompletion(
            id=str(uuid.uuid4()),
            object="chat.completion",
            created=int(time.time()),
            model=model,
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_data.get("output", response_data.get("text", str(response_data)))
                },
                "finish_reason": "stop"
            }],
            usage=None
        )
        
        # Add assistant response to session history
        if session_id:
            self._chat_history.add_message(session_id, completion["choices"][0]["message"])
        
        return completion
    
    def get_chat_history(self, session_id: str) -> List[ChatCompletionMessage]:
        """Get chat history for a session"""
        return self._chat_history.get_history(session_id)
    
    def clear_chat_history(self, session_id: str) -> None:
        """Clear chat history for a session"""
        self._chat_history.clear_session(session_id)


class ChatCode:
    """
    Code-focused chat completion client
    
    Optimized for programming, development, and technical discussions.
    
    Supported models:
    - 'standard': General model with coding capabilities (default)
    - 'online': Online-aware coding model with latest information
    - 'math': For algorithmic and computational problems
    
    Default chat_style: 'ai-code'
    
    Example:
        code_client = ChatCode(api_key="your-key")
        response = code_client.create(
            messages=[{"role": "user", "content": "Explain Python functions"}],
            chat_style="ai-code"
        )
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepai.org"):
        self.api_key = api_key
        self.base_url = base_url
        self._chat_history = ChatHistory()
        self._default_hacker_is_stinky = "very_stinky"
    
    def create(
        self,
        messages: List[ChatCompletionMessage],
        model: str = "standard",
        chat_style: str = "ai-code",
        session_id: Optional[str] = None,
        **kwargs
    ) -> ChatCompletion:
        """Create a code-focused chat completion"""
        
        # Handle session-wise chat history
        if session_id:
            for message in messages:
                self._chat_history.add_message(session_id, message)
            chat_history = self._chat_history.get_history(session_id)
        else:
            chat_history = messages
        
        # Prepare the request data
        data = {
            "chat_style": chat_style,
            "chatHistory": json.dumps(chat_history),
            "model": model,
            "hacker_is_stinky": self._default_hacker_is_stinky
        }
        data.update(kwargs)
        
        # Make the API request
        url = f"{self.base_url}/hacking_is_a_serious_crime"
        headers = {}
        if self.api_key:
            headers["Api-Key"] = self.api_key
        
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        
        # Parse response
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"output": response.text}
        
        # Create standardized response
        completion = ChatCompletion(
            id=str(uuid.uuid4()),
            object="chat.completion",
            created=int(time.time()),
            model=model,
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_data.get("output", response_data.get("text", str(response_data)))
                },
                "finish_reason": "stop"
            }],
            usage=None
        )
        
        # Add assistant response to session history
        if session_id:
            self._chat_history.add_message(session_id, completion["choices"][0]["message"])
        
        return completion
    
    def get_chat_history(self, session_id: str) -> List[ChatCompletionMessage]:
        """Get chat history for a session"""
        return self._chat_history.get_history(session_id)
    
    def clear_chat_history(self, session_id: str) -> None:
        """Clear chat history for a session"""
        self._chat_history.clear_session(session_id)


class TextToSpeech:
    """Text-to-Speech client"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepai.org"):
        self.api_key = api_key
        self.base_url = base_url
    
    def create(
        self,
        text: str,
        model: str = "aura-asteria-en",
        **kwargs
    ) -> TTSResponse:
        """Generate speech from text"""
        
        # Prepare the request data
        data = {
            "model": model,
            "text": text
        }
        data.update(kwargs)
        
        # Make the API request
        url = f"{self.base_url}/speech_response"
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Api-Key"] = self.api_key
        
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        # Parse response
        response_data = response.json()
        
        return TTSResponse(
            audio_url=response_data.get("audio_url", ""),
            id=response_data.get("id", str(uuid.uuid4())),
            status=response_data.get("status", "completed")
        )


class ImageGeneration:
    """Text-to-Image generation client"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepai.org"):
        self.api_key = api_key
        self.base_url = base_url
    
    def create(
        self,
        text: str,
        image_generator_version: str = "hd",
        use_old_model: str = "false",
        turbo: str = "true",
        **kwargs
    ) -> ImageResponse:
        """Generate image from text"""
        
        # Prepare the request data
        data = {
            "text": text,
            "image_generator_version": image_generator_version,
            "use_old_model": use_old_model,
            "turbo": turbo
        }
        data.update(kwargs)
        
        # Make the API request
        url = f"{self.base_url}/api/text2img"
        headers = {}
        if self.api_key:
            headers["Api-Key"] = self.api_key
        
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        
        # Parse response
        response_data = response.json()
        
        return ImageResponse(
            backend_request_id=response_data.get("backend_request_id", ""),
            id=response_data.get("id", ""),
            output_url=response_data.get("output_url", ""),
            share_url=response_data.get("share_url", "")
        )
    
    def save_image(self, image_response: ImageResponse, filename: str = "generated_image.jpg") -> bool:
        """Download and save the generated image"""
        try:
            if image_response["output_url"]:
                img_data = requests.get(image_response["output_url"]).content
                with open(filename, "wb") as f:
                    f.write(img_data)
                return True
        except Exception:
            pass
        return False


class SpeechToText:
    """
    Speech-to-Text client for converting audio to text
    
    Supported models: Various audio models available
    Endpoint: https://api.deepai.org/speech_to_text
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepai.org"):
        self.api_key = api_key
        self.base_url = base_url
    
    def create(
        self,
        voice_recording: Union[str, BinaryIO, bytes],
        **kwargs
    ) -> STTResponse:
        """Convert speech to text
        
        Args:
            voice_recording: Audio file (binary data, file path, or file object)
            **kwargs: Additional parameters
            
        Returns:
            STTResponse with text and usage information
        """
        
        # Prepare the request data
        files = {}
        if isinstance(voice_recording, str):
            # File path
            with open(voice_recording, 'rb') as f:
                files['voiceRecording'] = f.read()
        elif isinstance(voice_recording, bytes):
            # Binary data
            files['voiceRecording'] = voice_recording
        else:
            # File object
            files['voiceRecording'] = voice_recording.read()
        
        # Make the API request
        url = f"{self.base_url}/speech_to_text"
        headers = {}
        if self.api_key:
            headers["Api-Key"] = self.api_key
        
        response = requests.post(url, files={'voiceRecording': files['voiceRecording']}, headers=headers)
        response.raise_for_status()
        
        # Parse response
        response_data = response.json()
        
        return STTResponse(
            text=response_data.get("text", ""),
            usage=response_data.get("usage", {})
        )


class ChatStyleManager:
    """
    Manager for fetching available chat styles and characters
    
    Chat styles include: 'goku', 'gojo_9', 'ai-code', 'mathematics', etc.
    Endpoint: https://api.deepai.org/get_character_row/0/null/{genre}
    
    Available genres: 
    - 'All': All available characters
    - 'Anime': Anime characters  
    - 'Fantasy': Fantasy characters
    - 'Gaming': Gaming characters
    - 'History': Historical figures
    - 'Literature': Literary characters
    - 'Music': Musicians and music-related
    - 'Politics': Political figures
    - 'Television': TV show characters
    
    Character Creation: https://api.deepai.org/create_character
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepai.org"):
        self.api_key = api_key
        self.base_url = base_url
    
    def get_chat_styles(
        self, 
        genre: str = "All", 
        max_pages: int = 10
    ) -> List[ChatStyle]:
        """Fetch all available chat styles for a genre
        
        Args:
            genre: Genre to fetch - 'All', 'Anime', 'Fantasy', 'Gaming', 
                   'History', 'Literature', 'Music', 'Politics', 'Television'
            max_pages: Maximum pages to fetch (each page has ~20 styles)
            
        Returns:
            List of available chat styles with descriptions
        """
        
        # Validate genre
        valid_genres = ['All', 'Anime', 'Fantasy', 'Gaming', 'History', 
                       'Literature', 'Music', 'Politics', 'Television']
        if genre not in valid_genres:
            raise ValueError(f"Invalid genre '{genre}'. Must be one of: {valid_genres}")
        
        all_styles = []
        page = 0
        
        while page < max_pages:
            try:
                # Use the correct URL format
                url = f"{self.base_url}/get_character_row/{page}/null/{genre}"
                headers = {}
                if self.api_key:
                    headers["Api-Key"] = self.api_key
                
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                
                # Handle different response formats
                if isinstance(data, list):
                    styles = data
                elif isinstance(data, dict):
                    styles = data.get("characters", data.get("response", []))
                else:
                    styles = []
                
                if not styles:
                    break
                
                for style in styles:
                    chat_style = ChatStyle(
                        id=style.get("id", 0),
                        url_handle=style.get("url_handle", ""),
                        name=style.get("name", ""),
                        description=style.get("description", ""),
                        genre=style.get("genre", genre),
                        usage=style.get("usage", 0),
                        image=style.get("image", "")
                    )
                    all_styles.append(chat_style)
                
                page += 1
                
            except Exception as e:
                # If we get an error, break the loop
                break
        
        return all_styles
    
    def list_popular_styles(
        self, 
        genre: str = "All", 
        limit: int = 10
    ) -> List[ChatStyle]:
        """Get most popular chat styles for a genre
        
        Args:
            genre: Genre to search in ('All', 'Anime', 'Fantasy', etc.)
            limit: Maximum number of styles to return
            
        Returns:
            List of popular chat styles sorted by usage
        """
        
        styles = self.get_chat_styles(genre, max_pages=3)  # Get first 3 pages
        
        # Sort by usage (highest first) and limit results
        popular_styles = sorted(styles, key=lambda x: x.get("usage", 0), reverse=True)
        return popular_styles[:limit]
    
    def search_styles(
        self, 
        search_term: str, 
        genre: str = "All"
    ) -> List[ChatStyle]:
        """Search for chat styles by name or description
        
        Args:
            search_term: Term to search for in name or description
            genre: Genre to search within
            
        Returns:
            List of matching chat styles
        """
        
        all_styles = self.get_chat_styles(genre, max_pages=5)
        search_term_lower = search_term.lower()
        
        matching_styles = []
        for style in all_styles:
            name = style.get("name", "").lower()
            description = style.get("description", "").lower()
            
            if search_term_lower in name or search_term_lower in description:
                matching_styles.append(style)
        
        return matching_styles
    
    def create_character(
        self,
        name: str,
        description: str,
        is_public: bool = True
    ) -> Dict[str, Any]:
        """Create a new character for chat styles
        
        Args:
            name: Name of the character
            description: Description of the character's personality/style
            is_public: Whether the character should be public (default: True)
            
        Returns:
            Dictionary with creation result
            - Success: {"result": "success", "href": "<character_id>"}
            - Already exists: {"status": "This character already exists; log in to create a private character"}
            
        Raises:
            ValueError: If API key is required but not provided
            Exception: If creation fails for other reasons
        """
        
        if not self.api_key:
            raise ValueError("API key is required for character creation")
        
        # Prepare character info
        char_info = {
            "name": name,
            "description": description,
            "isPublic": is_public
        }
        
        # Prepare request
        url = f"{self.base_url}/create_character"
        headers = {
            "Api-Key": self.api_key
        }
        
        # Send as form data
        data = {
            "char_info": json.dumps(char_info)
        }
        
        try:
            response = requests.post(url, data=data, headers=headers)
            
            # Handle different response codes
            if response.status_code == 200:
                # Success
                return response.json()
            elif response.status_code == 401:
                # Character already exists
                return {"status": "This character already exists; log in to create a private character"}
            else:
                # Other error
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Character creation failed: {e}")
    
    def test_character(
        self,
        character_name: str,
        test_message: str = "Hello! Tell me about yourself.",
        model: str = "standard"
    ) -> ChatCompletion:
        """Test a newly created character
        
        Args:
            character_name: Name of the character to test (use as chat_style)
            test_message: Message to send to test the character
            model: Model to use for testing
            
        Returns:
            ChatCompletion response from the character
        """
        
        # Import here to avoid circular imports
        from .sync import DeepAI
        
        # Create a test client
        test_client = DeepAI(api_key=self.api_key, base_url=self.base_url)
        
        # Test the character
        response = test_client.chat.completions.create(
            model=model,
            chat_style=character_name,  # Use character name as chat style
            messages=[{"role": "user", "content": test_message}]
        )
        
        return response
    
    def get_available_genres(self) -> List[str]:
        """Get list of available genres
        
        Returns:
            List of available genre names
        """
        return ['All', 'Anime', 'Fantasy', 'Gaming', 'History', 
                'Literature', 'Music', 'Politics', 'Television']
        
        all_styles = self.get_chat_styles(genre, max_pages=3)
        
        # Sort by usage (popularity) 
        popular_styles = sorted(all_styles, key=lambda x: x.get("usage", 0), reverse=True)
        
        return popular_styles[:limit]
    
    def search_styles(
        self, 
        query: str, 
        genre: str = "Anime"
    ) -> List[ChatStyle]:
        """Search for chat styles by name or description
        
        Args:
            query: Search term
            genre: Genre to search in
            
        Returns:
            List of matching chat styles
        """
        
        all_styles = self.get_chat_styles(genre, max_pages=5)
        query_lower = query.lower()
        
        matching_styles = []
        for style in all_styles:
            if (query_lower in style.get("name", "").lower() or 
                query_lower in style.get("description", "").lower() or
                query_lower in style.get("url_handle", "").lower()):
                matching_styles.append(style)
        
        return matching_styles


class EnhancedDeepAI:
    """
    Enhanced DeepAI client with file upload support and additional features
    
    Supports:
    - File uploads with chat completions
    - Summary generation
    - Multiple models and chat styles
    - Session management
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepai.org"):
        self.api_key = api_key
        self.base_url = base_url
        self._chat_history = ChatHistory()
        self._default_hacker_is_stinky = "very_stinky"
    
    def create_with_file(
        self,
        messages: List[ChatCompletionMessage],
        model: str = "standard",
        chat_style: str = "chatgpt-alternative",
        file_upload: Optional[Union[str, bytes, BinaryIO]] = None,
        summary: bool = False,
        session_id: Optional[str] = None,
        **kwargs
    ) -> Union[ChatCompletion, ChatCompletionWithSummary]:
        """Create chat completion with optional file upload and summary
        
        Args:
            messages: Chat messages
            model: Model to use ('standard', 'online', 'math')
            chat_style: Chat style to use
            file_upload: Optional file to upload (path, bytes, or file object)
            summary: Whether to generate summary
            session_id: Session ID for chat history
            **kwargs: Additional parameters
            
        Returns:
            Chat completion response with optional summary
        """
        
        # Handle session-wise chat history
        if session_id:
            for message in messages:
                self._chat_history.add_message(session_id, message)
            chat_history = self._chat_history.get_history(session_id)
        else:
            chat_history = messages
        
        # Prepare the request
        url = f"{self.base_url}/hacking_is_a_serious_crime"
        headers = {}
        if self.api_key:
            headers["Api-Key"] = self.api_key
        
        # Prepare data
        data = {
            "chat_style": chat_style,
            "chatHistory": json.dumps(chat_history),
            "model": model,
            "hacker_is_stinky": self._default_hacker_is_stinky
        }
        if summary:
            data["summary"] = "true"
        data.update(kwargs)
        
        # Handle file upload
        files = None
        if file_upload:
            if isinstance(file_upload, str):
                # File path
                with open(file_upload, 'rb') as f:
                    files = {'file': f.read()}
            elif isinstance(file_upload, bytes):
                # Binary data
                files = {'file': file_upload}
            else:
                # File object
                files = {'file': file_upload.read()}
        
        # Make request
        if files:
            response = requests.post(url, data=data, files=files, headers=headers)
        else:
            response = requests.post(url, data=data, headers=headers)
        
        response.raise_for_status()
        
        # Parse response
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"output": response.text}
        
        # Create response
        completion_data = {
            "id": str(uuid.uuid4()),
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_data.get("output", response_data.get("text", str(response_data)))
                },
                "finish_reason": "stop"
            }],
            "usage": None
        }
        
        if summary and response_data.get("summary"):
            completion_data["summary"] = response_data["summary"]
            completion = ChatCompletionWithSummary(**completion_data)
        else:
            completion = ChatCompletion(**completion_data)
        
        # Add assistant response to session history
        if session_id:
            self._chat_history.add_message(session_id, completion["choices"][0]["message"])
        
        return completion
    
    def get_chat_history(self, session_id: str) -> List[ChatCompletionMessage]:
        """Get chat history for a session"""
        return self._chat_history.get_history(session_id)
    
    def clear_chat_history(self, session_id: str) -> None:
        """Clear chat history for a session"""
        self._chat_history.clear_session(session_id)


# Async versions
AsyncChatMath = ChatMath  # Placeholder for async versions
AsyncChatCode = ChatCode
AsyncTextToSpeech = TextToSpeech
AsyncImageGeneration = ImageGeneration
AsyncSpeechToText = SpeechToText
AsyncChatStyleManager = ChatStyleManager
AsyncEnhancedDeepAI = EnhancedDeepAI
