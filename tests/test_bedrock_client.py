"""
Tests for AWS Bedrock client.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from bot.bedrock_client import BedrockClient


class TestBedrockClient:
    """Test cases for BedrockClient."""

    @patch('bot.bedrock_client.boto3')
    @patch.dict('os.environ', {
        'AWS_REGION': 'us-east-1',
        'BEDROCK_MODEL_ID': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
    })
    def test_init_with_env_vars(self, mock_boto3):
        """Test initialization with environment variables."""
        client = BedrockClient()
        assert client.aws_region == 'us-east-1'
        assert client.model_id == 'anthropic.claude-3-5-sonnet-20241022-v2:0'

    @patch('bot.bedrock_client.boto3')
    def test_init_with_params(self, mock_boto3):
        """Test initialization with explicit parameters."""
        client = BedrockClient(
            model_id='anthropic.claude-3-haiku-20240307-v1:0',
            aws_region='eu-west-1',
            aws_access_key_id='AKIAIOSFODNN7EXAMPLE',
            aws_secret_access_key='secret',
        )
        assert client.model_id == 'anthropic.claude-3-haiku-20240307-v1:0'
        assert client.aws_region == 'eu-west-1'

    @patch('bot.bedrock_client.boto3')
    def test_init_default_model_and_region(self, mock_boto3):
        """Test that sensible defaults are applied when env vars are absent."""
        with patch.dict('os.environ', {}, clear=True):
            client = BedrockClient()
        assert client.model_id == 'anthropic.claude-3-5-sonnet-20241022-v2:0'
        assert client.aws_region == 'us-east-1'

    @patch('bot.bedrock_client.boto3')
    def test_get_file_type_xaml(self, mock_boto3):
        """Test file type detection for XAML files."""
        client = BedrockClient()
        assert client._get_file_type('workflow.xaml') == 'uipath_workflow'

    @patch('bot.bedrock_client.boto3')
    def test_get_file_type_json(self, mock_boto3):
        """Test file type detection for JSON files."""
        client = BedrockClient()
        assert client._get_file_type('project.json') == 'uipath_config'

    @patch('bot.bedrock_client.boto3')
    def test_get_file_type_python(self, mock_boto3):
        """Test file type detection for Python files."""
        client = BedrockClient()
        assert client._get_file_type('script.py') == 'python'

    @patch('bot.bedrock_client.boto3')
    def test_get_file_type_other(self, mock_boto3):
        """Test file type detection for unrecognised extensions."""
        client = BedrockClient()
        assert client._get_file_type('notes.txt') == 'other'

    @patch('bot.bedrock_client.boto3')
    def test_build_system_prompt_uipath(self, mock_boto3):
        """Test system prompt building for UiPath workflows."""
        client = BedrockClient()
        prompt = client._build_system_prompt('uipath_workflow')
        assert 'UiPath' in prompt
        assert 'XAML' in prompt
        assert 'error handling' in prompt.lower()

    @patch('bot.bedrock_client.boto3')
    def test_build_system_prompt_config(self, mock_boto3):
        """Test system prompt building for config files."""
        client = BedrockClient()
        prompt = client._build_system_prompt('uipath_config')
        assert 'configuration' in prompt.lower()
        assert 'credentials' in prompt.lower()

    @patch('bot.bedrock_client.boto3')
    def test_review_code_success(self, mock_boto3):
        """Test successful code review via Bedrock Converse API."""
        mock_bedrock = MagicMock()
        mock_boto3.client.return_value = mock_bedrock

        mock_bedrock.converse.return_value = {
            "output": {
                "message": {
                    "content": [{"text": "Great code!"}]
                }
            }
        }

        client = BedrockClient(
            model_id='anthropic.claude-3-5-sonnet-20241022-v2:0',
            aws_region='us-east-1',
        )

        result = client.review_code(diff="+ added line", file_path="test.xaml")

        assert result == "Great code!"
        mock_bedrock.converse.assert_called_once()

    @patch('bot.bedrock_client.boto3')
    def test_review_code_passes_system_and_user_message(self, mock_boto3):
        """Test that converse is called with a system prompt and a user message."""
        mock_bedrock = MagicMock()
        mock_boto3.client.return_value = mock_bedrock

        mock_bedrock.converse.return_value = {
            "output": {"message": {"content": [{"text": "ok"}]}}
        }

        client = BedrockClient(model_id='anthropic.claude-3-5-sonnet-20241022-v2:0')
        client.review_code(diff="- removed line", file_path="workflow.xaml")

        call_kwargs = mock_bedrock.converse.call_args.kwargs
        assert "system" in call_kwargs
        assert call_kwargs["system"][0]["text"]  # non-empty system prompt
        assert call_kwargs["messages"][0]["role"] == "user"

    @patch('bot.bedrock_client.boto3')
    def test_review_code_error_handling(self, mock_boto3):
        """Test that errors are caught and returned as strings."""
        mock_bedrock = MagicMock()
        mock_boto3.client.return_value = mock_bedrock
        mock_bedrock.converse.side_effect = Exception("throttling error")

        client = BedrockClient(model_id='anthropic.claude-3-5-sonnet-20241022-v2:0')
        result = client.review_code(diff="+ line", file_path="test.py")

        assert "Error during code review" in result
        assert "throttling error" in result
