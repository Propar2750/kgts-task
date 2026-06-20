import { useEffect, useState } from "react";
import type { CSSProperties } from "react";
import type { Difficulty, MatchState, RoundResult, Symbol } from "./types";
import { newMatch, makeMove } from "./api";
import Board from "./components/Board";
import StatusPanel from "./components/StatusPanel";
import DifficultySelector from "./components/DifficultySelector";
import RoundTransition from "./components/RoundTransition";
import MatchResult from "./components/MatchResult";

const ORDER_ACCENT = "#2fe0ea";
const CHAOS_ACCENT = "#ff4d8d";

export default function App() {
  const [match, setMatch] = useState<MatchState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pendingCell, setPendingCell] = useState<{ row: number; col: number } | null>(null);
  const [transition, setTransition] = useState<RoundResult | null>(null);
  const [difficulty, setDifficulty] = useState<Difficulty>("medium");

  async function startMatch() {
    setLoading(true);
    setError(null);
    setPendingCell(null);
    setTransition(null);
    try {
      setMatch(await newMatch());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't reach the server");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void startMatch();
  }, []);

  async function handlePick(symbol: Symbol) {
    if (!match || !pendingCell) return;
    const { row, col } = pendingCell;
    const prevResults = match.round_results.length;
    setPendingCell(null);
    setLoading(true);
    try {
      const { state } = await makeMove(match, row, col, symbol, difficulty);
      if (state.status === "IN_PROGRESS" && state.round_results.length > prevResults) {
        setTransition(state.round_results[state.round_results.length - 1]);
      }
      setMatch(state);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "That move didn't take");
    } finally {
      setLoading(false);
    }
  }

  const accent = match?.human_role === "CHAOS" ? CHAOS_ACCENT : ORDER_ACCENT;
  const interactive =
    !!match &&
    match.status === "IN_PROGRESS" &&
    match.current_player_id === "P1" &&
    !loading &&
    !transition;

  return (
    <div
      className="atmosphere relative min-h-full overflow-hidden px-4 py-8 sm:py-12"
      style={{ "--accent": accent } as CSSProperties}
    >
      <div className="relative z-10 mx-auto max-w-4xl">
        <header className="mb-8 text-center">
          <p className="font-mono text-[11px] uppercase tracking-[0.3em] text-muted">
            Five in a row — or none at all
          </p>
          <h1 className="mt-2 font-display text-5xl font-bold tracking-tight sm:text-6xl">
            <span className="text-order">Order</span>
            <span className="text-muted"> &amp; </span>
            <span className="text-chaos">Chaos</span>
          </h1>
        </header>

        {error && (
          <div className="mx-auto mb-5 max-w-md rounded-lg bg-chaos/15 px-4 py-2 text-center text-sm text-chaos ring-1 ring-chaos/30">
            {error}
          </div>
        )}

        {!match ? (
          <p className="text-center font-mono text-sm text-muted">
            {loading ? "Setting up the board…" : "No game."}
          </p>
        ) : (
          <div className="flex flex-col items-center gap-6 md:flex-row md:items-start md:justify-center">
            <div className="w-full max-w-md">
              <Board
                round={match.round}
                isInteractive={interactive}
                pendingCell={pendingCell}
                onCellClick={(row, col) => setPendingCell({ row, col })}
                onPick={handlePick}
                onCancelPicker={() => setPendingCell(null)}
              />
            </div>
            <div className="w-full max-w-xs space-y-4">
              <StatusPanel match={match} />
              <DifficultySelector value={difficulty} onChange={setDifficulty} />
            </div>
          </div>
        )}
      </div>

      {transition && match && (
        <RoundTransition
          result={transition}
          nextHumanRole={match.human_role}
          onContinue={() => setTransition(null)}
        />
      )}

      {match && match.status === "COMPLETE" && (
        <MatchResult match={match} onPlayAgain={startMatch} />
      )}
    </div>
  );
}
