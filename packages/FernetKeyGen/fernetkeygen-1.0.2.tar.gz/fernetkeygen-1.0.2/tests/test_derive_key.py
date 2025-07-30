import pytest
from unittest.mock import patch, MagicMock
import base64
from cryptography.fernet import Fernet
from FernetKeyGen.main import derive_key

class TestDeriveKey:

    @patch('FernetKeyGen.main.SaltManager')
    def test_derive_key_with_generate_salt_false(self, mock_salt_manager):
        """Test derive_key with generate_salt=False"""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.get.return_value = b'0123456789abcdef'
        mock_salt_manager.return_value = mock_instance

        # Call derive_key
        passphrase = 'test_passphrase'
        key = derive_key(passphrase, generate_salt=False)

        # Verify SaltManager was called correctly
        mock_salt_manager.assert_called_once_with(False, '.salt')
        mock_instance.get.assert_called_once()

        # Verify the key is a bytes object
        assert isinstance(key, bytes)

        # Verify key can be decoded as base64
        try:
            base64.urlsafe_b64decode(key)
        except Exception as e:
            pytest.fail(f"Key is not valid base64: {e}")

    @patch('FernetKeyGen.main.SaltManager')
    def test_derive_key_with_generate_salt_true(self, mock_salt_manager):
        """Test derive_key with generate_salt=True"""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.get.return_value = b'0123456789abcdef'
        mock_salt_manager.return_value = mock_instance

        # Call derive_key
        passphrase = 'test_passphrase'
        key = derive_key(passphrase, generate_salt=True)

        # Verify SaltManager was called correctly
        mock_salt_manager.assert_called_once_with(True, '.salt')
        mock_instance.get.assert_called_once()

        # Verify the key is a bytes object
        assert isinstance(key, bytes)

        # Verify key can be decoded as base64
        try:
            base64.urlsafe_b64decode(key)
        except Exception as e:
            pytest.fail(f"Key is not valid base64: {e}")

    @patch('FernetKeyGen.main.SaltManager')
    def test_derive_key_with_different_passphrases(self, mock_salt_manager):
        """Test derive_key with different passphrases"""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.get.return_value = b'0123456789abcdef'
        mock_salt_manager.return_value = mock_instance

        # Call derive_key with different passphrases
        passphrase1 = 'passphrase1'
        passphrase2 = 'passphrase2'

        key1 = derive_key(passphrase1)
        key2 = derive_key(passphrase2)

        # Verify keys are different
        assert key1 != key2

    @patch('FernetKeyGen.main.SaltManager')
    def test_derive_key_with_same_passphrase_different_salts(self, mock_salt_manager):
        """Test derive_key with the same passphrase but different salts"""
        # Setup mock for first call
        mock_instance1 = MagicMock()
        mock_instance1.get.return_value = b'0123456789abcdef'

        # Setup mock for second call
        mock_instance2 = MagicMock()
        mock_instance2.get.return_value = b'fedcba9876543210'

        # Configure mock_salt_manager to return different instances
        mock_salt_manager.side_effect = [mock_instance1, mock_instance2]

        # Call derive_key with the same passphrase
        passphrase = 'same_passphrase'

        key1 = derive_key(passphrase)
        key2 = derive_key(passphrase)

        # Verify keys are different
        assert key1 != key2

    @patch('FernetKeyGen.main.SaltManager')
    def test_derive_key_with_same_passphrase_same_salt(self, mock_salt_manager):
        """Test derive_key with same passphrase and same salt"""
        # Setup mocks to always return the same salt
        mock_instance = MagicMock()
        mock_instance.get.return_value = b'0123456789abcdef'
        mock_salt_manager.return_value = mock_instance

        # Call derive_key with the same passphrase twice
        passphrase = 'same_passphrase'

        key1 = derive_key(passphrase)
        key2 = derive_key(passphrase)

        # Verify keys are the same
        assert key1 == key2

    @patch('FernetKeyGen.main.SaltManager')
    def test_derive_key_with_empty_passphrase(self, mock_salt_manager):
        """Test derive_key with an empty passphrase"""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.get.return_value = b'0123456789abcdef'
        mock_salt_manager.return_value = mock_instance

        # Call derive_key with an empty passphrase
        passphrase = ''

        # This should work without errors and generate a random key
        key = derive_key(passphrase)

        # Verify the key is a bytes object
        assert isinstance(key, bytes)
        
    @patch('FernetKeyGen.main.SaltManager')
    def test_derive_key_with_non_string_passphrase(self, mock_salt_manager):
        """Test derive_key with a non-string passphrase (should raise AttributeError)"""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.get.return_value = b'0123456789abcdef'
        mock_salt_manager.return_value = mock_instance

        # Call derive_key with a non-string passphrase (integer)
        passphrase = 12345

        # This should raise an AttributeError because integers don't have an encode() method
        with pytest.raises(AttributeError):
            derive_key(passphrase)
            
    @patch('FernetKeyGen.main.SaltManager')
    def test_derive_key_cryptographic_properties(self, mock_salt_manager):
        """Test that the derived key has proper cryptographic properties for Fernet"""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.get.return_value = b'0123456789abcdef'
        mock_salt_manager.return_value = mock_instance

        # Call derive_key
        passphrase = 'test_passphrase'
        key = derive_key(passphrase)

        # Verify the key can be used with Fernet
        try:
            f = Fernet(key)
            message = b"Test message for encryption"
            token = f.encrypt(message)
            decrypted = f.decrypt(token)
            assert decrypted == message
        except Exception as e:
            pytest.fail(f"Key is not valid for Fernet: {e}")
            
    @patch('FernetKeyGen.main.SaltManager')
    def test_derive_key_with_very_long_passphrase(self, mock_salt_manager):
        """Test derive_key with a very long passphrase"""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.get.return_value = b'0123456789abcdef'
        mock_salt_manager.return_value = mock_instance

        # Call derive_key with a very long passphrase
        passphrase = 'x' * 10000  # 10,000 characters

        # This should work without errors
        key = derive_key(passphrase)

        # Verify the key is a bytes object
        assert isinstance(key, bytes)
        
        # Verify key can be decoded as base64
        try:
            base64.urlsafe_b64decode(key)
        except Exception as e:
            pytest.fail(f"Key is not valid base64: {e}")
            
    @patch('FernetKeyGen.main.SaltManager')
    def test_derive_key_with_unicode_passphrase(self, mock_salt_manager):
        """Test derive_key with a unicode passphrase"""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.get.return_value = b'0123456789abcdef'
        mock_salt_manager.return_value = mock_instance

        # Call derive_key with a unicode passphrase
        passphrase = "Unicode passphrase with special chars: 你好, こんにちは, 안녕하세요"

        # This should work without errors
        key = derive_key(passphrase)

        # Verify the key is a bytes object
        assert isinstance(key, bytes)
        
        # Verify key can be decoded as base64
        try:
            base64.urlsafe_b64decode(key)
        except Exception as e:
            pytest.fail(f"Key is not valid base64: {e}")
