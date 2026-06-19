"""Tests for the two-round match layer."""

import json

import pytest

from order_chaos import constants as C
from order_chaos import board as B
from order_chaos.game import InvalidMoveError
from order_chaos.match import (
    new_match,
    apply_match_move,
    resolve_match,
    current_player_id,
    MatchStatus,
    MatchState,
    RoundResult,
    to_dict,
    from_dict,
)


# --- helpers ---------------------------------------------------------------

def _rr(order_player, five, moves, fours=0):
    """Build a RoundResult for resolve_match unit tests."""
    return RoundResult(
        round=1 if order_player == "P1" else 2,
        order_player=order_player,
        order_achieved_five=five,
        order_moves=moves,
        straight_fours=fours,
    )


# --- match setup & flow ----------------------------------------------------

def test_new_match_round1_order_is_p1():
    m = new_match()
    assert m.current_round == 1
    assert m.status == MatchStatus.IN_PROGRESS
    assert m.round.current_player == C.Player.ORDER
    assert current_player_id(m) == "P1"  # human (Order) moves first
    assert m.round_results == ()
    assert m.overall_winner is None


def test_apply_move_continues_round_and_switches_player():
    m = new_match()
    m = apply_match_move(m, 0, 0, C.X)
    assert m.current_round == 1
    assert m.status == MatchStatus.IN_PROGRESS
    assert m.round.status == C.Status.IN_PROGRESS
    assert current_player_id(m) == "P2"  # now Chaos (bot)


def test_move_after_match_complete_raises():
    m = _play_full_match_p1_six_p2_five()
    assert m.status == MatchStatus.COMPLETE
    with pytest.raises(InvalidMoveError):
        apply_match_move(m, 2, 2, C.X)


def test_round1_order_win_advances_to_round2_with_swapped_roles():
    m = new_match()
    # P1 (Order) makes a horizontal five on row 0; bot (Chaos) plays row 5.
    order_cols = [0, 1, 2, 3, 4]
    for i, col in enumerate(order_cols):
        m = apply_match_move(m, 0, col, C.X)
        if i < 4:
            m = apply_match_move(m, 5, col, C.O)
    # round 1 recorded
    assert len(m.round_results) == 1
    r1 = m.round_results[0]
    assert r1.order_player == "P1"
    assert r1.order_achieved_five is True
    assert r1.order_moves == 5
    # advanced to round 2: fresh board, roles swapped (P2 is now Order, moves first)
    assert m.current_round == 2
    assert m.status == MatchStatus.IN_PROGRESS
    assert B.empty_cells(m.round.board) == [(r, c) for r in range(6) for c in range(6)]
    assert m.round.current_player == C.Player.ORDER
    assert current_player_id(m) == "P2"


def _play_full_match_p1_six_p2_five():
    """P1 wins round 1 in 6 Order-moves; P2 wins round 2 in 5 -> P2 overall."""
    m = new_match()
    # Round 1: P1 Order wastes one move at (3,3), then five on row 0.
    m = apply_match_move(m, 3, 3, C.X)  # P1 waste (order_moves=1)
    m = apply_match_move(m, 5, 5, C.O)  # bot Chaos
    for i, col in enumerate([0, 1, 2, 3, 4]):
        m = apply_match_move(m, 0, col, C.X)  # P1 Order
        if i < 4:
            m = apply_match_move(m, 5, col, C.O)  # bot Chaos
    # now round 2: P2 is Order and moves first
    assert m.current_round == 2
    for i, col in enumerate([0, 1, 2, 3, 4]):
        m = apply_match_move(m, 0, col, C.X)  # P2 Order
        if i < 4:
            m = apply_match_move(m, 5, col, C.O)  # P1 Chaos
    return m


def test_full_match_p2_fewer_moves_wins():
    m = _play_full_match_p1_six_p2_five()
    assert m.status == MatchStatus.COMPLETE
    assert len(m.round_results) == 2
    assert m.round_results[0].order_moves == 6
    assert m.round_results[1].order_moves == 5
    assert m.overall_winner == "P2"
    assert m.winner_reason


# --- resolve_match: every tiebreaker branch --------------------------------

def test_case1_p2_fewer_moves():
    assert resolve_match(_rr("P1", True, 6), _rr("P2", True, 5))[0] == "P2"


def test_case1_p1_fewer_moves():
    assert resolve_match(_rr("P1", True, 5), _rr("P2", True, 6))[0] == "P1"


def test_case1_tie_more_fours_p2():
    assert resolve_match(_rr("P1", True, 5, 2), _rr("P2", True, 5, 3))[0] == "P2"


def test_case1_tie_more_fours_p1():
    assert resolve_match(_rr("P1", True, 5, 3), _rr("P2", True, 5, 2))[0] == "P1"


def test_case1_tie_equal_fours_draw():
    assert resolve_match(_rr("P1", True, 5, 2), _rr("P2", True, 5, 2))[0] == "DRAW"


def test_case1_p2_no_five_p1_wins():
    assert resolve_match(_rr("P1", True, 7), _rr("P2", False, 0))[0] == "P1"


def test_case2_p2_five_wins():
    assert resolve_match(_rr("P1", False, 0), _rr("P2", True, 9))[0] == "P2"


def test_case2_no_five_more_fours_p1():
    assert resolve_match(_rr("P1", False, 0, 3), _rr("P2", False, 0, 2))[0] == "P1"


def test_case2_no_five_more_fours_p2():
    assert resolve_match(_rr("P1", False, 0, 2), _rr("P2", False, 0, 3))[0] == "P2"


def test_case2_no_five_equal_fours_draw():
    assert resolve_match(_rr("P1", False, 0, 2), _rr("P2", False, 0, 2))[0] == "DRAW"


# --- serialization ---------------------------------------------------------

def test_match_serialization_round_trip():
    m = new_match()
    m = apply_match_move(m, 0, 0, C.X)
    m = apply_match_move(m, 1, 1, C.O)
    restored = from_dict(json.loads(json.dumps(to_dict(m))))
    assert restored == m
    assert isinstance(restored, MatchState)


def test_completed_match_serialization_round_trip():
    m = _play_full_match_p1_six_p2_five()
    restored = from_dict(json.loads(json.dumps(to_dict(m))))
    assert restored == m
    assert restored.overall_winner == "P2"
