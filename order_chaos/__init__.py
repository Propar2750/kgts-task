"""Order & Chaos game engine (single-round).

Pure, framework-agnostic game mechanics for the 6x6 Order and Chaos game.
No UI, no AI — just the rules, state, and serialization helpers.
"""

from .constants import (
    BOARD_SIZE,
    WIN_LENGTH,
    FOUR_LENGTH,
    X,
    O,
    EMPTY,
    Player,
    Status,
)
from .game import (
    GameState,
    Move,
    InvalidMoveError,
    new_game,
    apply_move,
    legal_moves,
    is_legal,
    to_dict,
    from_dict,
)

__all__ = [
    "BOARD_SIZE",
    "WIN_LENGTH",
    "FOUR_LENGTH",
    "X",
    "O",
    "EMPTY",
    "Player",
    "Status",
    "GameState",
    "Move",
    "InvalidMoveError",
    "new_game",
    "apply_move",
    "legal_moves",
    "is_legal",
    "to_dict",
    "from_dict",
]
