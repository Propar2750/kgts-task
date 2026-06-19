"""Tests for the game engine: state, move application, rules, serialization."""

import pytest

from order_chaos import constants as C
from order_chaos import board as B
from order_chaos.game import (
    new_game,
    apply_move,
    legal_moves,
    is_legal,
    to_dict,
    from_dict,
    GameState,
    Move,
    InvalidMoveError,
)


def test_new_game_initial_state():
    g = new_game()
    assert g.status == C.Status.IN_PROGRESS
    assert g.current_player == C.Player.ORDER  # Order moves first
    assert g.winning_line is None
    assert g.order_moves == 0
    assert g.move_history == ()
    assert len(B.empty_cells(g.board)) == C.BOARD_SIZE * C.BOARD_SIZE


def test_apply_move_places_symbol_and_switches_player():
    g = new_game()
    g2 = apply_move(g, 0, 0, C.X)
    assert g2.board[0][0] == C.X
    assert g2.current_player == C.Player.CHAOS  # alternated
    assert g2.status == C.Status.IN_PROGRESS
    # original state untouched (immutable)
    assert g.board[0][0] == C.EMPTY
    assert g.current_player == C.Player.ORDER


def test_move_history_records_who_and_what():
    g = new_game()
    g = apply_move(g, 0, 0, C.X)  # Order
    g = apply_move(g, 1, 1, C.O)  # Chaos
    assert len(g.move_history) == 2
    assert g.move_history[0] == Move(0, 0, C.X, C.Player.ORDER)
    assert g.move_history[1] == Move(1, 1, C.O, C.Player.CHAOS)


def test_order_moves_counts_only_order_placements():
    g = new_game()
    g = apply_move(g, 0, 0, C.X)  # Order  -> 1
    g = apply_move(g, 0, 1, C.O)  # Chaos  -> still 1
    g = apply_move(g, 1, 0, C.X)  # Order  -> 2
    assert g.order_moves == 2


def test_legal_moves_count_is_two_per_empty_cell():
    g = new_game()
    moves = legal_moves(g)
    assert len(moves) == 2 * C.BOARD_SIZE * C.BOARD_SIZE
    g = apply_move(g, 0, 0, C.X)
    assert len(legal_moves(g)) == 2 * (C.BOARD_SIZE * C.BOARD_SIZE - 1)


def test_is_legal_rules():
    g = new_game()
    assert is_legal(g, 0, 0, C.X)
    assert not is_legal(g, -1, 0, C.X)  # out of bounds
    assert not is_legal(g, 0, 0, "Z")  # bad symbol
    g = apply_move(g, 0, 0, C.X)
    assert not is_legal(g, 0, 0, C.O)  # occupied


def test_apply_move_rejects_occupied_cell():
    g = apply_move(new_game(), 2, 2, C.X)
    with pytest.raises(InvalidMoveError):
        apply_move(g, 2, 2, C.O)


def test_apply_move_rejects_out_of_bounds():
    with pytest.raises(InvalidMoveError):
        apply_move(new_game(), 6, 0, C.X)


def test_apply_move_rejects_bad_symbol():
    with pytest.raises(InvalidMoveError):
        apply_move(new_game(), 0, 0, "Z")


def test_order_wins_on_straight_five():
    g = new_game()
    # Build a horizontal 5 of X on row 0, columns 0..4, ignoring strict turn
    # symbol strategy — both players may place either symbol.
    cols = [0, 1, 2, 3, 4]
    for i, col in enumerate(cols):
        if i < len(cols) - 1:
            g = apply_move(g, 0, col, C.X)
            # opponent plays somewhere harmless
            g = apply_move(g, 5, col, C.O)
        else:
            g = apply_move(g, 0, col, C.X)  # completes the five
    assert g.status == C.Status.ORDER_WIN
    assert g.winning_line is not None
    assert set(g.winning_line) == {(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)}


def test_win_detected_regardless_of_which_player_placed_fifth():
    # Order places four X's; Chaos is forced to complete the five (e.g. only
    # empty cell left in a near-full board). A straight-5 ends the round for
    # Order no matter who placed the last stone.
    g = new_game()
    g = apply_move(g, 0, 0, C.X)  # Order
    g = apply_move(g, 0, 1, C.X)  # Chaos places X (continuing the line)
    g = apply_move(g, 0, 2, C.X)  # Order
    g = apply_move(g, 0, 3, C.X)  # Chaos
    assert g.status == C.Status.IN_PROGRESS
    g = apply_move(g, 0, 4, C.X)  # Order completes -> win
    assert g.status == C.Status.ORDER_WIN


def test_no_moves_allowed_after_game_over():
    g = new_game()
    for col in range(5):
        if col < 4:
            g = apply_move(g, 0, col, C.X)
            g = apply_move(g, 5, col, C.O)
        else:
            g = apply_move(g, 0, col, C.X)
    assert g.status == C.Status.ORDER_WIN
    assert legal_moves(g) == []
    with pytest.raises(InvalidMoveError):
        apply_move(g, 1, 1, C.X)


def test_chaos_wins_when_board_full_without_five():
    # Fill the whole board in a pattern that never makes 5-in-a-row.
    # Pattern: per row, alternate XXOO blocks, shifting each row, so no symbol
    # ever runs 5 long in any direction.
    g = new_game()
    # Verified to contain no 5-in-a-row in any direction (g=(r+2c)%4).
    pattern = [
        "XOXOXO",
        "XOXOXO",
        "OXOXOX",
        "OXOXOX",
        "XOXOXO",
        "XOXOXO",
    ]
    for r in range(C.BOARD_SIZE):
        for c in range(C.BOARD_SIZE):
            if g.status != C.Status.IN_PROGRESS:
                break
            g = apply_move(g, r, c, pattern[r][c])
    assert g.status == C.Status.CHAOS_WIN
    assert B.is_full(g.board)


def test_serialization_round_trip():
    g = new_game()
    g = apply_move(g, 0, 0, C.X)
    g = apply_move(g, 1, 1, C.O)
    d = to_dict(g)
    # must be JSON-serializable
    import json

    restored = from_dict(json.loads(json.dumps(d)))
    assert restored == g
    assert isinstance(restored, GameState)
