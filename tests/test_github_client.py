"""
Tests for GitHub client.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from github import GithubException
from bot.github_client import GitHubClient


class TestGitHubClient:
    """Test cases for GitHubClient."""
    
    def test_init_with_token(self):
        """Test initialization with token parameter."""
        client = GitHubClient(access_token='test-token')
        assert client.access_token == 'test-token'
    
    @patch.dict('os.environ', {'GITHUB_TOKEN': 'env-token'})
    def test_init_with_env_var(self):
        """Test initialization with environment variable."""
        client = GitHubClient()
        assert client.access_token == 'env-token'
    
    @patch.dict('os.environ', {}, clear=True)
    def test_init_missing_token(self):
        """Test initialization fails without token."""
        with pytest.raises(ValueError, match="GitHub access token is required"):
            GitHubClient()
    
    @patch('bot.github_client.Github')
    def test_post_review_comment_uses_issue_comment_first(self, mock_github_class):
        """Test that post_review_comment tries issue comment first."""
        # Setup mocks
        mock_github = MagicMock()
        mock_github_class.return_value = mock_github
        
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_github.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr
        
        # Create client
        client = GitHubClient(access_token='test-token')
        
        # Call method
        client.post_review_comment(
            repo_full_name='owner/repo',
            pr_number=1,
            body='Test review'
        )
        
        # Verify issue comment was called
        mock_pr.create_issue_comment.assert_called_once_with('Test review')
        # Verify create_review was NOT called
        mock_pr.create_review.assert_not_called()
    
    @patch('bot.github_client.Github')
    def test_post_review_comment_fallback_to_review(self, mock_github_class):
        """Test fallback to create_review when issue comment fails with 403."""
        # Setup mocks
        mock_github = MagicMock()
        mock_github_class.return_value = mock_github
        
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_commit = MagicMock()
        
        mock_github.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr
        
        # Make issue comment fail with 403
        mock_pr.create_issue_comment.side_effect = GithubException(
            403, 
            {'message': 'Resource not accessible by integration'},
            None
        )
        
        # Setup commits
        mock_pr.get_commits.return_value = [mock_commit]
        
        # Create client
        client = GitHubClient(access_token='test-token')
        
        # Call method
        client.post_review_comment(
            repo_full_name='owner/repo',
            pr_number=1,
            body='Test review'
        )
        
        # Verify issue comment was attempted
        mock_pr.create_issue_comment.assert_called_once()
        # Verify create_review was called as fallback
        mock_pr.create_review.assert_called_once_with(
            commit=mock_commit,
            body='Test review',
            event='COMMENT'
        )
    
    @patch('bot.github_client.Github')
    def test_post_review_comment_no_fallback_for_other_errors(self, mock_github_class):
        """Test that non-403 errors propagate immediately without fallback."""
        # Setup mocks
        mock_github = MagicMock()
        mock_github_class.return_value = mock_github
        
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        
        mock_github.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr
        
        # Make issue comment fail with 429 (rate limit)
        mock_pr.create_issue_comment.side_effect = GithubException(
            429, 
            {'message': 'Rate limit exceeded'},
            None
        )
        
        # Create client
        client = GitHubClient(access_token='test-token')
        
        # Call method and expect exception
        with pytest.raises(Exception, match="Failed to post review comment"):
            client.post_review_comment(
                repo_full_name='owner/repo',
                pr_number=1,
                body='Test review'
            )
        
        # Verify issue comment was attempted
        mock_pr.create_issue_comment.assert_called_once()
        # Verify create_review was NOT called (no fallback for non-403 errors)
        mock_pr.create_review.assert_not_called()
    
    @patch('bot.github_client.Github')
    def test_post_issue_comment(self, mock_github_class):
        """Test posting issue comment directly."""
        # Setup mocks
        mock_github = MagicMock()
        mock_github_class.return_value = mock_github
        
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_github.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr
        
        # Create client
        client = GitHubClient(access_token='test-token')
        
        # Call method
        client.post_issue_comment(
            repo_full_name='owner/repo',
            pr_number=1,
            body='Test comment'
        )
        
        # Verify
        mock_pr.create_issue_comment.assert_called_once_with('Test comment')
    
    @patch('bot.github_client.Github')
    def test_get_pr_files(self, mock_github_class):
        """Test getting PR files."""
        # Setup mocks
        mock_github = MagicMock()
        mock_github_class.return_value = mock_github
        
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_file = MagicMock()
        
        mock_file.filename = 'test.xaml'
        mock_file.status = 'modified'
        mock_file.additions = 10
        mock_file.deletions = 5
        mock_file.changes = 15
        mock_file.patch = '+ added line'
        
        mock_github.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr
        mock_pr.get_files.return_value = [mock_file]
        
        # Create client
        client = GitHubClient(access_token='test-token')
        
        # Call method
        files = client.get_pr_files('owner/repo', 1)
        
        # Verify
        assert len(files) == 1
        assert files[0]['filename'] == 'test.xaml'
        assert files[0]['additions'] == 10
        assert files[0]['deletions'] == 5

    @patch('bot.github_client.Github')
    def test_post_inline_review_success(self, mock_github_class):
        """Test posting inline review with comments."""
        mock_github = MagicMock()
        mock_github_class.return_value = mock_github
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_commit = MagicMock()
        mock_github.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr
        mock_pr.get_commits.return_value = [mock_commit]

        client = GitHubClient(access_token='test-token')
        comments = [
            {"path": "test.py", "position": 3, "body": "Fix this"},
        ]
        client.post_inline_review('owner/repo', 1, comments, "Summary")

        mock_pr.create_review.assert_called_once_with(
            commit=mock_commit,
            body="Summary",
            event="COMMENT",
            comments=comments,
        )

    @patch('bot.github_client.Github')
    def test_post_inline_review_empty_comments_uses_issue_comment(self, mock_github_class):
        """When no inline comments, fall back to issue comment."""
        mock_github = MagicMock()
        mock_github_class.return_value = mock_github
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_github.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr

        client = GitHubClient(access_token='test-token')
        client.post_inline_review('owner/repo', 1, [], "Summary only")

        mock_pr.create_issue_comment.assert_called_once_with("Summary only")
        mock_pr.create_review.assert_not_called()

    @patch('bot.github_client.Github')
    def test_post_inline_review_403_fallback(self, mock_github_class):
        """Test 403 fallback to issue comment with formatted body."""
        mock_github = MagicMock()
        mock_github_class.return_value = mock_github
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_commit = MagicMock()
        mock_github.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr
        mock_pr.get_commits.return_value = [mock_commit]
        mock_pr.create_review.side_effect = GithubException(
            403, {'message': 'Forbidden'}, None
        )

        client = GitHubClient(access_token='test-token')
        comments = [{"path": "test.py", "position": 3, "body": "Fix this"}]
        client.post_inline_review('owner/repo', 1, comments, "Summary")

        # Should have fallen back to issue comment
        mock_pr.create_issue_comment.assert_called_once()
        call_body = mock_pr.create_issue_comment.call_args[0][0]
        assert "Summary" in call_body
        assert "Fix this" in call_body
