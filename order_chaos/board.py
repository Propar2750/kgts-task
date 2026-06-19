"""Low-level 6x6 grid helpers.

A board is a ``list[list[Optional[str]]]`` where each cell is ``EMPTY`` (None),
``X``, or ``O``. All helpers are pure: nothing here mutates a board passed in,
except ``copy_board`` which returns an independent copy you own.
"""

from __future__ import annotations

from typing import Optional

from .constants import BOARD_SIZE, EMPTY

Board = list  # alias for readability; concretely list[list[Optional[str]]]


def new_board() -> Board:
    """Return a fresh empty 6x6 board."""
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]


def in_bounds(row: int, col: int) -> bool:
    """True if (row, col) is a valid cell on the board."""
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


def is_empty(board: Board, row: int, col: int) -> bool:
    """True if the given cell holds no symbol."""
    return board[row][col] == EMPTY


def is_full(board: Board) -> bool:
    """True if every cell holds a symbol."""
    return all(cell != EMPTY for row in board for cell in row)


def empty_cells(board: Board) -> list[tuple[int, int]]:
    """Return the coordinates of every empty cell, row-major order."""
    return [
        (r, c)
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if board[r][c] == EMPTY
    ]


def copy_board(board: Board) -> Board:
    """Return an independent deep copy of the board."""
    return [row[:] for row in board]


def place(board: Board, row: int, col: int, symbol: Optional[str]) -> Board:
    """Return a NEW board with ``symbol`` placed at (row, col).

    Pure: the input board is left unchanged.
    """
    new = copy_board(board)
    new[row][col] = symbol
    return new
