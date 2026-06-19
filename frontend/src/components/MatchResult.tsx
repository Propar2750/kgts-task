import type { MatchState } from "../types";

interface Props {
  match: MatchState;
  onPlayAgain: () => void;
}

export default function MatchResult({ match, onPlayAgain }: Props) {
  const winner = match.overall_winner;
  const youWon = winner === "P1";
  const draw = winner === "DRAW";

  const headline = draw
    ? "It's a draw!"
    : youWon
      ? "You win! 🎉"
      : "The bot wins";

  const headlineColor = draw
    ? "text-slate-100"
    : youWon
      ? "text-emerald-300"
      : "text-rose-300";

  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/70 p-4">
      <div className="flex w-full max-w-md flex-col items-center gap-4 rounded-2xl bg-slate-900 p-6 text-center shadow-2xl ring-1 ring-slate-700">
        <h2 className={`text-3xl font-extrabold ${headlineColor}`}>{headline}</h2>
        {match.winner_reason && (
          <p className="text-slate-300">{match.winner_reason}</p>
        )}

        <div className="w-full space-y-1 rounded-lg bg-slate-800 p-3 text-left text-sm text-slate-300">
          {match.round_results.map((r) => (
            <div key={r.round}>
              <span className="font-semibold">Round {r.round}</span> — Order ({r.order_player}):{" "}
              {r.order_achieved_five
                ? `5-in-a-row in ${r.order_moves} moves`
                : "no 5"}
              , {r.straight_fours} straight-4s
            </div>
          ))}
        </div>

        <button
          className="mt-1 rounded-lg bg-emerald-500 px-6 py-2 font-semibold text-slate-900 hover:bg-emerald-400"
          onClick={onPlayAgain}
        >
          Play again
        </button>
      </div>
    </div>
  );
}
