"""FastAPI app exposing the Order & Chaos two-round match.

Stateless: the client holds the serialized match state and sends it with each
move. The server validates, applies the human's move, lets the bot reply (which
also drives the round-1 -> round-2 transition and the bot opening round 2 as
Order), and returns the new state. No session store / database.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from order_chaos.game import InvalidMoveError
from order_chaos import match as M
from order_chaos import ai

HUMAN = "P1"  # the human is always Player 1

app = FastAPI(title="Order & Chaos API")

# Allow the Vite dev server (and any local origin) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class MoveRequest(BaseModel):
    state: dict
    row: int
    col: int
    symbol: str
    difficulty: str = "medium"


@app.post("/api/match/new")
def new_match() -> dict:
    """Start a fresh match (round 1, human is Order, human to move)."""
    return M.to_dict(M.new_match())


@app.post("/api/match/move")
def make_move(req: MoveRequest) -> dict[str, Any]:
    """Apply the human's move, then let the bot respond, and return the new state."""
    try:
        state = M.from_dict(req.state)
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Malformed state: {exc}")

    if req.difficulty not in ai.DIFFICULTY_DEPTH:
        raise HTTPException(
            status_code=400, detail=f"Unknown difficulty: {req.difficulty!r}"
        )
    if state.status != M.MatchStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Match is already complete.")
    if M.current_player_id(state) != HUMAN:
        raise HTTPException(status_code=400, detail="It is not your turn.")

    # 1) the human's move
    try:
        state = M.apply_match_move(state, req.row, req.col, req.symbol)
    except InvalidMoveError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # 2) let the bot play until it is the human's turn again (or the match ends).
    #    This also covers the round-1 -> round-2 transition and the bot opening
    #    round 2 as Order.
    bot_moves: list[dict] = []
    while (
        state.status == M.MatchStatus.IN_PROGRESS
        and M.current_player_id(state) != HUMAN
    ):
        move = ai.choose_move(state.round, req.difficulty)
        state = M.apply_match_move(state, move.row, move.col, move.symbol)
        bot_moves.append({"row": move.row, "col": move.col, "symbol": move.symbol})

    return {"state": M.to_dict(state), "bot_moves": bot_moves}
