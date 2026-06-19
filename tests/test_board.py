"""Tests for the low-level board helpers."""

from order_chaos import constants as C
from order_chaos import board as B


def test_new_board_is_empty_6x6():
    board = B.new_board()
    assert len(board) == C.BOARD_SIZE
    assert all(len(row) == C.BOARD_SIZE for row in board)
    assert all(cell == C.EMPTY for row in board for cell in row)


def test_in_bounds():
    assert B.in_bounds(0, 0)
    assert B.in_bounds(5, 5)
    assert not B.in_bounds(-1, 0)
    assert not B.in_bounds(0, 6)
    assert not B.in_bounds(6, 6)


def test_is_empty():
    board = B.new_board()
    assert B.is_empty(board, 2, 3)
    board = B.place(board, 2, 3, C.X)
    assert not B.is_empty(board, 2, 3)


def test_place_is_pure_and_returns_new_board():
    board = B.new_board()
    new = B.place(board, 1, 1, C.O)
    # original untouched
    assert board[1][1] == C.EMPTY
    # new board has the placement
    assert new[1][1] == C.O
    # it is a genuinely different object
    assert new is not board


def test_empty_cells():
    board = B.new_board()
    assert len(B.empty_cells(board)) == C.BOARD_SIZE * C.BOARD_SIZE
    board = B.place(board, 0, 0, C.X)
    cells = B.empty_cells(board)
    assert (0, 0) not in cells
    assert len(cells) == C.BOARD_SIZE * C.BOARD_SIZE - 1


def test_is_full():
    board = B.new_board()
    assert not B.is_full(board)
    for r in range(C.BOARD_SIZE):
        for c in range(C.BOARD_SIZE):
            board = B.place(board, r, c, C.X)
    assert B.is_full(board)


def test_copy_board_is_deep():
    board = B.new_board()
    clone = B.copy_board(board)
    clone[0][0] = C.X
    assert board[0][0] == C.EMPTY
    assert clone is not board
