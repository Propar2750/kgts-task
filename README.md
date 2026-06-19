# Order & Chaos

A playable 6×6 game of **Order and Chaos** (KGTS Tech Task 3): a Python game engine +
two-round match layer behind a **FastAPI** backend, with an interactive **React + TypeScript**
frontend. You play a full two-round match against a bot — you are **Order** in round 1 and
**Chaos** in round 2 — and the app resolves the overall winner via the rulebook's tiebreaker.

> The bot is currently a **placeholder that plays random legal moves**. The real minimax +
> alpha-beta AI is a later task and drops into `order_chaos/bot.choose_move` with no other
> changes.

## Rules

- 6×6 grid; each turn a player places **either an `X` or an `O`** in any empty cell (the
  symbol choice is independent of whose turn it is — that's the core mechanic).
- **Order** wins a round by making a **straight-5** (5 identical symbols in a row, column,
  or diagonal). **Chaos** wins if the board fills with no straight-5.
- **Two rounds**, roles swapped: P1 = Order then Chaos; P2 = Chaos then Order.
- **Overall winner** (tiebreaker):
  - If round-1 Order made a 5: round-2 Order must make a 5 in **fewer Order-moves** to win;
    tie on moves → more **straight-4s** wins; still tied → draw. If round-2 Order makes no 5,
    round-1 Order wins.
  - If round-1 Order made no 5: round-2 Order wins by making any 5; otherwise more
    straight-4s wins, tie → draw.

## Architecture

```
order_chaos/        # pure Python game logic
  constants.py      # sizes, symbols, Player/Status enums
  board.py          # pure 6x6 grid helpers
  patterns.py       # straight-5 / straight-4 detection
  game.py           # single-round GameState + apply_move + serialization
  match.py          # two-round match: role swap, transitions, tiebreaker
  bot.py            # placeholder random opponent (swappable for minimax)
api/
  main.py           # FastAPI: POST /api/match/new, POST /api/match/move
frontend/           # Vite + React + TypeScript + Tailwind UI
tests/              # pytest suite (engine, match, bot, api)
```

The API is **stateless**: the frontend holds the serialized match state and sends it with
each move; the backend validates, applies your move, lets the bot reply (which also drives
the round-1→2 transition and the bot opening round 2 as Order), and returns the new state.

## Running locally

**Backend** (Python 3.9+):

```bash
pip install -e ".[test]"
uvicorn api.main:app --reload --port 8000
```

**Frontend** (Node 18+):

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173, talks to the API on :8000
```

Override the API URL with `VITE_API_URL` if the backend runs elsewhere.

## Tests

```bash
pytest                 # backend: engine + match + bot + api
cd frontend && npm test  # frontend smoke tests (Vitest + Testing Library)
```

## Public Python API

Engine: `new_game`, `apply_move`, `legal_moves`, `is_legal`, `to_dict`, `from_dict`,
`GameState`, `Move`, `Player`, `Status`, `InvalidMoveError`.
Match: `order_chaos.match.new_match`, `apply_match_move`, `resolve_match`,
`current_player_id`, `MatchState`, `RoundResult`, `MatchStatus`, `to_dict`/`from_dict`.

## Not yet implemented

The real minimax + alpha-beta AI (replaces the random bot) and production deployment.
