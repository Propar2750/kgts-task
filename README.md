# Order & Chaos

A playable 6×6 game of **Order and Chaos** (KGTS Tech Task 3): a Python game engine +
two-round match layer behind a **FastAPI** backend, with an interactive **React + TypeScript**
frontend. You play a full two-round match against a **minimax AI** — you are **Order** in
round 1 and **Chaos** in round 2 — and the app resolves the overall winner via the rulebook's
tiebreaker.

**Live demo:** _<paste your deployed URL here after deploying — see Deployment below>_

## The AI (`order_chaos/ai.py`)

A **minimax search with alpha-beta pruning**. The game's value is intrinsic to whose turn it
is — Order maximizes line potential, Chaos minimizes it — so the search treats Order-to-move
nodes as MAX and Chaos-to-move nodes as MIN over one heuristic, and naturally handles the bot
being Chaos in round 1 and Order in round 2.

- **Heuristic:** every length-5 window that mixes X and O is dead (0); a single-symbol window
  scores by how close it is to five (`10^k`). Order's win = +∞, Chaos's = −∞ (depth-adjusted
  to prefer faster wins).
- **Speed:** a flat mutable board with make/undo + **incremental evaluation** (a placement
  only touches the few windows through that cell), alpha-beta, move ordering, neighborhood
  pruning, and top-K per-node pruning. Hard (depth 4) runs in well under 100 ms per move.
- **Difficulty** (set in the UI) maps to search depth: **Easy = 2** plies (plus ~30% random
  moves), **Medium = 3**, **Hard = 4**.

> `order_chaos/bot.py` keeps a trivial random-move opponent as a baseline; the API uses the
> minimax AI.

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
  ai.py             # minimax + alpha-beta opponent (Easy/Medium/Hard depths)
  bot.py            # trivial random opponent (baseline)
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

## Deployment

The app ships as a **single Docker service**: the Dockerfile builds the React app and the
FastAPI server serves both the static UI and the `/api` routes from one origin (no CORS or
cross-service URL wiring). The production build calls the API at the same origin
(`src/api.ts`), and `STATIC_DIR` points the server at the built assets.

**Deploy to Render (free, one service):**

1. Push this repo to GitHub (already done).
2. In Render: **New → Blueprint**, connect this repo. Render reads `render.yaml` and builds
   the `Dockerfile`.
3. When the build finishes you get a URL like `https://order-and-chaos.onrender.com`.
4. Paste that URL into the **Live demo** line near the top of this README and commit.

> The free plan sleeps on inactivity, so the first request after idle can take ~30–50 s
> (cold start). Any Docker host works the same way (Railway, Fly.io, etc.).

**Run the Docker image locally** (optional sanity check):

```bash
docker build -t order-chaos . && docker run -p 8000:8000 order-chaos
# open http://localhost:8000
```

**Split hosting instead?** Set `VITE_API_URL` at build time to point the frontend (e.g. on
Vercel/Netlify) at a separately hosted backend; CORS is already open.
