"""Two-round match layer for Order & Chaos.

Wraps the single-round engine (:mod:`order_chaos.game`) with the full match:
two rounds with swapped roles, and the tiebreaker that decides the overall
winner. Player 1 is Order in round 1 and Chaos in round 2; Player 2 is the
reverse.

Like the engine, this is immutable-style and JSON-serializable: ``apply_match_move``
returns a NEW :class:`MatchState`.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Optional

from .constants import Player, Status
from .patterns import count_straight_fours
from . import game as G
from .game import GameState, InvalidMoveError


class MatchStatus(Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"


@dataclass(frozen=True)
class RoundResult:
    """Summary of one completed round, used for the tiebreaker and the UI."""

    round: int
    order_player: str  # "P1" or "P2"
    order_achieved_five: bool
    order_moves: int  # the Order player's own placements
    straight_fours: int = 0
    round_winner_role: Optional[Player] = None
    final_board: Optional[list] = None


@dataclass(frozen=True)
class MatchState:
    """Immutable snapshot of a two-round match."""

    current_round: int
    round: GameState
    round_results: tuple = ()
    status: MatchStatus = MatchStatus.IN_PROGRESS
    overall_winner: Optional[str] = None  # "P1" | "P2" | "DRAW"
    winner_reason: Optional[str] = None


# --- role mapping ----------------------------------------------------------

def order_player_for_round(round_num: int) -> str:
    """Which physical player is Order in the given round."""
    return "P1" if round_num == 1 else "P2"


def player_id_for_role(round_num: int, role: Player) -> str:
    """Map a role (ORDER/CHAOS) to the physical player ("P1"/"P2") this round."""
    order_player = order_player_for_round(round_num)
    chaos_player = "P2" if order_player == "P1" else "P1"
    return order_player if role == Player.ORDER else chaos_player


def role_of_player(round_num: int, player_id: str) -> Player:
    """Map a physical player to their role (ORDER/CHAOS) this round."""
    return Player.ORDER if order_player_for_round(round_num) == player_id else Player.CHAOS


def current_player_id(state: MatchState) -> Optional[str]:
    """Whose physical turn it is ("P1"/"P2"), or None if the match is over."""
    if state.status != MatchStatus.IN_PROGRESS:
        return None
    return player_id_for_role(state.current_round, state.round.current_player)


# --- match flow ------------------------------------------------------------

def new_match() -> MatchState:
    """Start a fresh match: round 1, empty board, Order (P1) to move."""
    return MatchState(current_round=1, round=G.new_game())


def _summarize_round(round_num: int, finished: GameState) -> RoundResult:
    achieved_five = finished.status == Status.ORDER_WIN
    return RoundResult(
        round=round_num,
        order_player=order_player_for_round(round_num),
        order_achieved_five=achieved_five,
        order_moves=finished.order_moves,
        straight_fours=count_straight_fours(finished.board),
        round_winner_role=Player.ORDER if achieved_five else Player.CHAOS,
        final_board=[row[:] for row in finished.board],
    )


def apply_match_move(state: MatchState, row: int, col: int, symbol: str) -> MatchState:
    """Apply one move to the current round and advance the match as needed.

    Raises :class:`InvalidMoveError` if the match is already complete or the
    move is illegal in the current round.
    """
    if state.status != MatchStatus.IN_PROGRESS:
        raise InvalidMoveError("Match is already complete.")

    new_round = G.apply_move(state.round, row, col, symbol)

    if new_round.status == Status.IN_PROGRESS:
        # round continues
        return replace(state, round=new_round)

    # round just ended — record it
    result = _summarize_round(state.current_round, new_round)
    results = state.round_results + (result,)

    if state.current_round == 1:
        # advance to round 2: reset board, roles swap (P2 is now Order, moves first)
        return MatchState(current_round=2, round=G.new_game(), round_results=results)

    # round 2 ended — resolve the match, keep the final board on display
    winner, reason = resolve_match(results[0], results[1])
    return MatchState(
        current_round=2,
        round=new_round,
        round_results=results,
        status=MatchStatus.COMPLETE,
        overall_winner=winner,
        winner_reason=reason,
    )


# --- tiebreaker ------------------------------------------------------------

def _compare_fours(r1: RoundResult, r2: RoundResult) -> tuple:
    """Tiebreak by straight-4 count. Returns (winner, reason)."""
    if r2.straight_fours > r1.straight_fours:
        return "P2", f"P2 created more straight-4s ({r2.straight_fours} vs {r1.straight_fours})."
    if r1.straight_fours > r2.straight_fours:
        return "P1", f"P1 created more straight-4s ({r1.straight_fours} vs {r2.straight_fours})."
    return "DRAW", f"Equal straight-4s ({r1.straight_fours} each) — it's a draw."


def resolve_match(r1: RoundResult, r2: RoundResult) -> tuple:
    """Decide the overall winner from the two round results.

    ``r1`` is round 1 (P1 played Order); ``r2`` is round 2 (P2 played Order).
    Returns ``(winner, reason)`` where winner is "P1" | "P2" | "DRAW".
    """
    if r1.order_achieved_five:
        # Case 1: P1's Order made a five in round 1.
        if r2.order_achieved_five:
            if r2.order_moves < r1.order_moves:
                return "P2", (
                    f"Both made a straight-5; P2 did it in fewer moves "
                    f"({r2.order_moves} vs {r1.order_moves})."
                )
            if r2.order_moves > r1.order_moves:
                return "P1", (
                    f"Both made a straight-5; P1 did it in fewer moves "
                    f"({r1.order_moves} vs {r2.order_moves})."
                )
            return _compare_fours(r1, r2)
        # P2 failed to make a five; P1 achieved the goal.
        return "P1", "P1 made a straight-5 as Order; P2 did not."

    # Case 2: P1's Order did NOT make a five (Chaos won round 1).
    if r2.order_achieved_five:
        return "P2", "P2 made a straight-5 as Order; P1 did not."
    return _compare_fours(r1, r2)


# --- serialization ---------------------------------------------------------

def _round_result_to_dict(r: RoundResult) -> dict:
    return {
        "round": r.round,
        "order_player": r.order_player,
        "order_achieved_five": r.order_achieved_five,
        "order_moves": r.order_moves,
        "straight_fours": r.straight_fours,
        "round_winner_role": r.round_winner_role.value if r.round_winner_role else None,
        "final_board": [row[:] for row in r.final_board] if r.final_board else None,
    }


def _round_result_from_dict(d: dict) -> RoundResult:
    role = d.get("round_winner_role")
    board = d.get("final_board")
    return RoundResult(
        round=d["round"],
        order_player=d["order_player"],
        order_achieved_five=d["order_achieved_five"],
        order_moves=d["order_moves"],
        straight_fours=d.get("straight_fours", 0),
        round_winner_role=Player(role) if role else None,
        final_board=[list(row) for row in board] if board else None,
    )


def to_dict(state: MatchState) -> dict:
    """Convert a match state to a JSON-serializable dict."""
    return {
        "current_round": state.current_round,
        "round": G.to_dict(state.round),
        "round_results": [_round_result_to_dict(r) for r in state.round_results],
        "status": state.status.value,
        "overall_winner": state.overall_winner,
        "winner_reason": state.winner_reason,
        # convenience fields for the UI (derived; ignored on the way back in)
        "current_player_id": current_player_id(state),
        "human_role": role_of_player(state.current_round, "P1").value,
    }


def from_dict(data: dict) -> MatchState:
    """Rebuild a match state from a dict produced by :func:`to_dict`."""
    return MatchState(
        current_round=data["current_round"],
        round=G.from_dict(data["round"]),
        round_results=tuple(
            _round_result_from_dict(r) for r in data["round_results"]
        ),
        status=MatchStatus(data["status"]),
        overall_winner=data["overall_winner"],
        winner_reason=data["winner_reason"],
    )
