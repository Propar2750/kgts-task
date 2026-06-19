"""Tests for win/line detection."""

from order_chaos import constants as C
from order_chaos import board as B
from order_chaos import patterns as P


def _board_from_rows(rows):
    """Build a board from a list of 6 strings using '.', 'X', 'O'."""
    out = B.new_board()
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            out[r][c] = C.EMPTY if ch == "." else ch
    return out


def test_no_five_returns_none():
    assert P.find_straight_five(B.new_board()) is None


def test_horizontal_five():
    board = _board_from_rows(
        [
            "......",
            "......",
            "XXXXX.",
            "......",
            "......",
            "......",
        ]
    )
    line = P.find_straight_five(board)
    assert line is not None
    assert set(line) == {(2, 0), (2, 1), (2, 2), (2, 3), (2, 4)}


def test_vertical_five():
    board = B.new_board()
    for r in range(5):
        board[r][3] = C.O
    line = P.find_straight_five(board)
    assert set(line) == {(0, 3), (1, 3), (2, 3), (3, 3), (4, 3)}


def test_diagonal_down_right_five():
    board = B.new_board()
    for i in range(5):
        board[i][i] = C.X
    line = P.find_straight_five(board)
    assert set(line) == {(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)}


def test_diagonal_down_left_five():
    board = B.new_board()
    for i in range(5):
        board[i][5 - i] = C.O
    line = P.find_straight_five(board)
    assert set(line) == {(0, 5), (1, 4), (2, 3), (3, 2), (4, 1)}


def test_five_at_bottom_right_corner():
    board = B.new_board()
    for c in range(1, 6):
        board[5][c] = C.X
    line = P.find_straight_five(board)
    assert set(line) == {(5, 1), (5, 2), (5, 3), (5, 4), (5, 5)}


def test_six_in_a_row_contains_a_five():
    board = _board_from_rows(
        [
            "OOOOOO",
            "......",
            "......",
            "......",
            "......",
            "......",
        ]
    )
    line = P.find_straight_five(board)
    assert line is not None
    assert len(line) == C.WIN_LENGTH


def test_mixed_symbols_do_not_count():
    board = _board_from_rows(
        [
            "XXXXO.",
            "......",
            "......",
            "......",
            "......",
            "......",
        ]
    )
    assert P.find_straight_five(board) is None


def test_count_straight_fours_horizontal():
    board = _board_from_rows(
        [
            "XXXX..",
            "......",
            "......",
            "......",
            "......",
            "......",
        ]
    )
    assert P.count_straight_fours(board) == 1


def test_count_straight_fours_none():
    assert P.count_straight_fours(B.new_board()) == 0
