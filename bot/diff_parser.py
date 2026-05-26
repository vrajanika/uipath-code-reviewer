"""
Diff position mapping utility.

Parses unified diff patches and maps file line numbers to GitHub diff positions,
which are required by GitHub's Pull Request Review API for inline comments.
"""

import re
from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class DiffLine:
    """Represents a single line within a diff patch."""
    position: int
    new_line_number: Optional[int]
    old_line_number: Optional[int]
    content: str
    line_type: str  # "add", "delete", or "context"


def parse_patch(patch: str) -> List[DiffLine]:
    """
    Parse a unified diff patch string into a list of DiffLine objects.

    Each non-header line in the patch gets a 1-based position value.
    The @@ hunk headers do NOT consume a position. The position counter
    does NOT reset between hunks.

    Args:
        patch: Raw patch string from GitHub's API (starts with @@ markers).

    Returns:
        List of DiffLine objects in order.
    """
    if not patch or not patch.strip():
        return []

    lines = patch.split('\n')
    result = []
    position_counter = 0
    current_new_line = 0
    current_old_line = 0

    hunk_header_re = re.compile(r'^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@')

    for line in lines:
        # Check for hunk header
        match = hunk_header_re.match(line)
        if match:
            current_old_line = int(match.group(1))
            current_new_line = int(match.group(2))
            continue

        # Skip empty trailing lines from split
        if position_counter == 0 and line == '' and not lines[-1]:
            continue

        position_counter += 1

        if line.startswith('+'):
            result.append(DiffLine(
                position=position_counter,
                new_line_number=current_new_line,
                old_line_number=None,
                content=line,
                line_type="add",
            ))
            current_new_line += 1
        elif line.startswith('-'):
            result.append(DiffLine(
                position=position_counter,
                new_line_number=None,
                old_line_number=current_old_line,
                content=line,
                line_type="delete",
            ))
            current_old_line += 1
        elif line.startswith('\\'):
            # "\ No newline at end of file" — counts as a position
            result.append(DiffLine(
                position=position_counter,
                new_line_number=None,
                old_line_number=None,
                content=line,
                line_type="context",
            ))
        else:
            # Context line (starts with space or is empty context)
            result.append(DiffLine(
                position=position_counter,
                new_line_number=current_new_line,
                old_line_number=current_old_line,
                content=line,
                line_type="context",
            ))
            current_new_line += 1
            current_old_line += 1

    return result


def build_position_map(patch: str) -> Dict[int, int]:
    """
    Build a mapping from new-file line numbers to diff positions.

    Only lines that appear in the diff have entries (context lines and
    added lines). Deleted lines are excluded since they have no new-file
    line number.

    Args:
        patch: Raw patch string from GitHub API.

    Returns:
        Dict mapping new_line_number -> diff position.
    """
    diff_lines = parse_patch(patch)
    position_map = {}

    for dl in diff_lines:
        if dl.new_line_number is not None:
            position_map[dl.new_line_number] = dl.position

    return position_map
