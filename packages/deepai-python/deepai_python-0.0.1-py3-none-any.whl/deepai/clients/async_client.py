import aiohttp
import asyncio
import json
import time
import uuid
from typing import Dict, List, Optional, Union, Any, AsyncIterator
from ..utils.types import ChatCompletion, ChatCompletionMessage, ChatHistory


class AsyncChatCompletions:
    """Async chat completions resource"""
    
    def __init__(self, client):
        self._client = client
    
    async def create(
        self,
        messages: List[ChatCompletionMessage],
        model: str = "standard",
        chat_style: str = "chatgpt-alternative",
        stream: bool = False,
        session_id: Optional[str] = None,
        **kwargs
    ) -> Union[ChatCompletion, AsyncIterator[str]]:
        """Create a chat completion asynchronously"""
        return await self._client._create_chat_completion(
            messages=messages,
            model=model,
            chat_style=chat_style,
            stream=stream,
            session_id=session_id,
            **kwargs
        )


class AsyncChat:
    """Async chat resource"""
    
    def __init__(self, client):
        self.completions = AsyncChatCompletions(client)


class AsyncDeepAI:
    """Async DeepAI API client"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepai.org"):
        self.api_key = api_key
        self.base_url = base_url
        self.chat = AsyncChat(self)
        self._chat_history = ChatHistory()
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Default parameters
        self._default_hacker_is_stinky = "very_stinky"
    
    async def __aenter__(self):
        """Async context manager entry"""
        self._session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._session:
            await self._session.close()
    
    def _get_session(self) -> aiohttp.ClientSession:
        """Get or create session"""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def _create_chat_completion(
        self,
        messages: List[ChatCompletionMessage],
        model: str = "standard",
        chat_style: str = "chatgpt-alternative",
        stream: bool = False,
        session_id: Optional[str] = None,
        **kwargs
    ) -> Union[ChatCompletion, AsyncIterator[str]]:
        """Internal method to create chat completion asynchronously"""
        
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
        data = aiohttp.FormData()
        data.add_field("chat_style", chat_style)
        data.add_field("chatHistory", json.dumps(chat_history))
        data.add_field("model", model)
        data.add_field("hacker_is_stinky", self._default_hacker_is_stinky)
        
        # Add any additional parameters
        for key, value in kwargs.items():
            data.add_field(key, str(value))
        
        # Prepare headers
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        url = f"{self.base_url}/hacking_is_a_serious_crime"
        
        if stream:
            return self._stream_completion(url, data, headers, session_id)
        else:
            return await self._complete_completion(url, data, headers, session_id)
    
    async def _complete_completion(
        self, 
        url: str, 
        data: aiohttp.FormData, 
        headers: Dict[str, str],
        session_id: Optional[str] = None
    ) -> ChatCompletion:
        """Handle non-streaming completion asynchronously"""
        session = self._get_session()
        
        async with session.post(url, data=data, headers=headers) as response:
            response.raise_for_status()
            
            # Parse the response
            content_type = response.headers.get('content-type', '')
            if content_type.startswith('application/json'):
                response_data = await response.json()
            else:
                response_text = await response.text()
                response_data = {"output": response_text}
        
        # Create standardized response
        completion = ChatCompletion(
            id=str(uuid.uuid4()),
            object="chat.completion",
            created=int(time.time()),
            model=data._fields[2][1],  # model field
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
    
    async def _stream_completion(
        self, 
        url: str, 
        data: aiohttp.FormData, 
        headers: Dict[str, str],
        session_id: Optional[str] = None
    ) -> AsyncIterator[str]:
        """Handle streaming completion asynchronously"""
        session = self._get_session()
        
        full_content = ""
        async with session.post(url, data=data, headers=headers) as response:
            response.raise_for_status()
            
            async for chunk in response.content.iter_chunked(8192):
                if chunk:
                    chunk_text = chunk.decode('utf-8', errors='ignore')
                    full_content += chunk_text
                    yield chunk_text
        
        # Add complete assistant response to session history
        if session_id and full_content:
            assistant_message = ChatCompletionMessage(
                role="assistant",
                content=full_content
            )
            self._chat_history.add_message(session_id, assistant_message)
    
    async def get_chat_history(self, session_id: str) -> List[ChatCompletionMessage]:
        """Get chat history for a session"""
        return self._chat_history.get_history(session_id)
    
    async def clear_chat_history(self, session_id: str) -> None:
        """Clear chat history for a session"""
        self._chat_history.clear_session(session_id)
    
    async def close(self):
        """Close the session"""
        if self._session:
            await self._session.close()
