"""Shared constants and enums for the Order & Chaos engine."""

from enum import Enum

# Board geometry
BOARD_SIZE = 6
WIN_LENGTH = 5  # straight-5 wins the round for Order
FOUR_LENGTH = 4  # straight-4, used by the (future) two-round tiebreaker

# Cell symbols. Kept as plain strings / None so a board is directly JSON-serializable.
X = "X"
O = "O"
EMPTY = None

SYMBOLS = (X, O)


class Player(Enum):
    """Whose turn it is. Independent of which symbol they place."""

    ORDER = "ORDER"
    CHAOS = "CHAOS"


class Status(Enum):
    """Outcome state of a single round."""

    IN_PROGRESS = "IN_PROGRESS"
    ORDER_WIN = "ORDER_WIN"
    CHAOS_WIN = "CHAOS_WIN"
