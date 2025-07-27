import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import requests
from translation import translate_text, translate_chunks, translate_file

class TranslationModuleTests(unittest.TestCase):
    
    @patch('translation.requests.post')
    @patch.dict(os.environ, {"GOOGLE_TRANSLATE_API_KEY": "fake_key"})
    def test_translate_text_with_api_key(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': {'translations': [{'translatedText': 'हैलो दुनिया'}]}}
        mock_post.return_value = mock_response
        
        result = translate_text("Hello world")
        
        # Verify API was called correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://translation.googleapis.com/language/translate/v2")
        self.assertEqual(kwargs['params']['q'], "Hello world")
        self.assertEqual(kwargs['params']['source'], "en")
        self.assertEqual(kwargs['params']['target'], "hi")
        self.assertEqual(kwargs['params']['key'], "fake_key")
        
        # Verify result
        self.assertEqual(result, "हैलो दुनिया")
    
    @patch('translation.requests.post')
    @patch.dict(os.environ, {"GOOGLE_TRANSLATE_API_KEY": "fake_key"})
    def test_translate_text_api_error(self, mock_post):
        # Setup mock to raise an exception
        mock_post.side_effect = requests.exceptions.RequestException("API Error")
        
        # Verify exception is propagated
        with self.assertRaises(requests.exceptions.RequestException):
            translate_text("Hello world")
    
    @patch('translation.Translator')
    @patch.dict(os.environ, {"GOOGLE_TRANSLATE_API_KEY": ""}, clear=True)
    def test_translate_text_with_googletrans(self, mock_translator_class):
        # Setup mock translator
        mock_translator = MagicMock()
        mock_result = MagicMock()
        mock_result.text = "हैलो दुनिया"
        mock_translator.translate.return_value = mock_result
        mock_translator_class.return_value = mock_translator
        
        result = translate_text("Hello world")
        
        # Verify translator was called correctly
        mock_translator.translate.assert_called_once_with("Hello world", src='en', dest='hi')
        
        # Verify result
        self.assertEqual(result, "हैलो दुनिया")
    
    @patch('translation.Translator')
    @patch('translation.logger')
    @patch.dict(os.environ, {"GOOGLE_TRANSLATE_API_KEY": ""}, clear=True)
    def test_translate_text_import_error(self, mock_logger, mock_translator_class):
        # Setup mock to raise ImportError
        mock_translator_class.side_effect = ImportError("No module named 'googletrans'")
        
        # Also need to mock requests since we'll fall back to API
        with patch('translation.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {'data': {'translations': [{'translatedText': 'हैलो दुनिया'}]}}
            mock_post.return_value = mock_response
            
            result = translate_text("Hello world")
            
            # Verify warnings were logged
            mock_logger.warning.assert_any_call("googletrans not installed, falling back to API translation")
    
    @patch('translation.translate_text')
    def test_translate_chunks(self, mock_translate_text):
        # Setup mock
        mock_translate_text.side_effect = lambda text: f"Translated: {text}"
        
        chunks = ["Chunk 1", "Chunk