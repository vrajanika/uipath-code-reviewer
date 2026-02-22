"""
Azure OpenAI client for code review.
"""

import os
from typing import Optional
from openai import AzureOpenAI


class AzureOpenAIClient:
    """Client for interacting with Azure OpenAI service."""
    
    def __init__(
        self,
        azure_endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: Optional[str] = None,
        deployment_name: Optional[str] = None,
    ):
        """
        Initialize the Azure OpenAI client.
        
        Args:
            azure_endpoint: Azure OpenAI endpoint URL
            api_key: Azure OpenAI API key
            api_version: API version (default: "2024-02-15-preview")
            deployment_name: Deployment/model name to use
        """
        self.azure_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.deployment_name = deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        if not self.azure_endpoint or not self.api_key:
            raise ValueError("Azure OpenAI endpoint and API key are required")
        
        if not self.deployment_name:
            raise ValueError("Azure OpenAI deployment name is required")
        
        self.client = AzureOpenAI(
            azure_endpoint=self.azure_endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
        )
    
    def review_code(self, diff: str, file_path: str, context: Optional[str] = None) -> str:
        """
        Review code changes using Azure OpenAI.
        
        Args:
            diff: Git diff of the changes
            file_path: Path to the file being reviewed
            context: Additional context about the changes
        
        Returns:
            Review comments from the AI
        """
        # Determine file type
        file_type = self._get_file_type(file_path)
        
        # Build the review prompt
        system_prompt = self._build_system_prompt(file_type)
        user_prompt = self._build_user_prompt(diff, file_path, context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_completion_tokens=2000,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error during code review: {str(e)}"
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine the type of file based on extension."""
        if file_path.endswith('.xaml'):
            return 'uipath_workflow'
        elif file_path.endswith('.json'):
            return 'uipath_config'
        elif file_path.endswith('.py'):
            return 'python'
        elif file_path.endswith(('.cs', '.vb')):
            return 'dotnet'
        else:
            return 'other'
    
    def _build_system_prompt(self, file_type: str) -> str:
        """Build the system prompt based on file type."""
        base_prompt = """You are an expert code reviewer specializing in UiPath automation projects. 
Your role is to review code changes and provide constructive feedback focusing on:
1. Code quality and best practices
2. Potential bugs or issues
3. Performance improvements
4. Security concerns
5. Maintainability and readability"""
        
        if file_type == 'uipath_workflow':
            return base_prompt + """

For UiPath XAML workflow files, pay special attention to:
- Proper error handling and retry logic
- Efficient selector usage and reliability
- Variable scope and naming conventions
- Workflow structure and modularity
- Use of best practices for UI automation
- Proper use of Try-Catch blocks
- Appropriate use of delays and timeouts
- Data type handling and conversions"""
        
        elif file_type == 'uipath_config':
            return base_prompt + """

For UiPath configuration files (JSON), pay special attention to:
- Proper configuration structure
- Secure handling of credentials and sensitive data
- Environment-specific settings
- Validation of configuration values"""
        
        return base_prompt
    
    def _build_user_prompt(self, diff: str, file_path: str, context: Optional[str] = None) -> str:
        """Build the user prompt with code changes."""
        prompt = f"""Please review the following code changes for the file: {file_path}

Code changes (diff):
```
{diff}
```
"""
        
        if context:
            prompt += f"\nAdditional context: {context}\n"
        
        prompt += """
Please provide a detailed code review focusing on:
1. Any issues or bugs you identify
2. Suggestions for improvement
3. Best practices that should be followed
4. Security concerns (if any)

Format your response as clear, actionable feedback that can be posted as a PR comment."""
        
        return prompt
