import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys
from io import StringIO

# Import the module to test
import main

class TestMain(unittest.TestCase):
    
    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_arguments(self, mock_parse_args):
        # Setup mock return value
        mock_args = MagicMock()
        mock_args.input = 'test_input.txt'
        mock_args.output = 'test_output.txt'
        mock_args.verbose = True
        mock_parse_args.return_value = mock_args
        
        # Call the function
        args = main.parse_arguments()
        
        # Assert results
        self.assertEqual(args.input, 'test_input.txt')
        self.assertEqual(args.output, 'test_output.txt')
        self.assertTrue(args.verbose)
        
    @patch('main.setup_logging')
    @patch('main.validate_file')
    @patch('main.translate_file')
    @patch('main.parse_arguments')
    def test_main_success(self, mock_parse_args, mock_translate_file, mock_validate_file, mock_setup_logging):
        # Setup mocks
        mock_args = MagicMock()
        mock_args.input = 'test_input.txt'
        mock_args.output = 'test_output.txt'
        mock_args.verbose = False
        mock_parse_args.return_value = mock_args
        
        mock_logger = MagicMock()
        mock_setup_logging.return_value = mock_logger
        
        mock_validate_file.return_value = True
        
        # Call the function
        result = main.main()
        
        # Assert results
        self.assertEqual(result, 0)
        mock_setup_logging.assert_called_once_with(False)
        mock_validate_file.assert_called_once_with('test_input.txt')
        mock_translate_file.assert_called_once_with('test_input.txt', 'test_output.txt')
        mock_logger.info.assert_any_call('Translating test_input.txt to test_output.txt')
        mock_logger.info.assert_any_call('Translation completed successfully')
        
    @patch('main.setup_logging')
    @patch('main.validate_file')
    @patch('main.parse_arguments')
    def test_main_invalid_file(self, mock_parse_args, mock_validate_file, mock_setup_logging):
        # Setup mocks
        mock_args = MagicMock()
        mock_args.input = 'nonexistent.txt'
        mock_args.output = 'test_output.txt'
        mock_args.verbose = False
        mock_parse_args.return_value = mock_args
        
        mock_logger = MagicMock()
        mock_setup_logging.return_value = mock_logger
        
        mock_validate_file.return_value = False
        
        # Call the function
        result = main.main()
        
        # Assert results
        self.assertEqual(result, 1)
        mock_setup_logging.assert_called_once_with(False)
        mock_validate_file.assert_called_once_with('nonexistent.txt')
        mock_logger.error.assert_called_once()
        
    @patch('main.setup_logging')
    @patch('main.validate_file')
    @patch('main.translate_file')
    @patch('main.parse_arguments')
    def test_main_translation_failure(self, mock_parse_args, mock_translate_file, mock_validate_file, mock_setup_logging):
        # Setup mocks
        mock_args = MagicMock()
        mock_args.input = 'test_input.txt'
        mock_args.output = 'test_output.txt'
        mock_args.verbose = False
        mock_parse_args.return_value = mock_args
        
        mock_logger = Magic