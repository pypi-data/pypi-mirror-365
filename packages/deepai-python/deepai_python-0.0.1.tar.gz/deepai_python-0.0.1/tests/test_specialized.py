"""
Test specialized clients
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from deepai import ChatMath, ChatCode, TextToSpeech, ImageGeneration


class TestChatMath(unittest.TestCase):
    """Test ChatMath specialized client"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = ChatMath(api_key="test-key")
        self.sample_messages = [
            {"role": "user", "content": "What is 2 + 2?"}
        ]
    
    def test_initialization(self):
        """Test ChatMath initialization"""
        self.assertEqual(self.client.api_key, "test-key")
        self.assertEqual(self.client.base_url, "https://api.deepai.org")
    
    @patch('requests.post')
    def test_math_completion(self, mock_post):
        """Test math-focused completion"""
        mock_response = Mock()
        mock_response.json.return_value = {"output": "2 + 2 = 4"}
        mock_response.headers = {"content-type": "application/json"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        response = self.client.create(
            messages=self.sample_messages,
            model="math",
            chat_style="mathematics"
        )
        
        self.assertEqual(response["model"], "math")
        self.assertEqual(response["choices"][0]["message"]["content"], "2 + 2 = 4")
        
        # Verify API call
        call_args = mock_post.call_args
        request_data = call_args.kwargs["data"]
        self.assertEqual(request_data["model"], "math")
        self.assertEqual(request_data["chat_style"], "mathematics")
    
    @patch('requests.post')
    def test_api_key_header(self, mock_post):
        """Test API key is sent correctly"""
        mock_response = Mock()
        mock_response.json.return_value = {"output": "Result"}
        mock_response.headers = {"content-type": "application/json"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        self.client.create(messages=self.sample_messages)
        
        call_args = mock_post.call_args
        headers = call_args.kwargs.get("headers", {})
        self.assertEqual(headers.get("Api-Key"), "test-key")


class TestChatCode(unittest.TestCase):
    """Test ChatCode specialized client"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = ChatCode(api_key="test-key")
        self.sample_messages = [
            {"role": "user", "content": "Explain Python functions"}
        ]
    
    @patch('requests.post')
    def test_code_completion(self, mock_post):
        """Test code-focused completion"""
        mock_response = Mock()
        mock_response.json.return_value = {"output": "Functions are reusable blocks of code..."}
        mock_response.headers = {"content-type": "application/json"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        response = self.client.create(
            messages=self.sample_messages,
            model="standard",
            chat_style="ai-code"
        )
        
        self.assertEqual(response["model"], "standard")
        self.assertIn("Functions", response["choices"][0]["message"]["content"])
        
        # Verify default chat style
        call_args = mock_post.call_args
        request_data = call_args.kwargs["data"]
        self.assertEqual(request_data["chat_style"], "ai-code")


class TestTextToSpeech(unittest.TestCase):
    """Test TextToSpeech client"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = TextToSpeech(api_key="test-key")
    
    @patch('requests.post')
    def test_tts_creation(self, mock_post):
        """Test TTS creation"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "audio_url": "https://example.com/audio.wav",
            "id": "tts-123",
            "status": "completed"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        response = self.client.create(
            text="Hello, world!",
            model="aura-asteria-en"
        )
        
        self.assertEqual(response["audio_url"], "https://example.com/audio.wav")
        self.assertEqual(response["id"], "tts-123")
        self.assertEqual(response["status"], "completed")
        
        # Verify API call
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]["url"], "https://api.deepai.org/speech_response")
        
        request_data = call_args.kwargs["json"]
        self.assertEqual(request_data["text"], "Hello, world!")
        self.assertEqual(request_data["model"], "aura-asteria-en")


class TestImageGeneration(unittest.TestCase):
    """Test ImageGeneration client"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = ImageGeneration(api_key="test-key")
    
    @patch('requests.post')
    def test_image_generation(self, mock_post):
        """Test image generation"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "backend_request_id": "img-123",
            "id": "gen-456",
            "output_url": "https://example.com/image.jpg",
            "share_url": "https://example.com/share/123"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        response = self.client.create(
            text="A beautiful sunset",
            image_generator_version="hd",
            turbo="true"
        )
        
        self.assertEqual(response["output_url"], "https://example.com/image.jpg")
        self.assertEqual(response["id"], "gen-456")
        
        # Verify API call
        call_args = mock_post.call_args
        request_data = call_args.kwargs["data"]
        self.assertEqual(request_data["text"], "A beautiful sunset")
        self.assertEqual(request_data["image_generator_version"], "hd")
        self.assertEqual(request_data["turbo"], "true")
    
    @patch('requests.get')
    def test_save_image(self, mock_get):
        """Test image saving functionality"""
        # Mock image data
        mock_get.return_value.content = b"fake_image_data"
        
        image_response = {
            "backend_request_id": "img-123",
            "id": "gen-456",
            "output_url": "https://example.com/image.jpg",
            "share_url": "https://example.com/share/123"
        }
        
        # Mock file operations
        with patch('builtins.open', create=True) as mock_open:
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            result = self.client.save_image(image_response, "test_image.jpg")
            
            self.assertTrue(result)
            mock_file.write.assert_called_once_with(b"fake_image_data")
            mock_open.assert_called_once_with("test_image.jpg", "wb")


if __name__ == "__main__":
    unittest.main()
