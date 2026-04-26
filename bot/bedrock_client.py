"""
AWS Bedrock client for code review using Claude models.
"""

import os
from typing import Optional
import boto3


class BedrockClient:
    """Client for interacting with Claude models via AWS Bedrock."""

    def __init__(
        self,
        model_id: Optional[str] = None,
        aws_region: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
    ):
        """
        Initialize the AWS Bedrock client.

        Args:
            model_id: Bedrock model ID (e.g. "anthropic.claude-3-5-sonnet-20241022-v2:0")
            aws_region: AWS region where Bedrock is enabled (e.g. "us-east-1")
            aws_access_key_id: AWS access key ID (optional if using IAM roles)
            aws_secret_access_key: AWS secret access key (optional if using IAM roles)
            aws_session_token: AWS session token for temporary credentials (optional)
        """
        self.model_id = model_id or os.getenv(
            "BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        self.aws_region = aws_region or os.getenv("AWS_REGION", "us-east-1")

        resolved_key = aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        resolved_secret = aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        resolved_token = aws_session_token or os.getenv("AWS_SESSION_TOKEN")

        session_kwargs = {"region_name": self.aws_region}
        if resolved_key and resolved_secret:
            session_kwargs["aws_access_key_id"] = resolved_key
            session_kwargs["aws_secret_access_key"] = resolved_secret
            if resolved_token:
                session_kwargs["aws_session_token"] = resolved_token

        self.client = boto3.client("bedrock-runtime", **session_kwargs)

    def review_code(self, diff: str, file_path: str, context: Optional[str] = None) -> str:
        """
        Review code changes using a Claude model on AWS Bedrock.

        Args:
            diff: Git diff of the changes
            file_path: Path to the file being reviewed
            context: Additional context about the changes

        Returns:
            Review comments from the AI
        """
        file_type = self._get_file_type(file_path)

        system_prompt = self._build_system_prompt(file_type)
        user_prompt = self._build_user_prompt(diff, file_path, context)

        try:
            response = self.client.converse(
                modelId=self.model_id,
                system=[{"text": system_prompt}],
                messages=[
                    {"role": "user", "content": [{"text": user_prompt}]},
                ],
                inferenceConfig={
                    "temperature": 0.3,
                    "maxTokens": 2000,
                },
            )
            return response["output"]["message"]["content"][0]["text"]
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
        base_prompt = """You are an expert code reviewer specializing in UiPath automation projects. \
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
