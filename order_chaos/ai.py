"""Minimax + alpha-beta AI for Order & Chaos.

The game's value is intrinsic to *whose turn it is*: the Order player always wants
to maximize line potential, the Chaos player always wants to minimize it. So the
search treats Order-to-move nodes as MAX and Chaos-to-move nodes as MIN over a
single evaluation function, and ``choose_move`` returns the best move for
``state.current_player`` — which handles the bot being Chaos in round 1 and Order
in round 2 with no special-casing.

Performance (the 6x6 branching factor is large — up to ~72 moves at the root):
the search runs on a flat, mutable board with make/undo and **incremental
evaluation** (placing a stone only touches the few length-5 windows through that
cell), plus alpha-beta pruning, move ordering, neighborhood pruning (only cells
adjacent to an existing stone), and **top-K** move pruning per node.
"""

from __future__ import annotations

import math
import random
from typing import Optional

from .constants import BOARD_SIZE, WIN_LENGTH, X, O, Player, Status
from .game import GameState, Move, legal_moves
from .patterns import line_windows

# A terminal win dominates any heuristic score.
WIN_SCORE = 10 ** 9

# Window score by how many stones of one symbol it holds (index = count, 0..5).
_SCORE = [0, 1, 10, 100, 1000, WIN_SCORE]

# Opening move (the empty board is symmetric, so play the centre).
CENTER = (BOARD_SIZE // 2, BOARD_SIZE // 2)

# Difficulty -> search depth (plies). Easy also mixes in randomness.
DIFFICULTY_DEPTH = {"easy": 2, "medium": 3, "hard": 4}
EASY_RANDOM_PROB = 0.3

# Per-node branching cap. Generous enough to keep tactical moves, small enough
# to stay responsive at depth 4.
TOP_K = 16

_N = BOARD_SIZE
_NCELLS = _N * _N

# --- precomputed window geometry (flat indices) ---------------------------

def _build_windows():
    windows = []
    cell_windows = [[] for _ in range(_NCELLS)]
    for cells in line_windows([[None] * _N for _ in range(_N)], WIN_LENGTH):
        w = tuple(r * _N + c for (r, c) in cells)
        wi = len(windows)
        windows.append(w)
        for idx in w:
            cell_windows[idx].append(wi)
    return windows, cell_windows


_WINDOWS, _CELL_WINDOWS = _build_windows()


def _contrib(xc: int, oc: int) -> int:
    """Score contribution of one window from its X/O counts (Order's view)."""
    if xc and oc:
        return 0  # blocked window: useless to Order, exactly what Chaos wants
    return _SCORE[xc] if xc else _SCORE[oc]


# --- public board evaluation (used by tests / for clarity) -----------------

def evaluate(board) -> int:
    """Heuristic score of a (non-terminal) board, from Order's perspective."""
    score = 0
    for cells in line_windows(board, WIN_LENGTH):
        xs = os = 0
        for (r, c) in cells:
            v = board[r][c]
            if v == X:
                xs += 1
            elif v == O:
                os += 1
        score += _contrib(xs, os)
    return score


# --- fast searcher (flat mutable board, make/undo, incremental eval) -------

class _Searcher:
    def __init__(self, board, rng, k: int = TOP_K):
        self.rng = rng
        self.k = k
        self.cell = [0] * _NCELLS  # 0 empty, 1 X, 2 O
        self.win_x = [0] * len(_WINDOWS)
        self.win_o = [0] * len(_WINDOWS)
        self.total = 0
        self.empty = 0
        for r in range(_N):
            for c in range(_N):
                v = board[r][c]
                i = r * _N + c
                if v == X:
                    self.cell[i] = 1
                elif v == O:
                    self.cell[i] = 2
                else:
                    self.empty += 1
        # initialise window counts + total from the starting position
        for wi, w in enumerate(_WINDOWS):
            xc = oc = 0
            for idx in w:
                if self.cell[idx] == 1:
                    xc += 1
                elif self.cell[idx] == 2:
                    oc += 1
            self.win_x[wi] = xc
            self.win_o[wi] = oc
            self.total += _contrib(xc, oc)

    def _place(self, i: int, val: int) -> bool:
        """Place; return True if this creates a straight-5 (an Order win)."""
        self.cell[i] = val
        self.empty -= 1
        five = False
        for w in _CELL_WINDOWS[i]:
            xc, oc = self.win_x[w], self.win_o[w]
            old = _contrib(xc, oc)
            if val == 1:
                xc += 1
                self.win_x[w] = xc
            else:
                oc += 1
                self.win_o[w] = oc
            self.total += _contrib(xc, oc) - old
            if xc == WIN_LENGTH or oc == WIN_LENGTH:
                five = True
        return five

    def _undo(self, i: int, val: int) -> None:
        self.cell[i] = 0
        self.empty += 1
        for w in _CELL_WINDOWS[i]:
            xc, oc = self.win_x[w], self.win_o[w]
            old = _contrib(xc, oc)
            if val == 1:
                xc -= 1
                self.win_x[w] = xc
            else:
                oc -= 1
                self.win_o[w] = oc
            self.total += _contrib(xc, oc) - old

    def _move_delta(self, i: int, val: int) -> int:
        """Change in total if ``val`` were placed at ``i`` (no commit)."""
        d = 0
        for w in _CELL_WINDOWS[i]:
            xc, oc = self.win_x[w], self.win_o[w]
            old = _contrib(xc, oc)
            new = _contrib(xc + 1, oc) if val == 1 else _contrib(xc, oc + 1)
            d += new - old
        return d

    def _scored_moves(self, maximizing: bool):
        """Top-K (delta, cell, val) candidate moves, best-first for the mover."""
        moves = []
        for i in range(_NCELLS):
            if self.cell[i] != 0:
                continue
            r, c = divmod(i, _N)
            adjacent = False
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < _N and 0 <= cc < _N and self.cell[rr * _N + cc]:
                        adjacent = True
                        break
                if adjacent:
                    break
            if not adjacent:
                continue
            moves.append((self._move_delta(i, 1), i, 1))
            moves.append((self._move_delta(i, 2), i, 2))
        moves.sort(key=lambda t: t[0], reverse=maximizing)
        return moves[: self.k]

    def _value_after(self, i: int, val: int, depth: int, alpha: float,
                     beta: float, maximizing: bool) -> float:
        five = self._place(i, val)
        if five:
            v: float = WIN_SCORE + depth  # straight-5 = Order win (any mover)
        elif self.empty == 0:
            v = -(WIN_SCORE + depth)  # full board, no five = Chaos win
        elif depth == 1:
            v = self.total
        else:
            v = self._search(depth - 1, alpha, beta, not maximizing)
        self._undo(i, val)
        return v

    def _search(self, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        moves = self._scored_moves(maximizing)
        if not moves:
            return self.total
        if maximizing:
            value = -math.inf
            for _, i, val in moves:
                value = max(value, self._value_after(i, val, depth, alpha, beta, True))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        value = math.inf
        for _, i, val in moves:
            value = min(value, self._value_after(i, val, depth, alpha, beta, False))
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value

    def root(self, depth: int, maximizing: bool):
        """Return a strongest (cell, val), ties broken randomly."""
        moves = self._scored_moves(maximizing)
        best_val = -math.inf if maximizing else math.inf
        best = []
        for _, i, val in moves:
            v = self._value_after(i, val, depth, -math.inf, math.inf, maximizing)
            if v == best_val:
                best.append((i, val))
            elif (v > best_val) if maximizing else (v < best_val):
                best_val = v
                best = [(i, val)]
        return self.rng.choice(best)


# --- public move selection -------------------------------------------------

def _is_empty_board(board) -> bool:
    return all(cell is None for row in board for cell in row)


def best_move(state: GameState, depth: int, rng: Optional[random.Random] = None) -> Move:
    """Search ``depth`` plies and return a strongest move (ties broken randomly)."""
    picker = rng or random
    if _is_empty_board(state.board):
        return Move(CENTER[0], CENTER[1], X, state.current_player)
    searcher = _Searcher(state.board, picker)
    i, val = searcher.root(depth, state.current_player == Player.ORDER)
    r, c = divmod(i, _N)
    return Move(r, c, X if val == 1 else O, state.current_player)


def choose_move(
    state: GameState,
    difficulty: str = "medium",
    rng: Optional[random.Random] = None,
) -> Move:
    """Pick a move for the current player at the given difficulty.

    Easy plays a random legal move ~30% of the time, otherwise searches
    ``DIFFICULTY_DEPTH[difficulty]`` plies. Medium/Hard always search.
    """
    if difficulty not in DIFFICULTY_DEPTH:
        raise ValueError(f"Unknown difficulty: {difficulty!r}")
    picker = rng or random
    if difficulty == "easy" and picker.random() < EASY_RANDOM_PROB:
        return picker.choice(legal_moves(state))
    return best_move(state, DIFFICULTY_DEPTH[difficulty], picker)
