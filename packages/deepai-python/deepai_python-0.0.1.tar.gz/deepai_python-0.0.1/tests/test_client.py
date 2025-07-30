"""
Test basic client functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json

# Add src to path for testing
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from deepai import DeepAI


class TestDeepAIClient(unittest.TestCase):
    """Test the main DeepAI client"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = DeepAI()
        self.sample_messages = [
            {"role": "user", "content": "Hello, world!"}
        ]
    
    def test_client_initialization(self):
        """Test client initialization"""
        # Test default initialization
        client = DeepAI()
        self.assertIsNone(client.api_key)
        self.assertEqual(client.base_url, "https://api.deepai.org")
        
        # Test with API key
        client_with_key = DeepAI(api_key="test-key")
        self.assertEqual(client_with_key.api_key, "test-key")
        
        # Test with custom base URL
        custom_client = DeepAI(base_url="https://custom.api.com")
        self.assertEqual(custom_client.base_url, "https://custom.api.com")
    
    @patch('requests.post')
    def test_basic_chat_completion(self, mock_post):
        """Test basic chat completion"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"output": "Hello! How can I help you?"}
        mock_response.headers = {"content-type": "application/json"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Make request
        response = self.client.chat.completions.create(
            messages=self.sample_messages,
            model="standard",
            chat_style="chatgpt-alternative"
        )
        
        # Verify response structure
        self.assertIn("choices", response)
        self.assertIn("id", response)
        self.assertIn("model", response)
        self.assertEqual(len(response["choices"]), 1)
        self.assertEqual(response["choices"][0]["message"]["role"], "assistant")
        self.assertEqual(response["choices"][0]["message"]["content"], "Hello! How can I help you?")
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn("data", call_args.kwargs)
        
        # Check request data
        request_data = call_args.kwargs["data"]
        self.assertEqual(request_data["model"], "standard")
        self.assertEqual(request_data["chat_style"], "chatgpt-alternative")
        self.assertIn("chatHistory", request_data)
    
    @patch('requests.post')
    def test_different_models(self, mock_post):
        """Test different model support"""
        mock_response = Mock()
        mock_response.json.return_value = {"output": "Model response"}
        mock_response.headers = {"content-type": "application/json"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        models = ["standard", "online", "math"]
        
        for model in models:
            response = self.client.chat.completions.create(
                messages=self.sample_messages,
                model=model
            )
            
            self.assertEqual(response["model"], model)
    
    @patch('requests.post')
    def test_different_chat_styles(self, mock_post):
        """Test different chat style support"""
        mock_response = Mock()
        mock_response.json.return_value = {"output": "Style response"}
        mock_response.headers = {"content-type": "application/json"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        chat_styles = ["chatgpt-alternative", "goku", "ai-code", "mathematics"]
        
        for style in chat_styles:
            self.client.chat.completions.create(
                messages=self.sample_messages,
                chat_style=style
            )
            
            # Verify style was sent in request
            call_args = mock_post.call_args
            request_data = call_args.kwargs["data"]
            self.assertEqual(request_data["chat_style"], style)
    
    def test_session_management(self):
        """Test session management functionality"""
        session_id = "test_session"
        
        # Add messages to session
        for message in self.sample_messages:
            self.client._chat_history.add_message(session_id, message)
        
        # Get history
        history = self.client.get_chat_history(session_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["content"], "Hello, world!")
        
        # Clear session
        self.client.clear_chat_history(session_id)
        history = self.client.get_chat_history(session_id)
        self.assertEqual(len(history), 0)
    
    @patch('requests.post')
    def test_api_key_header(self, mock_post):
        """Test API key is sent in headers"""
        mock_response = Mock()
        mock_response.json.return_value = {"output": "Response"}
        mock_response.headers = {"content-type": "application/json"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Client with API key
        client_with_key = DeepAI(api_key="test-api-key")
        
        client_with_key.chat.completions.create(
            messages=self.sample_messages
        )
        
        # Check headers
        call_args = mock_post.call_args
        headers = call_args.kwargs.get("headers", {})
        self.assertEqual(headers.get("Authorization"), "Bearer test-api-key")
    
    @patch('requests.post')
    def test_error_handling(self, mock_post):
        """Test error handling"""
        # Mock HTTP error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_post.return_value = mock_response
        
        with self.assertRaises(Exception):
            self.client.chat.completions.create(
                messages=self.sample_messages
            )
    
    @patch('requests.post')
    def test_non_json_response(self, mock_post):
        """Test handling of non-JSON responses"""
        mock_response = Mock()
        mock_response.text = "Plain text response"
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        response = self.client.chat.completions.create(
            messages=self.sample_messages
        )
        
        self.assertEqual(
            response["choices"][0]["message"]["content"], 
            "Plain text response"
        )


class TestChatHistory(unittest.TestCase):
    """Test chat history functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        from deepai.utils.types import ChatHistory
        self.chat_history = ChatHistory()
        self.session_id = "test_session"
        self.sample_message = {"role": "user", "content": "Test message"}
    
    def test_add_message(self):
        """Test adding messages to session"""
        self.chat_history.add_message(self.session_id, self.sample_message)
        
        history = self.chat_history.get_history(self.session_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], self.sample_message)
    
    def test_multiple_sessions(self):
        """Test managing multiple sessions"""
        session1 = "session_1"
        session2 = "session_2"
        
        message1 = {"role": "user", "content": "Message 1"}
        message2 = {"role": "user", "content": "Message 2"}
        
        self.chat_history.add_message(session1, message1)
        self.chat_history.add_message(session2, message2)
        
        history1 = self.chat_history.get_history(session1)
        history2 = self.chat_history.get_history(session2)
        
        self.assertEqual(len(history1), 1)
        self.assertEqual(len(history2), 1)
        self.assertEqual(history1[0]["content"], "Message 1")
        self.assertEqual(history2[0]["content"], "Message 2")
    
    def test_clear_session(self):
        """Test clearing session history"""
        self.chat_history.add_message(self.session_id, self.sample_message)
        self.chat_history.clear_session(self.session_id)
        
        history = self.chat_history.get_history(self.session_id)
        self.assertEqual(len(history), 0)
    
    def test_clear_all(self):
        """Test clearing all sessions"""
        session1 = "session_1"
        session2 = "session_2"
        
        self.chat_history.add_message(session1, self.sample_message)
        self.chat_history.add_message(session2, self.sample_message)
        
        self.chat_history.clear_all()
        
        history1 = self.chat_history.get_history(session1)
        history2 = self.chat_history.get_history(session2)
        
        self.assertEqual(len(history1), 0)
        self.assertEqual(len(history2), 0)


if __name__ == "__main__":
    unittest.main()
