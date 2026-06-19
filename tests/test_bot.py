"""Tests for the placeholder bot."""

from order_chaos import constants as C
from order_chaos import board as B
from order_chaos.game import new_game, apply_move, legal_moves, is_legal
from order_chaos.bot import choose_move


def test_choose_move_returns_a_legal_move():
    g = new_game()
    move = choose_move(g, C.Player.ORDER)
    assert is_legal(g, move.row, move.col, move.symbol)


def test_choose_move_never_picks_occupied_cell():
    # Fill all but one cell; the bot must pick the single empty one.
    g = new_game()
    cells = [(r, c) for r in range(C.BOARD_SIZE) for c in range(C.BOARD_SIZE)]
    for (r, c) in cells[:-1]:
        # place directly on the board to avoid triggering wins / turn rules
        g = g.__class__(
            board=B.place(g.board, r, c, C.X if (r + c) % 2 else C.O),
            current_player=g.current_player,
            status=g.status,
        )
    last = cells[-1]
    move = choose_move(g, C.Player.CHAOS)
    assert (move.row, move.col) == last


def test_choose_move_symbol_is_x_or_o():
    g = new_game()
    move = choose_move(g, C.Player.ORDER)
    assert move.symbol in (C.X, C.O)


def test_choose_move_is_drop_in_for_apply_move():
    # A bot move should be directly applicable by the engine.
    g = new_game()
    move = choose_move(g, C.Player.ORDER)
    g2 = apply_move(g, move.row, move.col, move.symbol)
    assert g2.board[move.row][move.col] == move.symbol
