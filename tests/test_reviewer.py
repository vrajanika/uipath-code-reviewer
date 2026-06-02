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

    def test_review_file_structured_success(self):
        """Test structured file review."""
        mock_azure = Mock()
        mock_azure.review_code_structured.return_value = {
            'summary': 'File looks good overall.',
            'comments': [
                {'line': 2, 'body': 'Consider renaming this variable.', 'severity': 'suggestion'},
            ]
        }

        reviewer = CodeReviewer(
            github_client=Mock(),
            azure_client=mock_azure,
        )

        file = {
            'filename': 'test.py',
            'patch': '@@ -1,3 +1,4 @@\n ctx\n+new\n ctx2',
            'additions': 1,
            'deletions': 0,
        }

        result = reviewer._review_file_structured(file)
        assert result['status'] == 'reviewed'
        assert result['summary'] == 'File looks good overall.'
        assert len(result['inline_comments']) == 1
        assert result['inline_comments'][0]['line'] == 2

    def test_review_pull_request_inline_mode(self):
        """Test full review in inline mode."""
        mock_github = Mock()
        mock_github.get_pr_files.return_value = [
            {
                'filename': 'Main.xaml',
                'status': 'modified',
                'additions': 5,
                'deletions': 2,
                'changes': 7,
                'patch': '@@ -1,3 +1,5 @@\n ctx\n-old\n+new1\n+new2\n ctx2',
            }
        ]
        mock_azure = Mock()
        mock_azure.review_code_structured.return_value = {
            'summary': 'Changes look reasonable.',
            'comments': [
                {'line': 2, 'body': 'Good change.', 'severity': 'praise'},
            ]
        }

        reviewer = CodeReviewer(
            github_client=mock_github,
            azure_client=mock_azure,
        )

        result = reviewer.review_pull_request(
            'owner/repo', 1, post_comments=False, inline_comments=True
        )
        assert result['status'] == 'success'
        assert 'inline_comments' in result
        assert len(result['inline_comments']) == 1
        assert result['inline_comments'][0]['path'] == 'Main.xaml'

    def test_review_pull_request_inline_skips_invalid_lines(self):
        """Test that comments referencing lines not in the diff are dropped."""
        mock_github = Mock()
        mock_github.get_pr_files.return_value = [
            {
                'filename': 'Main.xaml',
                'status': 'modified',
                'additions': 1,
                'deletions': 0,
                'changes': 1,
                'patch': '@@ -1,2 +1,3 @@\n ctx\n+new\n ctx2',
            }
        ]
        mock_azure = Mock()
        mock_azure.review_code_structured.return_value = {
            'summary': 'OK',
            'comments': [
                {'line': 999, 'body': 'This line does not exist.', 'severity': 'issue'},
            ]
        }

        reviewer = CodeReviewer(
            github_client=mock_github,
            azure_client=mock_azure,
        )

        result = reviewer.review_pull_request(
            'owner/repo', 1, post_comments=False, inline_comments=True
        )
        assert result['inline_comments'] == []

    def test_review_pull_request_legacy_mode(self):
        """Test that legacy mode still works via inline_comments=False."""
        mock_github = Mock()
        mock_github.get_pr_files.return_value = [
            {
                'filename': 'Main.xaml',
                'status': 'modified',
                'additions': 1,
                'deletions': 0,
                'changes': 1,
                'patch': '@@ -1,2 +1,3 @@\n ctx\n+new\n ctx2',
            }
        ]
        mock_azure = Mock()
        mock_azure.review_code.return_value = "Legacy review text"

        reviewer = CodeReviewer(
            github_client=mock_github,
            azure_client=mock_azure,
        )

        result = reviewer.review_pull_request(
            'owner/repo', 1, post_comments=False, inline_comments=False
        )
        assert result['status'] == 'success'
        assert 'overall_review' in result
        assert 'inline_comments' not in result

    def test_compile_inline_review_summary(self):
        """Test compiling inline review summary."""
        reviewer = CodeReviewer(
            github_client=Mock(),
            azure_client=Mock(),
        )

        file_summaries = [
            {
                'filename': 'test.py',
                'summary': 'Looks good.',
                'additions': 5,
                'deletions': 2,
            }
        ]

        summary = reviewer._compile_inline_review_summary(file_summaries)
        assert 'test.py' in summary
        assert 'Looks good.' in summary
        assert '+5 -2' in summary
        assert 'Reviewed 1 file(s)' in summary

    def test_review_inline_with_suggested_fix(self):
        """Test that suggestion block is appended when suggested_fix is present."""
        mock_github = Mock()
        mock_github.get_pr_files.return_value = [
            {
                'filename': 'Main.xaml',
                'status': 'modified',
                'additions': 1,
                'deletions': 0,
                'changes': 1,
                'patch': '@@ -1,2 +1,3 @@\n ctx\n+new\n ctx2',
            }
        ]
        mock_azure = Mock()
        mock_azure.review_code_structured.return_value = {
            'summary': 'Rename variable.',
            'comments': [
                {
                    'line': 2,
                    'body': 'Use a descriptive name.',
                    'severity': 'issue',
                    'suggested_fix': '    better_name = compute()',
                },
            ]
        }

        reviewer = CodeReviewer(
            github_client=mock_github,
            azure_client=mock_azure,
        )

        result = reviewer.review_pull_request(
            'owner/repo', 1, post_comments=False, inline_comments=True
        )
        assert len(result['inline_comments']) == 1
        body = result['inline_comments'][0]['body']
        assert '```suggestion' in body
        assert '    better_name = compute()' in body
        assert body.endswith('\n```')

    def test_review_inline_without_suggested_fix_unchanged(self):
        """Test that no suggestion block appears when suggested_fix is absent."""
        mock_github = Mock()
        mock_github.get_pr_files.return_value = [
            {
                'filename': 'Main.xaml',
                'status': 'modified',
                'additions': 1,
                'deletions': 0,
                'changes': 1,
                'patch': '@@ -1,2 +1,3 @@\n ctx\n+new\n ctx2',
            }
        ]
        mock_azure = Mock()
        mock_azure.review_code_structured.return_value = {
            'summary': 'Looks good.',
            'comments': [
                {'line': 2, 'body': 'Nice work here.', 'severity': 'praise'},
            ]
        }

        reviewer = CodeReviewer(
            github_client=mock_github,
            azure_client=mock_azure,
        )

        result = reviewer.review_pull_request(
            'owner/repo', 1, post_comments=False, inline_comments=True
        )
        assert len(result['inline_comments']) == 1
        body = result['inline_comments'][0]['body']
        assert '```suggestion' not in body

    def test_review_inline_mixed_comments(self):
        """Test mix of comments with and without suggested_fix."""
        mock_github = Mock()
        mock_github.get_pr_files.return_value = [
            {
                'filename': 'workflow.xaml',
                'status': 'modified',
                'additions': 3,
                'deletions': 0,
                'changes': 3,
                'patch': '@@ -1,2 +1,5 @@\n ctx\n+line1\n+line2\n+line3\n ctx2',
            }
        ]
        mock_azure = Mock()
        mock_azure.review_code_structured.return_value = {
            'summary': 'Mixed feedback.',
            'comments': [
                {
                    'line': 2,
                    'body': 'Fix naming.',
                    'severity': 'issue',
                    'suggested_fix': '    x = 1',
                },
                {
                    'line': 3,
                    'body': 'Good pattern.',
                    'severity': 'praise',
                },
                {
                    'line': 4,
                    'body': 'Add type hint.',
                    'severity': 'suggestion',
                    'suggested_fix': '    count: int = 0',
                },
            ]
        }

        reviewer = CodeReviewer(
            github_client=mock_github,
            azure_client=mock_azure,
        )

        result = reviewer.review_pull_request(
            'owner/repo', 1, post_comments=False, inline_comments=True
        )
        comments = result['inline_comments']
        assert len(comments) == 3

        # First comment has suggestion
        assert '```suggestion' in comments[0]['body']
        assert '    x = 1' in comments[0]['body']

        # Second comment (praise) has no suggestion
        assert '```suggestion' not in comments[1]['body']

        # Third comment has suggestion
        assert '```suggestion' in comments[2]['body']
        assert '    count: int = 0' in comments[2]['body']
