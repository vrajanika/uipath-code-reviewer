"""
Tests for diff position mapping utility.
"""

import pytest
from bot.diff_parser import parse_patch, build_position_map, get_line_content, DiffLine


class TestParsePatch:
    """Test cases for parse_patch."""

    def test_single_hunk_additions_only(self):
        """Patch with added lines and context."""
        patch = (
            "@@ -10,3 +10,5 @@ def foo():\n"
            " existing1\n"
            " existing2\n"
            "+new1\n"
            "+new2\n"
            " existing3"
        )
        lines = parse_patch(patch)
        assert len(lines) == 5
        assert lines[0].position == 1
        assert lines[0].new_line_number == 10
        assert lines[0].line_type == "context"
        assert lines[2].position == 3
        assert lines[2].new_line_number == 12
        assert lines[2].line_type == "add"
        assert lines[3].position == 4
        assert lines[3].new_line_number == 13
        assert lines[3].line_type == "add"

    def test_single_hunk_mixed(self):
        """Patch with adds, deletes, and context."""
        patch = (
            "@@ -5,4 +5,4 @@\n"
            " context\n"
            "-old_line\n"
            "+new_line\n"
            " context2"
        )
        lines = parse_patch(patch)
        assert len(lines) == 4
        assert lines[1].line_type == "delete"
        assert lines[1].old_line_number == 6
        assert lines[1].new_line_number is None
        assert lines[2].line_type == "add"
        assert lines[2].new_line_number == 6

    def test_multiple_hunks_position_continues(self):
        """Position counter does NOT reset between hunks."""
        patch = (
            "@@ -1,3 +1,3 @@\n"
            " context1\n"
            "-old1\n"
            "+new1\n"
            "@@ -20,3 +20,3 @@\n"
            " context2\n"
            "-old2\n"
            "+new2"
        )
        lines = parse_patch(patch)
        # First hunk: positions 1, 2, 3
        assert lines[0].position == 1
        assert lines[2].position == 3
        # Second hunk: positions 4, 5, 6
        assert lines[3].position == 4
        assert lines[3].content == " context2"
        assert lines[5].position == 6
        assert lines[5].line_type == "add"

    def test_empty_patch(self):
        """Empty patch returns empty list."""
        assert parse_patch("") == []
        assert parse_patch("  ") == []

    def test_no_newline_marker(self):
        """'\\ No newline at end of file' counts as a position."""
        patch = (
            "@@ -1,2 +1,2 @@\n"
            "-old\n"
            "+new\n"
            "\\ No newline at end of file"
        )
        lines = parse_patch(patch)
        assert len(lines) == 3
        assert lines[2].position == 3
        assert lines[2].content.startswith("\\")

    def test_deletions_only(self):
        """Patch with only deletions."""
        patch = (
            "@@ -1,3 +1,1 @@\n"
            " context\n"
            "-deleted1\n"
            "-deleted2"
        )
        lines = parse_patch(patch)
        assert len(lines) == 3
        assert lines[1].line_type == "delete"
        assert lines[1].new_line_number is None
        assert lines[2].line_type == "delete"
        assert lines[2].new_line_number is None


class TestBuildPositionMap:
    """Test cases for build_position_map."""

    def test_basic_mapping(self):
        """Context and added lines map to positions."""
        patch = (
            "@@ -10,3 +10,5 @@\n"
            " existing1\n"
            " existing2\n"
            "+new1\n"
            "+new2\n"
            " existing3"
        )
        pos_map = build_position_map(patch)
        # existing1 -> new line 10, position 1
        assert pos_map[10] == 1
        # existing2 -> new line 11, position 2
        assert pos_map[11] == 2
        # new1 -> new line 12, position 3
        assert pos_map[12] == 3
        # new2 -> new line 13, position 4
        assert pos_map[13] == 4
        # existing3 -> new line 14, position 5
        assert pos_map[14] == 5

    def test_deleted_lines_excluded(self):
        """Deleted lines do not appear in the position map."""
        patch = (
            "@@ -5,3 +5,2 @@\n"
            " context\n"
            "-deleted\n"
            " context2"
        )
        pos_map = build_position_map(patch)
        assert 5 in pos_map  # context -> new line 5
        assert 6 in pos_map  # context2 -> new line 6
        # position 2 was the deleted line — no new_line_number
        assert pos_map[5] == 1
        assert pos_map[6] == 3

    def test_empty_patch(self):
        """Empty patch returns empty map."""
        assert build_position_map("") == {}

    def test_multiple_hunks(self):
        """Position map works across multiple hunks."""
        patch = (
            "@@ -1,2 +1,2 @@\n"
            " ctx1\n"
            "+add1\n"
            "@@ -10,2 +10,2 @@\n"
            " ctx2\n"
            "+add2"
        )
        pos_map = build_position_map(patch)
        assert pos_map[1] == 1   # ctx1
        assert pos_map[2] == 2   # add1
        assert pos_map[10] == 3  # ctx2
        assert pos_map[11] == 4  # add2


class TestGetLineContent:
    """Test cases for get_line_content."""

    def test_get_line_content_added_line(self):
        """Returns content of an added line with + prefix stripped."""
        patch = (
            "@@ -10,3 +10,5 @@\n"
            " existing1\n"
            " existing2\n"
            "+new1\n"
            "+new2\n"
            " existing3"
        )
        assert get_line_content(patch, 12) == "new1"
        assert get_line_content(patch, 13) == "new2"

    def test_get_line_content_context_line(self):
        """Returns content of a context line with space prefix stripped."""
        patch = (
            "@@ -10,3 +10,5 @@\n"
            " existing1\n"
            " existing2\n"
            "+new1\n"
            "+new2\n"
            " existing3"
        )
        assert get_line_content(patch, 10) == "existing1"
        assert get_line_content(patch, 14) == "existing3"

    def test_get_line_content_not_in_patch(self):
        """Returns None when the line number is not in the patch."""
        patch = (
            "@@ -10,2 +10,3 @@\n"
            " existing\n"
            "+added\n"
            " existing2"
        )
        assert get_line_content(patch, 999) is None

    def test_get_line_content_empty_patch(self):
        """Returns None for empty patch."""
        assert get_line_content("", 1) is None
        assert get_line_content("  ", 1) is None
