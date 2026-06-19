"""The Order & Chaos game engine (single round).

State is held in an immutable-style ``GameState``. ``apply_move`` returns a NEW
state rather than mutating, which keeps the engine safe for a future minimax
search (no undo bookkeeping) and trivial to test. State is plain data and
serializes to/from JSON-friendly dicts via ``to_dict`` / ``from_dict``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .constants import EMPTY, SYMBOLS, Player, Status
from . import board as B
from .patterns import find_straight_five


class InvalidMoveError(Exception):
    """Raised when an illegal move is applied to a game state."""


@dataclass(frozen=True)
class Move:
    """A single placement: the cell, the symbol placed, and who placed it.

    ``symbol`` is independent of ``player`` — in Order and Chaos either player
    may place either an X or an O on their turn.
    """

    row: int
    col: int
    symbol: str
    player: Player


@dataclass(frozen=True)
class GameState:
    """Immutable snapshot of a single round.

    Build the next state with :func:`apply_move`; never mutate in place.
    """

    board: list
    current_player: Player
    status: Status
    winning_line: Optional[list] = None
    order_moves: int = 0
    move_history: tuple = ()


def new_game() -> GameState:
    """Return the starting state: empty board, Order to move."""
    return GameState(
        board=B.new_board(),
        current_player=Player.ORDER,
        status=Status.IN_PROGRESS,
        winning_line=None,
        order_moves=0,
        move_history=(),
    )


def is_legal(state: GameState, row: int, col: int, symbol: str) -> bool:
    """True if placing ``symbol`` at (row, col) is a legal move right now."""
    return (
        state.status == Status.IN_PROGRESS
        and symbol in SYMBOLS
        and B.in_bounds(row, col)
        and B.is_empty(state.board, row, col)
    )


def legal_moves(state: GameState) -> list[Move]:
    """All legal moves: every empty cell paired with each symbol.

    Empty when the round is over. Useful for the (future) AI's move generation.
    """
    if state.status != Status.IN_PROGRESS:
        return []
    return [
        Move(r, c, symbol, state.current_player)
        for (r, c) in B.empty_cells(state.board)
        for symbol in SYMBOLS
    ]


def apply_move(state: GameState, row: int, col: int, symbol: str) -> GameState:
    """Apply a move and return the resulting NEW state.

    Raises :class:`InvalidMoveError` if the move is illegal. After placing the
    symbol the round is resolved: a straight-5 anywhere on the board is an
    immediate win for Order (regardless of who placed the fifth stone); a full
    board with no straight-5 is a win for Chaos; otherwise play continues with
    the turn passing to the other player.
    """
    if not is_legal(state, row, col, symbol):
        raise InvalidMoveError(
            f"Illegal move: symbol={symbol!r} at ({row}, {col}) "
            f"(status={state.status.value})"
        )

    mover = state.current_player
    new_board = B.place(state.board, row, col, symbol)
    history = state.move_history + (Move(row, col, symbol, mover),)
    order_moves = state.order_moves + (1 if mover == Player.ORDER else 0)

    winning_line = find_straight_five(new_board)
    if winning_line is not None:
        status = Status.ORDER_WIN
    elif B.is_full(new_board):
        status = Status.CHAOS_WIN
    else:
        status = Status.IN_PROGRESS

    next_player = Player.CHAOS if mover == Player.ORDER else Player.ORDER

    return GameState(
        board=new_board,
        current_player=next_player,
        status=status,
        winning_line=winning_line,
        order_moves=order_moves,
        move_history=history,
    )


# --- Serialization -------------------------------------------------------

def to_dict(state: GameState) -> dict:
    """Convert a state to a JSON-serializable dict."""
    return {
        "board": [row[:] for row in state.board],
        "current_player": state.current_player.value,
        "status": state.status.value,
        "winning_line": (
            [[r, c] for (r, c) in state.winning_line]
            if state.winning_line is not None
            else None
        ),
        "order_moves": state.order_moves,
        "move_history": [
            {
                "row": m.row,
                "col": m.col,
                "symbol": m.symbol,
                "player": m.player.value,
            }
            for m in state.move_history
        ],
    }


def from_dict(data: dict) -> GameState:
    """Rebuild a state from a dict produced by :func:`to_dict`."""
    winning_line = data["winning_line"]
    return GameState(
        board=[list(row) for row in data["board"]],
        current_player=Player(data["current_player"]),
        status=Status(data["status"]),
        winning_line=(
            [tuple(cell) for cell in winning_line]
            if winning_line is not None
            else None
        ),
        order_moves=data["order_moves"],
        move_history=tuple(
            Move(m["row"], m["col"], m["symbol"], Player(m["player"]))
            for m in data["move_history"]
        ),
    )
