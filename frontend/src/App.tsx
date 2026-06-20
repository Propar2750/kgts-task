import { useEffect, useState } from "react";
import type { Difficulty, MatchState, RoundResult, Symbol } from "./types";
import { newMatch, makeMove } from "./api";
import Board from "./components/Board";
import StatusPanel from "./components/StatusPanel";
import DifficultySelector from "./components/DifficultySelector";
import RoundTransition from "./components/RoundTransition";
import MatchResult from "./components/MatchResult";

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
      setError(e instanceof Error ? e.message : "Failed to start match");
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
      if (
        state.status === "IN_PROGRESS" &&
        state.round_results.length > prevResults
      ) {
        setTransition(state.round_results[state.round_results.length - 1]);
      }
      setMatch(state);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Move failed");
    } finally {
      setLoading(false);
    }
  }

  const interactive =
    !!match &&
    match.status === "IN_PROGRESS" &&
    match.current_player_id === "P1" &&
    !loading &&
    !transition;

  return (
    <div className="min-h-full bg-gradient-to-b from-slate-900 to-slate-950 px-4 py-8 text-slate-100">
      <div className="mx-auto max-w-4xl">
        <header className="mb-6 text-center">
          <h1 className="text-4xl font-extrabold tracking-tight">
            Order <span className="text-slate-500">&amp;</span> Chaos
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            6×6 · two rounds · you vs. a bot
          </p>
        </header>

        {error && (
          <div className="mx-auto mb-4 max-w-md rounded-lg bg-rose-500/20 px-4 py-2 text-center text-sm text-rose-200">
            {error}
          </div>
        )}

        {!match ? (
          <p className="text-center text-slate-400">
            {loading ? "Loading…" : "No game."}
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
              <div className="rounded-xl bg-slate-800/60 p-4">
                <DifficultySelector value={difficulty} onChange={setDifficulty} />
              </div>
              <StatusPanel match={match} />
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
