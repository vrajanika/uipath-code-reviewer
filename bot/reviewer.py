"""
Main code reviewer orchestrator.
"""

from typing import Optional, List, Dict
from .azure_openai_client import AzureOpenAIClient
from .github_client import GitHubClient
from .diff_parser import build_position_map

SEVERITY_EMOJI = {
    'issue': '\u26a0\ufe0f',
    'suggestion': '\U0001f4a1',
    'nitpick': '\U0001f50d',
    'praise': '\U0001f44d',
}


class CodeReviewer:
    """Orchestrates code review process using Azure OpenAI and GitHub."""

    def __init__(
        self,
        github_client: Optional[GitHubClient] = None,
        azure_client: Optional[AzureOpenAIClient] = None,
    ):
        """
        Initialize the code reviewer.

        Args:
            github_client: GitHub client instance
            azure_client: Azure OpenAI client instance
        """
        self.github_client = github_client or GitHubClient()
        self.azure_client = azure_client or AzureOpenAIClient()

    def review_pull_request(
        self,
        repo_full_name: str,
        pr_number: int,
        post_comments: bool = True,
        focus_on_uipath: bool = True,
        inline_comments: bool = True,
    ) -> Dict:
        """
        Review a pull request.

        Args:
            repo_full_name: Full repository name (e.g., "owner/repo")
            pr_number: Pull request number
            post_comments: Whether to post comments to GitHub
            focus_on_uipath: Focus review on UiPath-specific files
            inline_comments: Use inline line-level comments (True) or
                legacy single-comment mode (False)

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

        # Use inline comments path or legacy path
        if inline_comments:
            return self._review_inline(files, repo_full_name, pr_number, post_comments)
        else:
            return self._review_legacy(files, repo_full_name, pr_number, post_comments)

    def _review_inline(
        self,
        files: List[Dict],
        repo_full_name: str,
        pr_number: int,
        post_comments: bool,
    ) -> Dict:
        """Review files using structured AI output and inline comments."""
        reviews = []
        all_inline_comments = []
        file_summaries = []

        for file in files:
            if not file['patch']:
                continue

            review = self._review_file_structured(file)
            reviews.append(review)

            # Build position map for this file's patch
            position_map = build_position_map(file['patch'])

            # Convert AI line references to diff positions
            for comment in review.get('inline_comments', []):
                line_num = comment['line']
                if line_num in position_map:
                    severity = comment.get('severity', 'suggestion')
                    emoji = SEVERITY_EMOJI.get(severity, '')
                    prefix = f"{emoji} **{severity.upper()}**: " if emoji else ""

                    body = f"{prefix}{comment['body']}"

                    # Append GitHub suggestion block if the AI provided a fix
                    suggested_fix = comment.get('suggested_fix')
                    if suggested_fix:
                        body += f"\n\n```suggestion\n{suggested_fix}\n```"

                    all_inline_comments.append({
                        'path': file['filename'],
                        'position': position_map[line_num],
                        'body': body,
                    })

            if review.get('summary'):
                file_summaries.append({
                    'filename': file['filename'],
                    'summary': review['summary'],
                    'additions': file['additions'],
                    'deletions': file['deletions'],
                })

        # Build overall summary
        overall_summary = self._compile_inline_review_summary(file_summaries)

        # Post if requested
        if post_comments and (all_inline_comments or file_summaries):
            try:
                self.github_client.post_inline_review(
                    repo_full_name=repo_full_name,
                    pr_number=pr_number,
                    comments=all_inline_comments,
                    summary=overall_summary,
                )
                return {
                    'status': 'success',
                    'message': 'Review completed and posted with inline comments',
                    'reviews': reviews,
                    'overall_review': overall_summary,
                    'inline_comments': all_inline_comments,
                }
            except Exception as e:
                return {
                    'status': 'partial_success',
                    'message': f'Review completed but failed to post: {str(e)}',
                    'reviews': reviews,
                    'overall_review': overall_summary,
                    'inline_comments': all_inline_comments,
                }

        return {
            'status': 'success',
            'message': 'Review completed',
            'reviews': reviews,
            'overall_review': overall_summary,
            'inline_comments': all_inline_comments,
        }

    def _review_legacy(
        self,
        files: List[Dict],
        repo_full_name: str,
        pr_number: int,
        post_comments: bool,
    ) -> Dict:
        """Review files using the original single-comment approach."""
        reviews = []
        for file in files:
            if file['patch']:
                review = self._review_file(file)
                reviews.append(review)

        overall_review = self._compile_overall_review(reviews)

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
        """Review a single file (legacy free-form text mode)."""
        filename = file['filename']
        patch = file['patch']

        try:
            review_comment = self.azure_client.review_code(
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

    def _review_file_structured(self, file: Dict) -> Dict:
        """Review a single file using structured AI output."""
        filename = file['filename']
        patch = file['patch']

        try:
            structured = self.azure_client.review_code_structured(
                diff=patch,
                file_path=filename,
                context=None,
            )

            return {
                'filename': filename,
                'status': 'reviewed',
                'summary': structured.get('summary', ''),
                'inline_comments': structured.get('comments', []),
                'additions': file['additions'],
                'deletions': file['deletions'],
            }
        except Exception as e:
            return {
                'filename': filename,
                'status': 'error',
                'summary': f'Failed to review: {str(e)}',
                'inline_comments': [],
                'additions': file['additions'],
                'deletions': file['deletions'],
            }

    def _compile_overall_review(self, reviews: List[Dict]) -> str:
        """Compile individual file reviews into an overall review (legacy mode)."""
        if not reviews:
            return "No files were reviewed."

        review_parts = [
            "## \U0001f916 UiPath Code Review",
            "",
            f"Reviewed {len(reviews)} file(s) in this pull request.",
            "",
        ]

        for review in reviews:
            if review['status'] == 'reviewed':
                review_parts.append(f"### \U0001f4c4 `{review['filename']}`")
                review_parts.append(f"*Changes: +{review['additions']} -{review['deletions']}*")
                review_parts.append("")
                review_parts.append(review['comment'])
                review_parts.append("")
                review_parts.append("---")
                review_parts.append("")

        review_parts.append("*Review powered by Azure OpenAI*")

        return "\n".join(review_parts)

    def _compile_inline_review_summary(self, file_summaries: List[Dict]) -> str:
        """
        Compile file summaries into the body of a GitHub review.

        This is the text that appears at the top of the review, above the
        inline comments. It is concise since the detailed feedback is in
        the inline comments themselves.
        """
        if not file_summaries:
            return "No files were reviewed."

        parts = [
            "## Code Review",
            "",
            f"Reviewed {len(file_summaries)} file(s). See inline comments for details.",
            "",
        ]

        for fs in file_summaries:
            parts.append(f"**`{fs['filename']}`** (+{fs['additions']} -{fs['deletions']})")
            parts.append(f"> {fs['summary']}")
            parts.append("")

        parts.append("*Review powered by Azure OpenAI*")
        return "\n".join(parts)
