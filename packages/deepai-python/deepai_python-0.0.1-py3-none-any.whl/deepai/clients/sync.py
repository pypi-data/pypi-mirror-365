import requests
import json
import time
import uuid
from typing import Dict, List, Optional, Union, Any, Iterator
from ..utils.types import ChatCompletion, ChatCompletionMessage, ChatHistory


class ChatCompletions:
    """Chat completions resource"""
    
    def __init__(self, client):
        self._client = client
    
    def create(
        self,
        messages: List[ChatCompletionMessage],
        model: str = "standard",
        chat_style: str = "chatgpt-alternative",
        stream: bool = False,
        session_id: Optional[str] = None,
        **kwargs
    ) -> Union[ChatCompletion, Iterator[str]]:
        """Create a chat completion"""
        return self._client._create_chat_completion(
            messages=messages,
            model=model,
            chat_style=chat_style,
            stream=stream,
            session_id=session_id,
            **kwargs
        )


class Chat:
    """Chat resource"""
    
    def __init__(self, client):
        self.completions = ChatCompletions(client)


class DeepAI:
    """
    DeepAI API client for chat completions
    
    Supported models:
    - 'standard': General purpose model (default)
    - 'math': Mathematics-focused model
    - 'online': Online-aware model with current information
    - Custom models: Check API documentation for latest models
    
    Chat styles:
    - 'chatgpt-alternative': Default conversational style
    - 'ai-code': Programming and development focused
    - 'mathematics': Mathematical reasoning focused
    - 'goku', 'gojo_9': Character-based conversation styles
    - Many more: Use ChatStyleManager to discover all available styles
    
    Example:
        client = DeepAI()
        response = client.chat.completions.create(
            model="standard",
            chat_style="chatgpt-alternative",
            messages=[{"role": "user", "content": "Hello"}]
        )
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepai.org"):
        self.api_key = api_key
        self.base_url = base_url
        self.chat = Chat(self)
        self._chat_history = ChatHistory()
        
        # Default parameters
        self._default_hacker_is_stinky = "very_stinky"
    
    def _create_chat_completion(
        self,
        messages: List[ChatCompletionMessage],
        model: str = "standard",
        chat_style: str = "chatgpt-alternative",
        stream: bool = False,
        session_id: Optional[str] = None,
        **kwargs
    ) -> Union[ChatCompletion, Iterator[str]]:
        """Internal method to create chat completion"""
        
        # Handle session-wise chat history
        if session_id:
            # Add current messages to session history
            for message in messages:
                self._chat_history.add_message(session_id, message)
            
            # Get complete chat history for this session
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
        
        # Add any additional parameters
        data.update(kwargs)
        
        # Make the API request
        url = f"{self.base_url}/hacking_is_a_serious_crime"
        
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        if stream:
            return self._stream_completion(url, data, headers, session_id)
        else:
            return self._complete_completion(url, data, headers, session_id)
    
    def _complete_completion(
        self, 
        url: str, 
        data: Dict[str, Any], 
        headers: Dict[str, str],
        session_id: Optional[str] = None
    ) -> ChatCompletion:
        """Handle non-streaming completion"""
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        
        # Parse the response (adjust based on actual DeepAI response format)
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"output": response.text}
        
        # Create standardized response
        completion = ChatCompletion(
            id=str(uuid.uuid4()),
            object="chat.completion",
            created=int(time.time()),
            model=data.get("model", "standard"),
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
    
    def _stream_completion(
        self, 
        url: str, 
        data: Dict[str, Any], 
        headers: Dict[str, str],
        session_id: Optional[str] = None
    ) -> Iterator[str]:
        """Handle streaming completion"""
        response = requests.post(url, data=data, headers=headers, stream=True)
        response.raise_for_status()
        
        full_content = ""
        for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
            if chunk:
                full_content += chunk
                yield chunk
        
        # Add complete assistant response to session history
        if session_id and full_content:
            assistant_message = ChatCompletionMessage(
                role="assistant",
                content=full_content
            )
            self._chat_history.add_message(session_id, assistant_message)
    
    def get_chat_history(self, session_id: str) -> List[ChatCompletionMessage]:
        """Get chat history for a session"""
        return self._chat_history.get_history(session_id)
    
    def clear_chat_history(self, session_id: str) -> None:
        """Clear chat history for a session"""
        self._chat_history.clear_session(session_id)
