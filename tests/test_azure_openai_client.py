"""
Tests for Azure OpenAI client.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from bot.azure_openai_client import AzureOpenAIClient


class TestAzureOpenAIClient:
    """Test cases for AzureOpenAIClient."""
    
    @patch.dict('os.environ', {
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_KEY': 'test-key',
        'AZURE_OPENAI_DEPLOYMENT_NAME': 'test-deployment',
    })
    def test_init_with_env_vars(self):
        """Test initialization with environment variables."""
        client = AzureOpenAIClient()
        assert client.azure_endpoint == 'https://test.openai.azure.com/'
        assert client.api_key == 'test-key'
        assert client.deployment_name == 'test-deployment'
    
    def test_init_with_params(self):
        """Test initialization with parameters."""
        client = AzureOpenAIClient(
            azure_endpoint='https://test.openai.azure.com/',
            api_key='test-key',
            deployment_name='test-deployment',
        )
        assert client.azure_endpoint == 'https://test.openai.azure.com/'
        assert client.api_key == 'test-key'
        assert client.deployment_name == 'test-deployment'
    
    def test_init_missing_endpoint(self):
        """Test initialization fails without endpoint."""
        with pytest.raises(ValueError, match="Azure OpenAI endpoint and API key are required"):
            AzureOpenAIClient(api_key='test-key', deployment_name='test-deployment')
    
    def test_init_missing_deployment(self):
        """Test initialization fails without deployment name."""
        with pytest.raises(ValueError, match="Azure OpenAI deployment name is required"):
            AzureOpenAIClient(
                azure_endpoint='https://test.openai.azure.com/',
                api_key='test-key'
            )
    
    def test_get_file_type_xaml(self):
        """Test file type detection for XAML files."""
        client = AzureOpenAIClient(
            azure_endpoint='https://test.openai.azure.com/',
            api_key='test-key',
            deployment_name='test-deployment',
        )
        assert client._get_file_type('workflow.xaml') == 'uipath_workflow'
    
    def test_get_file_type_json(self):
        """Test file type detection for JSON files."""
        client = AzureOpenAIClient(
            azure_endpoint='https://test.openai.azure.com/',
            api_key='test-key',
            deployment_name='test-deployment',
        )
        assert client._get_file_type('project.json') == 'uipath_config'
    
    def test_get_file_type_python(self):
        """Test file type detection for Python files."""
        client = AzureOpenAIClient(
            azure_endpoint='https://test.openai.azure.com/',
            api_key='test-key',
            deployment_name='test-deployment',
        )
        assert client._get_file_type('script.py') == 'python'
    
    def test_build_system_prompt_uipath(self):
        """Test system prompt building for UiPath workflows."""
        client = AzureOpenAIClient(
            azure_endpoint='https://test.openai.azure.com/',
            api_key='test-key',
            deployment_name='test-deployment',
        )
        prompt = client._build_system_prompt('uipath_workflow')
        assert 'UiPath' in prompt
        assert 'XAML' in prompt
        assert 'error handling' in prompt.lower()
    
    @patch('bot.azure_openai_client.AzureOpenAI')
    def test_review_code_success(self, mock_azure_openai):
        """Test successful code review."""
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Great code!"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        # Create client
        client = AzureOpenAIClient(
            azure_endpoint='https://test.openai.azure.com/',
            api_key='test-key',
            deployment_name='test-deployment',
        )
        
        # Test review
        result = client.review_code(
            diff="+ added line",
            file_path="test.xaml"
        )
        
        assert result == "Great code!"
        mock_client.chat.completions.create.assert_called_once()
