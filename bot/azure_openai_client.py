"""
Azure OpenAI client for code review.
"""

import os
import json
import re
from typing import Optional, Dict, List
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
                max_completion_tokens=3000,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error during code review: {str(e)}"
    
    def review_code_structured(self, diff: str, file_path: str, context: Optional[str] = None) -> Dict:
        """
        Review code changes and return structured inline comments.

        Args:
            diff: Git diff of the changes
            file_path: Path to the file being reviewed
            context: Additional context about the changes

        Returns:
            Dict with keys:
                - "comments": list of inline comment dicts (line, body, severity)
                - "summary": str, overall summary for the file

            Falls back to {"comments": [], "summary": <raw text>} on parse failure.
        """
        file_type = self._get_file_type(file_path)

        system_prompt = self._build_structured_system_prompt(file_type)
        user_prompt = self._build_structured_user_prompt(diff, file_path, context)

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_completion_tokens=3000,
            )

            raw_text = response.choices[0].message.content
            return self._parse_ai_response(raw_text)
        except Exception as e:
            return {
                "summary": f"Error during code review: {str(e)}",
                "comments": [],
            }

    def _parse_ai_response(self, response_text: str) -> Dict:
        """
        Parse the AI's response text into structured format.

        Strips markdown code fences if present, then attempts JSON parsing.
        Falls back to treating the raw text as a summary if parsing fails.
        """
        text = response_text.strip()

        # Strip markdown code fences (```json ... ``` or ``` ... ```)
        fence_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', text, re.DOTALL)
        if fence_match:
            text = fence_match.group(1).strip()

        try:
            parsed = json.loads(text)

            if not isinstance(parsed, dict):
                raise ValueError("Response is not a JSON object")

            if "summary" not in parsed:
                parsed["summary"] = "Review completed."

            if "comments" not in parsed or not isinstance(parsed["comments"], list):
                parsed["comments"] = []

            # Validate each comment
            valid_comments = []
            for c in parsed["comments"]:
                if isinstance(c, dict) and "line" in c and "body" in c:
                    comment_data = {
                        "line": int(c["line"]),
                        "body": str(c["body"]),
                        "severity": c.get("severity", "suggestion"),
                    }
                    if c.get("suggested_fix") and isinstance(c["suggested_fix"], str) and c["suggested_fix"].strip():
                        fix_text = c["suggested_fix"]
                        if "\n" not in fix_text:  # single-line only
                            comment_data["suggested_fix"] = fix_text
                    valid_comments.append(comment_data)
            parsed["comments"] = valid_comments

            return parsed
        except (json.JSONDecodeError, ValueError, TypeError):
            return {
                "summary": response_text,
                "comments": [],
            }

    def _build_structured_system_prompt(self, file_type: str) -> str:
        """Build system prompt that instructs AI to return structured JSON."""
        base_prompt = """You are an expert code reviewer. Review code changes and provide feedback as structured JSON.

You MUST respond with valid JSON only. No markdown, no extra text outside the JSON.

Use this exact schema:
{
  "summary": "Brief overall assessment of changes in this file (1-3 sentences).",
  "comments": [
    {
      "line": <new-file line number from the diff>,
      "body": "Your feedback for this specific line.",
      "severity": "issue|suggestion|nitpick|praise",
      "suggested_fix": "replacement code for the entire line (optional)"
    }
  ]
}

Rules for the "line" field:
- Use the NEW file line number (the number after + in @@ -old +new @@)
- Only reference lines that appear in the diff (added or context lines)
- Do NOT reference deleted lines (lines starting with -)
- If you have general feedback not tied to a specific line, put it in "summary"

Severity meanings:
- "issue": Bug, potential error, or correctness problem
- "suggestion": Improvement that would make the code better
- "nitpick": Minor style or convention preference
- "praise": Something done well worth calling out

Rules for "suggested_fix":
- OPTIONAL — only include when you have a concrete code replacement for the line
- Must contain the full replacement for the ENTIRE line, with proper indentation preserved
- Single line only — do NOT include newlines
- Do NOT include for "praise" or "nitpick" severity
- Do NOT wrap in backticks — provide the raw code string

Keep comments concise and actionable. Aim for 1-5 inline comments per file.
If the changes look good with no issues, return an empty comments array and a positive summary."""

        if file_type == 'uipath_workflow':
            base_prompt += """

Focus areas for UiPath XAML workflow files:
- Error handling and retry logic
- Selector usage and reliability
- Variable scope and naming conventions
- Workflow structure and modularity
- Try-Catch blocks, delays, and timeouts"""

        elif file_type == 'uipath_config':
            base_prompt += """

Focus areas for UiPath configuration files:
- Configuration structure
- Secure handling of credentials and sensitive data
- Environment-specific settings
- Validation of configuration values"""

        return base_prompt

    def _build_structured_user_prompt(self, diff: str, file_path: str, context: Optional[str] = None) -> str:
        """Build user prompt for structured JSON review."""
        prompt = f"""Review the following code changes for: {file_path}

Diff (unified format):
```
{diff}
```"""

        if context:
            prompt += f"\n\nAdditional context: {context}"

        prompt += "\n\nRespond with JSON only. Follow the schema in your instructions."

        return prompt

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
