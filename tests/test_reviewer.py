"""
Tests for Code Reviewer.
"""

import pytest
from unittest.mock import Mock, MagicMock
from bot.reviewer import CodeReviewer


class TestCodeReviewer:
    """Test cases for CodeReviewer."""
    
    def test_filter_uipath_files_xaml(self):
        """Test filtering UiPath XAML files."""
        reviewer = CodeReviewer(
            github_client=Mock(),
            azure_client=Mock(),
        )
        
        files = [
            {'filename': 'Main.xaml', 'patch': 'test'},
            {'filename': 'README.md', 'patch': 'test'},
            {'filename': 'workflow.xaml', 'patch': 'test'},
        ]
        
        filtered = reviewer._filter_uipath_files(files)
        assert len(filtered) == 2
        assert all(f['filename'].endswith('.xaml') for f in filtered)
    
    def test_filter_uipath_files_json(self):
        """Test filtering UiPath JSON files."""
        reviewer = CodeReviewer(
            github_client=Mock(),
            azure_client=Mock(),
        )
        
        files = [
            {'filename': 'project.json', 'patch': 'test'},
            {'filename': 'data.json', 'patch': 'test'},
            {'filename': 'test.py', 'patch': 'test'},
        ]
        
        filtered = reviewer._filter_uipath_files(files)
        assert len(filtered) == 2
        assert all(f['filename'].endswith('.json') for f in filtered)
    
    def test_compile_overall_review(self):
        """Test compiling overall review."""
        reviewer = CodeReviewer(
            github_client=Mock(),
            azure_client=Mock(),
        )
        
        reviews = [
            {
                'filename': 'test.xaml',
                'status': 'reviewed',
                'comment': 'Looks good!',
                'additions': 10,
                'deletions': 5,
            }
        ]
        
        overall = reviewer._compile_overall_review(reviews)
        assert 'test.xaml' in overall
        assert 'Looks good!' in overall
        assert '+10 -5' in overall
        assert 'UiPath Code Review' in overall
    
    def test_review_file_success(self):
        """Test successful file review."""
        mock_azure = Mock()
        mock_azure.review_code.return_value = "Great code!"
        
        reviewer = CodeReviewer(
            github_client=Mock(),
            azure_client=mock_azure,
        )
        
        file = {
            'filename': 'test.xaml',
            'patch': '+ new line',
            'additions': 1,
            'deletions': 0,
        }
        
        result = reviewer._review_file(file)
        assert result['status'] == 'reviewed'
        assert result['comment'] == 'Great code!'
        assert result['filename'] == 'test.xaml'
    
    def test_review_pull_request_no_files(self):
        """Test review when no files are changed."""
        mock_github = Mock()
        mock_github.get_pr_files.return_value = []
        
        reviewer = CodeReviewer(
            github_client=mock_github,
            azure_client=Mock(),
        )
        
        result = reviewer.review_pull_request('owner/repo', 1, post_comments=False)
        assert result['status'] == 'no_changes'
    
    def test_review_pull_request_no_uipath_files(self):
        """Test review when no UiPath files are changed."""
        mock_github = Mock()
        mock_github.get_pr_files.return_value = [
            {'filename': 'README.md', 'patch': 'test'}
        ]
        
        reviewer = CodeReviewer(
            github_client=mock_github,
            azure_client=Mock(),
        )
        
        result = reviewer.review_pull_request(
            'owner/repo', 1, post_comments=False, focus_on_uipath=True
        )
        assert result['status'] == 'no_uipath_files'
