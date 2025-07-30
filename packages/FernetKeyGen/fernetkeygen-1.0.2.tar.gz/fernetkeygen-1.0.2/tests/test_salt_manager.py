import os
import pytest
from unittest.mock import mock_open, patch
from FernetKeyGen.SaltManager import SaltManager

class TestSaltManager:
    
    def test_init(self):
        """Test SaltManager initialization"""
        # Test with a default path
        sm = SaltManager(generate=False)
        assert sm.generate is False
        assert sm.path == '.salt'
        
        # Test with a custom path
        custom_path = 'custom_salt_path'
        sm = SaltManager(generate=True, path=custom_path)
        assert sm.generate is True
        assert sm.path == custom_path
    
    @patch('os.urandom')
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_and_store(self, mock_file, mock_urandom):
        """Test salt generation and storage"""
        # Mock os.urandom to return a predictable value
        expected_salt = b'0123456789abcdef'
        mock_urandom.return_value = expected_salt
        
        # Create SaltManager and call _generate_and_store
        sm = SaltManager(generate=True)
        salt = sm._generate_and_store()
        
        # Verify salt is correct
        assert salt == expected_salt
        
        # Verify file operations
        mock_file.assert_called_once_with('.salt', 'wb')
        mock_file().write.assert_called_once_with(expected_salt)
    
    @patch('builtins.open', new_callable=mock_open, read_data=b'0123456789abcdef')
    def test_read(self, mock_file):
        """Test reading salt from a file"""
        # Create SaltManager and call _read
        sm = SaltManager(generate=False)
        salt = sm._read()
        
        # Verify salt is correct
        assert salt == b'0123456789abcdef'
        
        # Verify file operations
        mock_file.assert_called_once_with('.salt', 'rb')
    
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_read_file_not_found(self, mock_file):
        """Test reading salt when a file doesn't exist"""
        # Create SaltManager
        sm = SaltManager(generate=False)
        
        # Verify FileNotFoundError is raised
        with pytest.raises(FileNotFoundError):
            sm._read()
    
    @patch('os.urandom')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_with_generate_true(self, mock_file, mock_urandom):
        """Test get method with generate=True"""
        # Mock os.urandom to return a predictable value
        expected_salt = b'0123456789abcdef'
        mock_urandom.return_value = expected_salt
        
        # Create SaltManager and call get
        sm = SaltManager(generate=True)
        salt = sm.get()
        
        # Verify salt is correct
        assert salt == expected_salt
        
        # Verify file operations
        mock_file.assert_called_once_with('.salt', 'wb')
        mock_file().write.assert_called_once_with(expected_salt)
    
    @patch('builtins.open', new_callable=mock_open, read_data=b'0123456789abcdef')
    def test_get_with_generate_false(self, mock_file):
        """Test get method with generate=False"""
        # Create SaltManager and call get
        sm = SaltManager(generate=False)
        salt = sm.get()
        
        # Verify salt is correct
        assert salt == b'0123456789abcdef'
        
        # Verify file operations
        mock_file.assert_called_once_with('.salt', 'rb')