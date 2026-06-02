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

    @patch('bot.azure_openai_client.AzureOpenAI')
    def test_review_code_structured_success(self, mock_azure_openai):
        """Test structured review returns parsed JSON."""
        mock_client = MagicMock()
        json_response = '{"summary": "Looks good", "comments": [{"line": 5, "body": "Fix this", "severity": "issue"}]}'
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=json_response))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client

        client = AzureOpenAIClient(
            azure_endpoint='https://test.openai.azure.com/',
            api_key='test-key',
            deployment_name='test-deployment',
        )

        result = client.review_code_structured(diff="+ new line", file_path="test.py")
        assert result['summary'] == 'Looks good'
        assert len(result['comments']) == 1
        assert result['comments'][0]['line'] == 5
        assert result['comments'][0]['body'] == 'Fix this'
        assert result['comments'][0]['severity'] == 'issue'

    @patch('bot.azure_openai_client.AzureOpenAI')
    def test_review_code_structured_invalid_json_fallback(self, mock_azure_openai):
        """Test fallback when AI returns non-JSON."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="This is just plain text"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client

        client = AzureOpenAIClient(
            azure_endpoint='https://test.openai.azure.com/',
            api_key='test-key',
            deployment_name='test-deployment',
        )

        result = client.review_code_structured(diff="+ line", file_path="test.py")
        assert result['summary'] == "This is just plain text"
        assert result['comments'] == []

    def test_parse_ai_response_with_code_fences(self):
        """Test parsing JSON wrapped in markdown code fences."""
        client = AzureOpenAIClient(
            azure_endpoint='https://test.openai.azure.com/',
            api_key='test-key',
            deployment_name='test-deployment',
        )
        raw = '```json\n{"summary": "ok", "comments": []}\n```'
        result = client._parse_ai_response(raw)
        assert result['summary'] == 'ok'
        assert result['comments'] == []

    def test_parse_ai_response_missing_summary(self):
        """Test parsing JSON with missing summary field."""
        client = AzureOpenAIClient(
            azure_endpoint='https://test.openai.azure.com/',
            api_key='test-key',
            deployment_name='test-deployment',
        )
        raw = '{"comments": [{"line": 1, "body": "test"}]}'
        result = client._parse_ai_response(raw)
        assert result['summary'] == 'Review completed.'
        assert len(result['comments']) == 1
        assert result['comments'][0]['severity'] == 'suggestion'

    def test_parse_ai_response_invalid_comments_skipped(self):
        """Test that comments without required fields are skipped."""
        client = AzureOpenAIClient(
            azure_endpoint='https://test.openai.azure.com/',
            api_key='test-key',
            deployment_name='test-deployment',
        )
        raw = '{"summary": "ok", "comments": [{"line": 1, "body": "valid"}, {"bad": "entry"}, "not a dict"]}'
        result = client._parse_ai_response(raw)
        assert len(result['comments']) == 1
        assert result['comments'][0]['body'] == 'valid'

    def test_parse_ai_response_with_suggested_fix(self):
        """Test that suggested_fix is preserved when present."""
        client = AzureOpenAIClient(
            azure_endpoint='https://test.openai.azure.com/',
            api_key='test-key',
            deployment_name='test-deployment',
        )
        raw = '{"summary": "ok", "comments": [{"line": 5, "body": "Use descriptive name", "severity": "suggestion", "suggested_fix": "    better_name = compute()"}]}'
        result = client._parse_ai_response(raw)
        assert len(result['comments']) == 1
        assert result['comments'][0]['suggested_fix'] == '    better_name = compute()'

    def test_parse_ai_response_without_suggested_fix(self):
        """Test that absent suggested_fix does not cause errors."""
        client = AzureOpenAIClient(
            azure_endpoint='https://test.openai.azure.com/',
            api_key='test-key',
            deployment_name='test-deployment',
        )
        raw = '{"summary": "ok", "comments": [{"line": 3, "body": "Looks fine", "severity": "praise"}]}'
        result = client._parse_ai_response(raw)
        assert len(result['comments']) == 1
        assert 'suggested_fix' not in result['comments'][0]

    def test_parse_ai_response_empty_suggested_fix_excluded(self):
        """Test that empty, null, and whitespace-only suggested_fix values are excluded."""
        client = AzureOpenAIClient(
            azure_endpoint='https://test.openai.azure.com/',
            api_key='test-key',
            deployment_name='test-deployment',
        )
        # Empty string
        raw = '{"summary": "ok", "comments": [{"line": 1, "body": "test", "suggested_fix": ""}]}'
        result = client._parse_ai_response(raw)
        assert 'suggested_fix' not in result['comments'][0]

        # Whitespace only
        raw = '{"summary": "ok", "comments": [{"line": 1, "body": "test", "suggested_fix": "   "}]}'
        result = client._parse_ai_response(raw)
        assert 'suggested_fix' not in result['comments'][0]

        # Null
        raw = '{"summary": "ok", "comments": [{"line": 1, "body": "test", "suggested_fix": null}]}'
        result = client._parse_ai_response(raw)
        assert 'suggested_fix' not in result['comments'][0]

    def test_parse_ai_response_multiline_suggested_fix_rejected(self):
        """Test that multi-line suggested_fix is rejected."""
        client = AzureOpenAIClient(
            azure_endpoint='https://test.openai.azure.com/',
            api_key='test-key',
            deployment_name='test-deployment',
        )
        raw = '{"summary": "ok", "comments": [{"line": 1, "body": "test", "suggested_fix": "line1\\nline2"}]}'
        result = client._parse_ai_response(raw)
        assert 'suggested_fix' not in result['comments'][0]

    @patch('bot.azure_openai_client.AzureOpenAI')
    def test_review_code_structured_with_suggested_fix(self, mock_azure_openai):
        """Test full structured review flow preserves suggested_fix."""
        mock_client = MagicMock()
        json_response = '{"summary": "Needs fixes", "comments": [{"line": 10, "body": "Rename var", "severity": "issue", "suggested_fix": "    count = 0"}]}'
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=json_response))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client

        client = AzureOpenAIClient(
            azure_endpoint='https://test.openai.azure.com/',
            api_key='test-key',
            deployment_name='test-deployment',
        )

        result = client.review_code_structured(diff="+ new line", file_path="test.py")
        assert result['summary'] == 'Needs fixes'
        assert len(result['comments']) == 1
        assert result['comments'][0]['suggested_fix'] == '    count = 0'
