"""Line / win detection for the Order & Chaos board.

The board is tiny (6x6), so detection is a straightforward scan of every
straight-line window in the four orientations: horizontal, vertical, and the
two diagonals.
"""

from __future__ import annotations

from typing import Optional

from .constants import BOARD_SIZE, WIN_LENGTH, FOUR_LENGTH, EMPTY

# Direction vectors: right, down, down-right, down-left.
# Scanning each window once in these four directions covers every line on the
# board exactly once (the reverse directions would just re-find the same lines).
DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]


def _window(board, row: int, col: int, dr: int, dc: int, length: int):
    """Return the cells of the length-N window from (row, col) in (dr, dc).

    Returns None if the window runs off the board.
    """
    cells = []
    for i in range(length):
        r, c = row + dr * i, col + dc * i
        if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
            return None
        cells.append((r, c))
    return cells


def _iter_lines(board, length: int):
    """Yield every length-N window on the board as a list of (r, c) cells."""
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            for dr, dc in DIRECTIONS:
                cells = _window(board, r, c, dr, dc, length)
                if cells is not None:
                    yield cells


def line_windows(board, length: int):
    """Public: yield every length-N straight-line window as a list of cells.

    Used by the AI's evaluation function to score line potential.
    """
    return _iter_lines(board, length)


def _all_same_symbol(board, cells) -> bool:
    """True if every cell in the window holds the same non-empty symbol."""
    first = board[cells[0][0]][cells[0][1]]
    if first == EMPTY:
        return False
    return all(board[r][c] == first for r, c in cells)


def find_straight_five(board) -> Optional[list[tuple[int, int]]]:
    """Return the five cells of a straight-5, or None if none exists.

    A straight-5 is five identical symbols in a horizontal, vertical, or
    diagonal line. Returns the first one found.
    """
    for cells in _iter_lines(board, WIN_LENGTH):
        if _all_same_symbol(board, cells):
            return cells
    return None


def count_straight_fours(board) -> int:
    """Count the length-4 same-symbol windows on the board.

    Forward-looking helper for the two-round tiebreaker; the single-round
    engine does not use it for win resolution.
    """
    return sum(
        1 for cells in _iter_lines(board, FOUR_LENGTH) if _all_same_symbol(board, cells)
    )
