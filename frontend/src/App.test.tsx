import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import App from "./App";
import type { MatchState } from "./types";

const freshMatch: MatchState = {
  current_round: 1,
  round: {
    board: Array.from({ length: 6 }, () => Array(6).fill(null)),
    current_player: "ORDER",
    status: "IN_PROGRESS",
    winning_line: null,
    order_moves: 0,
    move_history: [],
  },
  round_results: [],
  status: "IN_PROGRESS",
  overall_winner: null,
  winner_reason: null,
  current_player_id: "P1",
  human_role: "ORDER",
};

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => ({
      ok: true,
      json: async () => freshMatch,
    })),
  );
});

afterEach(() => {
  vi.unstubAllGlobals();
});

test("renders a 6x6 board (36 cells) after loading a match", async () => {
  render(<App />);
  await waitFor(() => {
    expect(screen.getAllByTestId("cell")).toHaveLength(36);
  });
});

test("clicking an empty cell opens the X/O picker", async () => {
  render(<App />);
  const cells = await screen.findAllByTestId("cell");
  fireEvent.click(cells[0]);
  expect(screen.getByLabelText("Place X")).toBeInTheDocument();
  expect(screen.getByLabelText("Place O")).toBeInTheDocument();
});
