"""
GitHub integration for code review bot.
"""

import os
from typing import Optional, List, Dict
from github import Github, GithubException
from github.PullRequest import PullRequest
from github.Repository import Repository


class GitHubClient:
    """Client for interacting with GitHub API."""
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the GitHub client.
        
        Args:
            access_token: GitHub personal access token or app token
        """
        self.access_token = access_token or os.getenv("GITHUB_TOKEN")
        
        if not self.access_token:
            raise ValueError("GitHub access token is required")
        
        self.client = Github(self.access_token)
    
    def get_repository(self, repo_full_name: str) -> Repository:
        """
        Get a repository by full name.
        
        Args:
            repo_full_name: Full repository name (e.g., "owner/repo")
        
        Returns:
            GitHub Repository object
        """
        return self.client.get_repo(repo_full_name)
    
    def get_pull_request(self, repo_full_name: str, pr_number: int) -> PullRequest:
        """
        Get a pull request.
        
        Args:
            repo_full_name: Full repository name
            pr_number: Pull request number
        
        Returns:
            GitHub PullRequest object
        """
        repo = self.get_repository(repo_full_name)
        return repo.get_pull(pr_number)
    
    def get_pr_files(self, repo_full_name: str, pr_number: int) -> List[Dict]:
        """
        Get files changed in a pull request.
        
        Args:
            repo_full_name: Full repository name
            pr_number: Pull request number
        
        Returns:
            List of file information dictionaries
        """
        pr = self.get_pull_request(repo_full_name, pr_number)
        files = []
        
        for file in pr.get_files():
            files.append({
                'filename': file.filename,
                'status': file.status,
                'additions': file.additions,
                'deletions': file.deletions,
                'changes': file.changes,
                'patch': file.patch if hasattr(file, 'patch') else None,
            })
        
        return files
    
    def post_review_comment(
        self,
        repo_full_name: str,
        pr_number: int,
        body: str,
        commit_id: Optional[str] = None,
        event: str = "COMMENT"
    ) -> None:
        """
        Post a review comment on a pull request.
        
        Uses issue comments by default for better compatibility with GitHub Actions.
        Falls back to create_review if issue comments fail.
        
        Args:
            repo_full_name: Full repository name
            pr_number: Pull request number
            body: Comment body
            commit_id: Specific commit to comment on (optional)
            event: Review event type (COMMENT, APPROVE, REQUEST_CHANGES)
        """
        try:
            pr = self.get_pull_request(repo_full_name, pr_number)
            
            # Try issue comment first (more reliable with GitHub Actions token)
            try:
                pr.create_issue_comment(body)
                return
            except GithubException as issue_comment_error:
                # If issue comment fails, try create_review as fallback
                if commit_id:
                    commit = pr.base.repo.get_commit(commit_id)
                else:
                    # Get the latest commit
                    commits = list(pr.get_commits())
                    commit = commits[-1] if commits else None
                
                if commit:
                    pr.create_review(
                        commit=commit,
                        body=body,
                        event=event
                    )
                else:
                    # Re-raise the original issue comment error if no fallback worked
                    raise issue_comment_error
        
        except GithubException as e:
            raise Exception(f"Failed to post review comment: {str(e)}")
    
    def post_issue_comment(self, repo_full_name: str, pr_number: int, body: str) -> None:
        """
        Post a regular comment on a pull request.
        
        Args:
            repo_full_name: Full repository name
            pr_number: Pull request number
            body: Comment body
        """
        try:
            pr = self.get_pull_request(repo_full_name, pr_number)
            pr.create_issue_comment(body)
        except GithubException as e:
            raise Exception(f"Failed to post comment: {str(e)}")
    
    def get_pr_diff(self, repo_full_name: str, pr_number: int) -> str:
        """
        Get the full diff of a pull request.
        
        Args:
            repo_full_name: Full repository name
            pr_number: Pull request number
        
        Returns:
            Full diff as a string
        """
        pr = self.get_pull_request(repo_full_name, pr_number)
        
        # Compile all file patches into a single diff
        files = pr.get_files()
        diff_parts = []
        
        for file in files:
            if hasattr(file, 'patch') and file.patch:
                diff_parts.append(f"--- a/{file.filename}")
                diff_parts.append(f"+++ b/{file.filename}")
                diff_parts.append(file.patch)
                diff_parts.append("")
        
        return "\n".join(diff_parts)
