import type { MatchState } from "../types";

interface Props {
  match: MatchState;
  onPlayAgain: () => void;
}

export default function MatchResult({ match, onPlayAgain }: Props) {
  const winner = match.overall_winner;
  const youWon = winner === "P1";
  const draw = winner === "DRAW";

  const headline = draw ? "Stalemate." : youWon ? "You win." : "The bot wins.";
  const color = draw ? "var(--color-ink-text)" : youWon ? "var(--color-win)" : "var(--color-chaos)";

  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center bg-ink/80 p-4 backdrop-blur-sm">
      <div className="animate-rise flex w-full max-w-md flex-col items-center gap-4 rounded-2xl bg-ink-2 p-7 text-center ring-1 ring-white/10 shadow-2xl">
        <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-muted">
          Match result
        </p>
        <h2 className="font-display text-4xl font-bold" style={{ color }}>
          {headline}
        </h2>
        {match.winner_reason && (
          <p className="text-ink-text/85">{match.winner_reason}</p>
        )}

        <div className="w-full space-y-1.5 rounded-xl bg-white/[0.04] p-4 text-left">
          {match.round_results.map((r) => (
            <div key={r.round} className="flex items-center justify-between text-sm">
              <span className="text-muted">
                Round {r.round} · Order {r.order_player}
              </span>
              <span className="font-mono text-xs text-ink-text/90">
                {r.order_achieved_five ? `5 in ${r.order_moves}` : "no 5"} ·{" "}
                {r.straight_fours}×4
              </span>
            </div>
          ))}
        </div>

        <button
          className="mt-1 rounded-lg px-6 py-2.5 font-semibold text-ink transition hover:brightness-110"
          style={{ background: "var(--accent)" }}
          onClick={onPlayAgain}
          autoFocus
        >
          Play again
        </button>
      </div>
    </div>
  );
}
