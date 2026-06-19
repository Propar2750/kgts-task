"""Tests for the FastAPI match API."""

from fastapi.testclient import TestClient

from order_chaos import constants as C
from order_chaos.match import new_match, apply_match_move, to_dict
from api.main import app

client = TestClient(app)


def _new():
    return client.post("/api/match/new").json()


def test_new_match_shape():
    state = _new()
    assert state["current_round"] == 1
    assert state["status"] == "IN_PROGRESS"
    assert state["current_player_id"] == "P1"  # human (Order) to move
    assert state["human_role"] == "ORDER"


def test_human_move_gets_bot_reply_and_returns_to_p1():
    state = _new()
    resp = client.post(
        "/api/match/move",
        json={"state": state, "row": 2, "col": 2, "symbol": C.X},
    )
    assert resp.status_code == 200
    body = resp.json()
    # human's symbol landed
    assert body["state"]["round"]["board"][2][2] == C.X
    # bot replied at least once
    assert len(body["bot_moves"]) >= 1
    # invariant: control returns to the human (or the match is over)
    new_state = body["state"]
    assert new_state["current_player_id"] in ("P1", None)


def test_illegal_move_returns_400():
    state = _new()
    resp = client.post(
        "/api/match/move",
        json={"state": state, "row": 6, "col": 0, "symbol": C.X},  # out of bounds
    )
    assert resp.status_code == 400


def test_move_on_completed_match_returns_400():
    # Build a completed match deterministically (no bot), then POST a move.
    m = new_match()
    m = apply_match_move(m, 3, 3, C.X)  # P1 waste
    m = apply_match_move(m, 5, 5, C.O)  # P2 Chaos
    for i, col in enumerate([0, 1, 2, 3, 4]):
        m = apply_match_move(m, 0, col, C.X)  # P1 Order -> five (6 moves)
        if i < 4:
            m = apply_match_move(m, 5, col, C.O)
    for i, col in enumerate([0, 1, 2, 3, 4]):
        m = apply_match_move(m, 0, col, C.X)  # P2 Order -> five (5 moves)
        if i < 4:
            m = apply_match_move(m, 5, col, C.O)
    assert m.status.value == "COMPLETE"
    resp = client.post(
        "/api/match/move",
        json={"state": to_dict(m), "row": 1, "col": 1, "symbol": C.X},
    )
    assert resp.status_code == 400
