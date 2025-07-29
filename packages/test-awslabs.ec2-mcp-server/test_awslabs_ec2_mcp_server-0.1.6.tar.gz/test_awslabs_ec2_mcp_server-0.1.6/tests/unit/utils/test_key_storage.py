"""
Tests for EC2 MCP Server key storage utilities.
"""

import json
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from cryptography.fernet import Fernet

from awslabs.ec2_mcp_server.utils.key_storage import KeyStorageManager
from awslabs.ec2_mcp_server.utils.aws import AWSClientManager


class TestKeyStorageManager:
    """Test cases for KeyStorageManager class."""

    @pytest.fixture
    def mock_aws_client(self):
        """Create a mock AWS client manager."""
        client = MagicMock(spec=AWSClientManager)
        return client

    @pytest.fixture
    def config(self):
        """Test configuration."""
        return {
            "aws_region": "us-east-1",
            "encryption_salt": "test-salt-123",
            "s3_keypair_bucket": "test-bucket",
            "s3_keypair_prefix": "test-prefix"
        }

    @pytest.fixture
    def key_storage_manager(self, mock_aws_client, config):
        """Create KeyStorageManager instance."""
        return KeyStorageManager(mock_aws_client, config)

    @pytest.fixture
    def sample_private_key(self):
        """Sample private key material."""
        return "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA...\n-----END RSA PRIVATE KEY-----"

    def test_init(self, mock_aws_client, config):
        """Test KeyStorageManager initialization."""
        manager = KeyStorageManager(mock_aws_client, config)
        assert manager.aws_client == mock_aws_client
        assert manager.config == config
        assert manager.region == "us-east-1"

    def test_init_default_region(self, mock_aws_client):
        """Test initialization with default region."""
        config = {}
        manager = KeyStorageManager(mock_aws_client, config)
        assert manager.region == "us-east-1"

    def test_storage_methods_constant(self):
        """Test STORAGE_METHODS constant."""
        expected_methods = {
            "secrets_manager": "AWS Secrets Manager",
            "s3_encrypted": "Encrypted S3 Storage", 
            "parameter_store": "AWS Systems Manager Parameter Store"
        }
        assert KeyStorageManager.STORAGE_METHODS == expected_methods

    def test_generate_encryption_key(self, key_storage_manager):
        """Test encryption key generation."""
        key_name = "test-key"
        encryption_key = key_storage_manager._generate_encryption_key(key_name)
        
        assert isinstance(encryption_key, bytes)
        assert len(encryption_key) == 44  # Base64 encoded 32-byte key
        
        # Should be deterministic
        key2 = key_storage_manager._generate_encryption_key(key_name)
        assert encryption_key == key2

    def test_generate_encryption_key_different_names(self, key_storage_manager):
        """Test that different key names generate different encryption keys."""
        key1 = key_storage_manager._generate_encryption_key("key1")
        key2 = key_storage_manager._generate_encryption_key("key2")
        assert key1 != key2

    @patch('awslabs.ec2_mcp_server.utils.key_storage.logger')
    def test_generate_encryption_key_default_salt_warning(self, mock_logger, mock_aws_client):
        """Test warning for default salt usage."""
        config = {"aws_region": "us-east-1"}
        manager = KeyStorageManager(mock_aws_client, config)
        manager._generate_encryption_key("test-key")
        mock_logger.warning.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_private_key_secrets_manager(self, key_storage_manager, sample_private_key):
        """Test storing private key in Secrets Manager."""
        mock_secrets_client = MagicMock()
        mock_secrets_client.create_secret.return_value = {"ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:test"}
        key_storage_manager.aws_client.get_client.return_value = mock_secrets_client

        result = await key_storage_manager.store_private_key(
            "test-key", sample_private_key, "secrets_manager"
        )

        assert result["status"] == "success"
        assert result["storage_method"] == "secrets_manager"
        assert result["storage_location"] == "ec2/keypairs/test-key"
        assert "secret_arn" in result
        
        mock_secrets_client.create_secret.assert_called_once()
        call_args = mock_secrets_client.create_secret.call_args[1]
        assert call_args["Name"] == "ec2/keypairs/test-key"
        assert "private_key" in json.loads(call_args["SecretString"])

    @pytest.mark.asyncio
    async def test_store_private_key_s3_encrypted(self, key_storage_manager, sample_private_key):
        """Test storing private key in S3 with KMS encryption."""
        mock_s3_client = MagicMock()
        key_storage_manager.aws_client.get_client.return_value = mock_s3_client

        result = await key_storage_manager.store_private_key(
            "test-key", sample_private_key, "s3_encrypted"
        )

        assert result["status"] == "success"
        assert result["storage_method"] == "s3_encrypted"
        assert result["bucket"] == "test-bucket"
        assert result["key"] == "test-prefix/test-key.pem"
        assert result["encryption"] == "KMS"
        assert result["kms_key"] == "aws/s3 (default)"
        
        mock_s3_client.put_object.assert_called_once()
        call_args = mock_s3_client.put_object.call_args[1]
        assert call_args["Bucket"] == "test-bucket"
        assert call_args["Key"] == "test-prefix/test-key.pem"
        assert call_args["ServerSideEncryption"] == "aws:kms"
        assert "SSEKMSKeyId" not in call_args  # Should use default aws/s3 key
        assert call_args["ContentType"] == "application/x-pem-file"
        assert "Tagging" not in call_args  # No tags provided

    @pytest.mark.asyncio
    async def test_store_private_key_s3_encrypted_default_bucket(self, mock_aws_client):
        """Test S3 storage with default bucket configuration."""
        config = {"aws_region": "us-west-2"}
        manager = KeyStorageManager(mock_aws_client, config)
        mock_s3_client = MagicMock()
        manager.aws_client.get_client.return_value = mock_s3_client

        await manager.store_private_key("test-key", "key-content", "s3_encrypted")

        call_args = mock_s3_client.put_object.call_args[1]
        assert call_args["Bucket"] == "ec2-mcp-keypairs-us-west-2"
        assert call_args["Key"] == "private-keys/test-key.pem"
        assert call_args["ServerSideEncryption"] == "aws:kms"
        assert "Tagging" not in call_args  # No tags provided

    @pytest.mark.asyncio
    async def test_store_private_key_s3_encrypted_custom_kms_key(self, mock_aws_client):
        """Test S3 storage with custom KMS key."""
        config = {
            "aws_region": "us-west-2",
            "kms_key_id": "arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789012"
        }
        manager = KeyStorageManager(mock_aws_client, config)
        mock_s3_client = MagicMock()
        manager.aws_client.get_client.return_value = mock_s3_client

        result = await manager.store_private_key("test-key", "key-content", "s3_encrypted")

        assert result["kms_key"] == "arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789012"
        call_args = mock_s3_client.put_object.call_args[1]
        assert call_args["ServerSideEncryption"] == "aws:kms"
        assert call_args["SSEKMSKeyId"] == "arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789012"

    @pytest.mark.asyncio
    async def test_store_private_key_s3_encrypted_with_tags(self, mock_aws_client):
        """Test S3 storage with tags."""
        config = {"aws_region": "us-west-2"}
        manager = KeyStorageManager(mock_aws_client, config)
        mock_s3_client = MagicMock()
        manager.aws_client.get_client.return_value = mock_s3_client

        tags = {"Environment": "test", "Project": "ec2-mcp", "Owner": "test-user"}
        result = await manager.store_private_key(
            "test-key", "key-content", "s3_encrypted", tags=tags
        )

        assert result["status"] == "success"
        call_args = mock_s3_client.put_object.call_args[1]
        assert call_args["Bucket"] == "ec2-mcp-keypairs-us-west-2"
        assert call_args["Key"] == "private-keys/test-key.pem"
        assert call_args["ServerSideEncryption"] == "aws:kms"
        
        # Verify tags are properly encoded
        assert "Tagging" in call_args
        expected_tags = "Environment=test&Project=ec2-mcp&Owner=test-user"
        assert call_args["Tagging"] == expected_tags

    @pytest.mark.asyncio
    async def test_store_private_key_s3_encrypted_with_special_char_tags(self, mock_aws_client):
        """Test S3 storage with tags containing special characters."""
        config = {"aws_region": "us-west-2"}
        manager = KeyStorageManager(mock_aws_client, config)
        mock_s3_client = MagicMock()
        manager.aws_client.get_client.return_value = mock_s3_client

        tags = {"Environment": "test & dev", "Project": "ec2-mcp+server"}
        await manager.store_private_key(
            "test-key", "key-content", "s3_encrypted", tags=tags
        )

        call_args = mock_s3_client.put_object.call_args[1]
        # Verify special characters are URL encoded
        assert "Tagging" in call_args
        expected_tags = "Environment=test%20%26%20dev&Project=ec2-mcp%2Bserver"
        assert call_args["Tagging"] == expected_tags

    @pytest.mark.asyncio
    async def test_store_private_key_parameter_store(self, key_storage_manager, sample_private_key):
        """Test storing private key in Parameter Store."""
        mock_ssm_client = MagicMock()
        key_storage_manager.aws_client.get_client.return_value = mock_ssm_client

        result = await key_storage_manager.store_private_key(
            "test-key", sample_private_key, "parameter_store"
        )

        assert result["status"] == "success"
        assert result["storage_method"] == "parameter_store"
        assert result["storage_location"] == "/ec2/keypairs/test-key/private-key"
        
        mock_ssm_client.put_parameter.assert_called_once()
        call_args = mock_ssm_client.put_parameter.call_args[1]
        assert call_args["Name"] == "/ec2/keypairs/test-key/private-key"
        assert call_args["Value"] == sample_private_key
        assert call_args["Type"] == "SecureString"
        assert call_args["Overwrite"] is False

    @pytest.mark.asyncio
    async def test_store_private_key_unsupported_method(self, key_storage_manager, sample_private_key):
        """Test error handling for unsupported storage method."""
        result = await key_storage_manager.store_private_key(
            "test-key", sample_private_key, "unsupported_method"
        )
        
        assert result["status"] == "error"
        assert "Unsupported storage method" in result["message"]

    @pytest.mark.asyncio
    async def test_store_private_key_secrets_manager_with_tags(self, key_storage_manager, sample_private_key):
        """Test storing private key in Secrets Manager with tags."""
        mock_secrets_client = MagicMock()
        mock_secrets_client.create_secret.return_value = {"ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:test"}
        key_storage_manager.aws_client.get_client.return_value = mock_secrets_client

        tags = {"Environment": "test", "Owner": "test-user"}
        await key_storage_manager.store_private_key(
            "test-key", sample_private_key, "secrets_manager", tags=tags
        )

        call_args = mock_secrets_client.create_secret.call_args[1]
        assert "Tags" in call_args
        expected_tags = [{"Key": "Environment", "Value": "test"}, {"Key": "Owner", "Value": "test-user"}]
        assert call_args["Tags"] == expected_tags

    @pytest.mark.asyncio
    async def test_store_private_key_parameter_store_with_tags(self, key_storage_manager, sample_private_key):
        """Test storing private key in Parameter Store with tags."""
        mock_ssm_client = MagicMock()
        key_storage_manager.aws_client.get_client.return_value = mock_ssm_client

        tags = {"Environment": "test"}
        await key_storage_manager.store_private_key(
            "test-key", sample_private_key, "parameter_store", tags=tags
        )

        call_args = mock_ssm_client.put_parameter.call_args[1]
        assert "Tags" in call_args
        expected_tags = [{"Key": "Environment", "Value": "test"}]
        assert call_args["Tags"] == expected_tags

    @pytest.mark.asyncio
    async def test_store_private_key_exception_handling(self, key_storage_manager, sample_private_key):
        """Test exception handling during storage."""
        mock_secrets_client = MagicMock()
        mock_secrets_client.create_secret.side_effect = Exception("AWS Error")
        key_storage_manager.aws_client.get_client.return_value = mock_secrets_client

        result = await key_storage_manager.store_private_key(
            "test-key", sample_private_key, "secrets_manager"
        )

        assert result["status"] == "error"
        assert "Failed to store private key" in result["message"]

    @pytest.mark.asyncio
    async def test_delete_stored_key_secrets_manager(self, key_storage_manager):
        """Test deleting stored key from Secrets Manager."""
        mock_secrets_client = MagicMock()
        key_storage_manager.aws_client.get_client.return_value = mock_secrets_client

        result = await key_storage_manager.delete_stored_key(
            "test-key", "secrets_manager", "ec2/keypairs/test-key"
        )

        assert result["status"] == "success"
        assert "Secret deleted" in result["message"]
        mock_secrets_client.delete_secret.assert_called_once_with(
            SecretId="ec2/keypairs/test-key", ForceDeleteWithoutRecovery=True
        )

    @pytest.mark.asyncio
    async def test_delete_stored_key_s3_encrypted(self, key_storage_manager):
        """Test deleting stored key from S3."""
        mock_s3_client = MagicMock()
        key_storage_manager.aws_client.get_client.return_value = mock_s3_client

        result = await key_storage_manager.delete_stored_key(
            "test-key", "s3_encrypted", "s3://test-bucket/test-prefix/test-key.encrypted"
        )

        assert result["status"] == "success"
        assert "Encrypted key deleted" in result["message"]
        mock_s3_client.delete_object.assert_called_once_with(
            Bucket="test-bucket", Key="test-prefix/test-key.encrypted"
        )

    @pytest.mark.asyncio
    async def test_delete_stored_key_parameter_store(self, key_storage_manager):
        """Test deleting stored key from Parameter Store."""
        mock_ssm_client = MagicMock()
        key_storage_manager.aws_client.get_client.return_value = mock_ssm_client

        result = await key_storage_manager.delete_stored_key(
            "test-key", "parameter_store", "/ec2/keypairs/test-key/private-key"
        )

        assert result["status"] == "success"
        assert "Parameter deleted" in result["message"]
        mock_ssm_client.delete_parameter.assert_called_once_with(
            Name="/ec2/keypairs/test-key/private-key"
        )

    @pytest.mark.asyncio
    async def test_delete_stored_key_unsupported_method(self, key_storage_manager):
        """Test error handling for unsupported deletion method."""
        result = await key_storage_manager.delete_stored_key(
            "test-key", "unsupported_method", "location"
        )
        
        assert result["status"] == "error"
        assert "Unsupported storage method" in result["message"]

    @pytest.mark.asyncio
    async def test_delete_stored_key_exception_handling(self, key_storage_manager):
        """Test exception handling during deletion."""
        mock_secrets_client = MagicMock()
        mock_secrets_client.delete_secret.side_effect = Exception("AWS Error")
        key_storage_manager.aws_client.get_client.return_value = mock_secrets_client

        result = await key_storage_manager.delete_stored_key(
            "test-key", "secrets_manager", "ec2/keypairs/test-key"
        )

        assert result["status"] == "error"
        assert "Failed to delete stored key" in result["message"]

    @pytest.mark.asyncio
    async def test_store_in_secrets_manager_with_description(self, key_storage_manager, sample_private_key):
        """Test storing in Secrets Manager with custom description."""
        mock_secrets_client = MagicMock()
        mock_secrets_client.create_secret.return_value = {"ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:test"}
        key_storage_manager.aws_client.get_client.return_value = mock_secrets_client

        result = await key_storage_manager._store_in_secrets_manager(
            "test-key", sample_private_key, description="Custom description"
        )

        call_args = mock_secrets_client.create_secret.call_args[1]
        assert call_args["Description"] == "Custom description"

    @pytest.mark.asyncio
    async def test_store_in_s3_encrypted_with_custom_bucket(self, key_storage_manager, sample_private_key):
        """Test S3 storage with custom bucket and prefix."""
        mock_s3_client = MagicMock()
        key_storage_manager.aws_client.get_client.return_value = mock_s3_client

        result = await key_storage_manager._store_in_s3_encrypted(
            "test-key", sample_private_key, bucket_name="custom-bucket", key_prefix="custom-prefix"
        )

        call_args = mock_s3_client.put_object.call_args[1]
        assert call_args["Bucket"] == "custom-bucket"
        assert call_args["Key"] == "custom-prefix/test-key.encrypted"
        assert result["bucket"] == "custom-bucket"

    @pytest.mark.asyncio
    async def test_store_in_parameter_store_with_custom_name(self, key_storage_manager, sample_private_key):
        """Test Parameter Store storage with custom parameter name."""
        mock_ssm_client = MagicMock()
        key_storage_manager.aws_client.get_client.return_value = mock_ssm_client

        result = await key_storage_manager._store_in_parameter_store(
            "test-key", sample_private_key, parameter_name="/custom/param/name"
        )

        call_args = mock_ssm_client.put_parameter.call_args[1]
        assert call_args["Name"] == "/custom/param/name"
        assert result["storage_location"] == "/custom/param/name"

    @pytest.mark.asyncio
    async def test_encryption_key_validation(self, key_storage_manager, sample_private_key):
        """Test that encryption key is valid for Fernet."""
        encryption_key = key_storage_manager._generate_encryption_key("test-key")
        
        # Should be able to create Fernet cipher with the key
        fernet = Fernet(encryption_key)
        
        # Should be able to encrypt and decrypt
        encrypted = fernet.encrypt(sample_private_key.encode())
        decrypted = fernet.decrypt(encrypted).decode()
        assert decrypted == sample_private_key

    @pytest.mark.asyncio
    async def test_s3_encryption_flow(self, key_storage_manager, sample_private_key):
        """Test the complete S3 encryption flow."""
        mock_s3_client = MagicMock()
        key_storage_manager.aws_client.get_client.return_value = mock_s3_client

        await key_storage_manager._store_in_s3_encrypted("test-key", sample_private_key)

        # Verify that the data passed to S3 is encrypted
        call_args = mock_s3_client.put_object.call_args[1]
        encrypted_data = call_args["Body"]
        
        # Should not be the original private key
        assert encrypted_data != sample_private_key.encode()
        
        # Should be able to decrypt with the same encryption key
        encryption_key = key_storage_manager._generate_encryption_key("test-key")
        fernet = Fernet(encryption_key)
        decrypted = fernet.decrypt(encrypted_data).decode()
        assert decrypted == sample_private_key

    @pytest.mark.asyncio
    async def test_s3_metadata(self, key_storage_manager, sample_private_key):
        """Test S3 metadata is set correctly."""
        mock_s3_client = MagicMock()
        key_storage_manager.aws_client.get_client.return_value = mock_s3_client

        await key_storage_manager._store_in_s3_encrypted("test-key", sample_private_key)

        call_args = mock_s3_client.put_object.call_args[1]
        metadata = call_args["Metadata"]
        
        assert metadata["key-name"] == "test-key"
        assert metadata["created-by"] == "ec2-mcp-server"
        assert metadata["encryption-method"] == "fernet"
        assert call_args["ContentType"] == "application/octet-stream"

    @pytest.mark.asyncio
    async def test_secrets_manager_secret_value_structure(self, key_storage_manager, sample_private_key):
        """Test the structure of secret value stored in Secrets Manager."""
        mock_secrets_client = MagicMock()
        mock_secrets_client.create_secret.return_value = {"ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:test"}
        key_storage_manager.aws_client.get_client.return_value = mock_secrets_client

        await key_storage_manager._store_in_secrets_manager("test-key", sample_private_key)

        call_args = mock_secrets_client.create_secret.call_args[1]
        secret_value = json.loads(call_args["SecretString"])
        
        assert secret_value["private_key"] == sample_private_key
        assert secret_value["key_name"] == "test-key"
        assert secret_value["created_by"] == "ec2-mcp-server"

    def test_region_from_config(self, mock_aws_client):
        """Test that region is properly extracted from config."""
        config = {"aws_region": "eu-west-1"}
        manager = KeyStorageManager(mock_aws_client, config)
        assert manager.region == "eu-west-1"

    def test_different_salt_different_keys(self, mock_aws_client):
        """Test that different salts produce different encryption keys."""
        config1 = {"encryption_salt": "salt1", "aws_region": "us-east-1"}
        config2 = {"encryption_salt": "salt2", "aws_region": "us-east-1"}
        
        manager1 = KeyStorageManager(mock_aws_client, config1)
        manager2 = KeyStorageManager(mock_aws_client, config2)
        
        key1 = manager1._generate_encryption_key("test")
        key2 = manager2._generate_encryption_key("test")
        
        assert key1 != key2

    def test_different_region_different_keys(self, mock_aws_client):
        """Test that different regions produce different encryption keys."""
        config1 = {"encryption_salt": "same-salt", "aws_region": "us-east-1"}
        config2 = {"encryption_salt": "same-salt", "aws_region": "us-west-2"}
        
        manager1 = KeyStorageManager(mock_aws_client, config1)
        manager2 = KeyStorageManager(mock_aws_client, config2)
        
        key1 = manager1._generate_encryption_key("test")
        key2 = manager2._generate_encryption_key("test")
        
        assert key1 != key2