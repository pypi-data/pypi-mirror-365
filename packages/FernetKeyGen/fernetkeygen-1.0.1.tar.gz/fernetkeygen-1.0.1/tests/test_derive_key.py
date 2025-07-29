import pytest
from unittest.mock import patch, MagicMock
import base64
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
        passphrase = b'test_passphrase'
        key = derive_key(passphrase, generate_salt=False)

        # Verify SaltManager was called correctly
        mock_salt_manager.assert_called_once_with(False)
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
        passphrase = b'test_passphrase'
        key = derive_key(passphrase, generate_salt=True)

        # Verify SaltManager was called correctly
        mock_salt_manager.assert_called_once_with(True)
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
        passphrase1 = b'passphrase1'
        passphrase2 = b'passphrase2'

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
        passphrase = b'same_passphrase'

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
        passphrase = b'same_passphrase'

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
        passphrase = b''

        # This should work without errors
        key = derive_key(passphrase)

        # Verify the key is a bytes object
        assert isinstance(key, bytes)
