# Order & Chaos — Game Engine

Pure Python game engine for the 6×6 game of **Order and Chaos** (KGTS Tech Task 3).

This is the **engine only** — the game mechanics, state, and helpers that play and
store a single round. No UI and no AI yet; both are designed to attach on top of
this engine later (a React frontend talking to a Python backend, plus a minimax bot).

## Rules (single round)

- 6×6 grid; each cell is empty, `X`, or `O`.
- **Order** moves first, then players alternate.
- On a turn, a player places **either an `X` or an `O`** in any empty cell — the
  choice of symbol is independent of whose turn it is.
- **Order wins** the moment a **straight-5** appears (5 identical symbols in a row,
  column, or diagonal), regardless of who placed the fifth stone.
- **Chaos wins** if the board fills with no straight-5.

## Layout

```
order_chaos/
  constants.py   # board size, win length, symbols, Player/Status enums
  board.py       # pure 6x6 grid helpers
  patterns.py    # straight-5 / straight-4 detection
  game.py        # GameState, Move, apply_move, legal_moves, serialization
tests/           # pytest suite
```

## Usage

```python
from order_chaos import new_game, apply_move, Status

game = new_game()                 # empty board, Order to move
game = apply_move(game, 0, 0, "X")  # place X at row 0, col 0
print(game.current_player)        # Player.CHAOS
print(game.status)                # Status.IN_PROGRESS
```

The state is immutable: `apply_move` returns a **new** `GameState` and never
mutates the one passed in. Illegal moves raise `InvalidMoveError`.

### Storing game state

```python
from order_chaos import to_dict, from_dict
import json

blob = json.dumps(to_dict(game))   # JSON-serializable snapshot
game = from_dict(json.loads(blob)) # restored, equal to the original
```

## Running the tests

```bash
pip install -e ".[test]"   # or: pip install pytest
pytest
```

## Public API

`new_game`, `apply_move`, `legal_moves`, `is_legal`, `to_dict`, `from_dict`,
`GameState`, `Move`, `Player`, `Status`, `InvalidMoveError`.

## Not yet implemented (next steps)

- Interactive React UI for the board.
- AI opponent (minimax + alpha-beta pruning) — `legal_moves` and the cheap
  immutable `apply_move` are designed for exactly this search.
- Two-round match layer: role swap, board reset, and the move-count /
  straight-4 tiebreaker that decides the overall winner.
