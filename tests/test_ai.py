"""Tests for the minimax + alpha-beta AI."""

import random

from order_chaos import constants as C
from order_chaos import board as B
from order_chaos.game import GameState, apply_move, is_legal
from order_chaos import ai


def _state(rows, current=C.Player.ORDER):
    """Build an IN_PROGRESS GameState from rows of '.', 'X', 'O'."""
    board = B.new_board()
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            board[r][c] = C.EMPTY if ch == "." else ch
    return GameState(board=board, current_player=current, status=C.Status.IN_PROGRESS)


EMPTY_ROWS = ["......"] * 6


# --- evaluation ------------------------------------------------------------

def test_evaluate_empty_board_is_zero():
    assert ai.evaluate(B.new_board()) == 0


def test_evaluate_rewards_longer_lines():
    three = _state(["XXX...", *["......"] * 5]).board
    four = _state(["XXXX..", *["......"] * 5]).board
    assert ai.evaluate(four) > ai.evaluate(three) > 0


def test_evaluate_dead_window_scores_lower_than_open():
    open4 = _state(["XXXX..", *["......"] * 5]).board
    blocked4 = _state(["XXXXO.", *["......"] * 5]).board
    # an O blocking the line kills those windows -> lower score for Order
    assert ai.evaluate(open4) > ai.evaluate(blocked4)


# --- tactics ---------------------------------------------------------------

def test_order_takes_the_immediate_win():
    # Order to move with four X's on row 0; the winning move is (0,4).
    state = _state(["XXXX..", *["......"] * 5], current=C.Player.ORDER)
    move = ai.choose_move(state, "hard")
    after = apply_move(state, move.row, move.col, move.symbol)
    assert after.status == C.Status.ORDER_WIN


def test_chaos_blocks_the_immediate_threat():
    # Chaos to move; Order threatens (0,4) for five. Chaos must occupy (0,4).
    state = _state(["XXXX..", *["......"] * 5], current=C.Player.CHAOS)
    move = ai.choose_move(state, "medium")
    assert (move.row, move.col) == (0, 4)
    after = apply_move(state, move.row, move.col, move.symbol)
    assert after.status == C.Status.IN_PROGRESS  # threat neutralized


def test_first_move_plays_center():
    state = _state(EMPTY_ROWS, current=C.Player.ORDER)
    move = ai.choose_move(state, "hard")
    assert (move.row, move.col) == ai.CENTER


# --- difficulty ------------------------------------------------------------

def test_choose_move_legal_for_all_difficulties():
    state = _state(["X.....", "..O...", *["......"] * 4], current=C.Player.ORDER)
    for diff in ("easy", "medium", "hard"):
        move = ai.choose_move(state, diff, rng=random.Random(1))
        assert is_legal(state, move.row, move.col, move.symbol)


def test_easy_random_branch_returns_legal_move():
    # Force the random branch (rng.random() < 0.3) and confirm a legal move.
    state = _state(["XXXX..", *["......"] * 5], current=C.Player.ORDER)

    class AlwaysRandom(random.Random):
        def random(self):
            return 0.0

    move = ai.choose_move(state, "easy", rng=AlwaysRandom(0))
    assert is_legal(state, move.row, move.col, move.symbol)


def test_hard_is_deterministic_on_winning_position():
    # Hard never takes the random branch; it must find the win.
    state = _state(["XXXX..", *["......"] * 5], current=C.Player.ORDER)
    move = ai.choose_move(state, "hard", rng=random.Random(99))
    after = apply_move(state, move.row, move.col, move.symbol)
    assert after.status == C.Status.ORDER_WIN


def test_unknown_difficulty_raises():
    state = _state(EMPTY_ROWS)
    try:
        ai.choose_move(state, "impossible")
        assert False, "expected ValueError"
    except ValueError:
        pass
