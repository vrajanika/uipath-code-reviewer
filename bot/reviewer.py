"""
Main code reviewer orchestrator.
"""

from typing import Optional, List, Dict
from .bedrock_client import BedrockClient
from .github_client import GitHubClient


class CodeReviewer:
    """Orchestrates code review process using AWS Bedrock Claude and GitHub."""

    def __init__(
        self,
        github_client: Optional[GitHubClient] = None,
        bedrock_client: Optional[BedrockClient] = None,
    ):
        """
        Initialize the code reviewer.

        Args:
            github_client: GitHub client instance
            bedrock_client: AWS Bedrock client instance
        """
        self.github_client = github_client or GitHubClient()
        self.bedrock_client = bedrock_client or BedrockClient()
    
    def review_pull_request(
        self,
        repo_full_name: str,
        pr_number: int,
        post_comments: bool = True,
        focus_on_uipath: bool = True,
    ) -> Dict:
        """
        Review a pull request.
        
        Args:
            repo_full_name: Full repository name (e.g., "owner/repo")
            pr_number: Pull request number
            post_comments: Whether to post comments to GitHub
            focus_on_uipath: Focus review on UiPath-specific files
        
        Returns:
            Dictionary containing review results
        """
        # Get PR files
        files = self.github_client.get_pr_files(repo_full_name, pr_number)
        
        if not files:
            return {
                'status': 'no_changes',
                'message': 'No files to review',
                'reviews': []
            }
        
        # Filter files if focusing on UiPath
        if focus_on_uipath:
            files = self._filter_uipath_files(files)
        
        if not files:
            return {
                'status': 'no_uipath_files',
                'message': 'No UiPath files found to review',
                'reviews': []
            }
        
        # Review each file
        reviews = []
        for file in files:
            if file['patch']:  # Only review files with actual changes
                review = self._review_file(file)
                reviews.append(review)
        
        # Compile overall review
        overall_review = self._compile_overall_review(reviews)
        
        # Post comments if requested
        if post_comments and reviews:
            try:
                self.github_client.post_review_comment(
                    repo_full_name=repo_full_name,
                    pr_number=pr_number,
                    body=overall_review,
                    event="COMMENT"
                )
                
                return {
                    'status': 'success',
                    'message': 'Review completed and posted',
                    'reviews': reviews,
                    'overall_review': overall_review
                }
            except Exception as e:
                return {
                    'status': 'partial_success',
                    'message': f'Review completed but failed to post: {str(e)}',
                    'reviews': reviews,
                    'overall_review': overall_review
                }
        
        return {
            'status': 'success',
            'message': 'Review completed',
            'reviews': reviews,
            'overall_review': overall_review
        }
    
    def _filter_uipath_files(self, files: List[Dict]) -> List[Dict]:
        """Filter to only UiPath-related files."""
        uipath_extensions = ['.xaml', '.json', '.config']
        uipath_patterns = ['project.json', 'package.json', 'workflow']
        
        filtered = []
        for file in files:
            filename = file['filename'].lower()
            
            # Check extensions
            if any(filename.endswith(ext) for ext in uipath_extensions):
                filtered.append(file)
                continue
            
            # Check patterns
            if any(pattern in filename for pattern in uipath_patterns):
                filtered.append(file)
        
        return filtered
    
    def _review_file(self, file: Dict) -> Dict:
        """Review a single file."""
        filename = file['filename']
        patch = file['patch']
        
        try:
            review_comment = self.bedrock_client.review_code(
                diff=patch,
                file_path=filename,
                context=None
            )
            
            return {
                'filename': filename,
                'status': 'reviewed',
                'comment': review_comment,
                'additions': file['additions'],
                'deletions': file['deletions'],
            }
        except Exception as e:
            return {
                'filename': filename,
                'status': 'error',
                'comment': f'Failed to review: {str(e)}',
                'additions': file['additions'],
                'deletions': file['deletions'],
            }
    
    def _compile_overall_review(self, reviews: List[Dict]) -> str:
        """Compile individual file reviews into an overall review."""
        if not reviews:
            return "No files were reviewed."
        
        review_parts = [
            "## 🤖 UiPath Code Review",
            "",
            f"Reviewed {len(reviews)} file(s) in this pull request.",
            "",
        ]
        
        for review in reviews:
            if review['status'] == 'reviewed':
                review_parts.append(f"### 📄 `{review['filename']}`")
                review_parts.append(f"*Changes: +{review['additions']} -{review['deletions']}*")
                review_parts.append("")
                review_parts.append(review['comment'])
                review_parts.append("")
                review_parts.append("---")
                review_parts.append("")
        
        review_parts.append("*Review powered by Claude on AWS Bedrock*")
        
        return "\n".join(review_parts)
