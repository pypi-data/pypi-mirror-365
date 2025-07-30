from typing import Dict, List, Optional, Union, Any
from typing_extensions import TypedDict, Literal


class ChatCompletionMessage(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatCompletionChoice(TypedDict):
    index: int
    message: ChatCompletionMessage
    finish_reason: Optional[str]


class ChatCompletion(TypedDict):
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Optional[Dict[str, Any]]


class TTSResponse(TypedDict):
    audio_url: str
    id: str
    status: str


class STTResponse(TypedDict):
    text: str
    usage: Dict[str, Any]


class ImageResponse(TypedDict):
    backend_request_id: str
    id: str
    output_url: str
    share_url: str


class ChatStyle(TypedDict):
    id: int
    url_handle: str
    name: str
    description: str
    genre: str
    usage: int
    image: str


class ChatCompletionWithSummary(TypedDict):
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Optional[Dict[str, Any]]
    summary: Optional[str]


class ErrorResponse(TypedDict):
    error: str
    code: Optional[str]
    message: Optional[str]


class ChatHistory:
    """Session-wise chat history storage"""
    
    def __init__(self):
        self._sessions: Dict[str, List[ChatCompletionMessage]] = {}
    
    def add_message(self, session_id: str, message: ChatCompletionMessage) -> None:
        """Add a message to the session history"""
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append(message)
    
    def get_history(self, session_id: str) -> List[ChatCompletionMessage]:
        """Get chat history for a session"""
        return self._sessions.get(session_id, [])
    
    def clear_session(self, session_id: str) -> None:
        """Clear history for a specific session"""
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    def clear_all(self) -> None:
        """Clear all session histories"""
        self._sessions.clear()
