"""Placeholder opponent for Order & Chaos.

``choose_move`` plays a random legal move. It is intentionally trivial — a
stand-in until the real minimax + alpha-beta AI is built. That AI will implement
the SAME signature, so it drops in here with no change to the API or match layer.
"""

from __future__ import annotations

import random

from .constants import Player
from .game import GameState, Move, legal_moves


def choose_move(state: GameState, role: Player, rng: random.Random | None = None) -> Move:
    """Return a move for the player whose turn it is.

    ``role`` is the role (ORDER/CHAOS) the bot is playing; the random bot ignores
    it, but the real AI will use it to pick a strategy. Pass ``rng`` to make the
    choice deterministic in tests.
    """
    moves = legal_moves(state)
    if not moves:
        raise ValueError("No legal moves available.")
    picker = rng or random
    return picker.choice(moves)
