// Typed fetch client for the Order & Chaos backend.

import type { MatchState, MoveResponse, Symbol } from "./types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      if (data?.detail) detail = data.detail;
    } catch {
      // ignore non-JSON error bodies
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export function newMatch(): Promise<MatchState> {
  return postJson<MatchState>("/api/match/new", {});
}

export function makeMove(
  state: MatchState,
  row: number,
  col: number,
  symbol: Symbol,
): Promise<MoveResponse> {
  return postJson<MoveResponse>("/api/match/move", { state, row, col, symbol });
}
