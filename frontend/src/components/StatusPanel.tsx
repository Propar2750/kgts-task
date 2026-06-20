import type { ReactNode } from "react";
import type { MatchState } from "../types";

interface Props {
  match: MatchState;
}

function Eyebrow({ children }: { children: ReactNode }) {
  return (
    <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-muted">
      {children}
    </p>
  );
}

export default function StatusPanel({ match }: Props) {
  const yourTurn = match.current_player_id === "P1";
  const role = match.human_role;
  const goal =
    role === "ORDER"
      ? "Build a line of five — any direction, X or O."
      : "Break every line. Let no five complete.";

  return (
    <div className="space-y-4 rounded-2xl bg-ink-2/70 p-5 ring-1 ring-white/5 backdrop-blur-sm">
      {/* Allegiance — the emotional anchor, recolored by role */}
      <div>
        <Eyebrow>Round {match.current_round} of 2 · you are</Eyebrow>
        <div className="mt-1 flex items-baseline gap-2">
          <span
            className="font-display text-2xl font-bold tracking-tight"
            style={{ color: "var(--accent)" }}
          >
            {role}
          </span>
          <span className="text-sm text-muted">vs. the bot</span>
        </div>
        <p className="mt-1 text-sm text-ink-text/80">{goal}</p>
      </div>

      {/* Turn indicator */}
      {match.status === "IN_PROGRESS" && (
        <div
          className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold"
          style={{
            background: yourTurn
              ? "color-mix(in srgb, var(--accent) 16%, transparent)"
              : "rgba(255,255,255,0.04)",
            color: yourTurn ? "var(--accent)" : "var(--color-muted)",
          }}
        >
          {yourTurn ? (
            <>
              <span className="h-2 w-2 rounded-full bg-accent" />
              Your move — pick a cell
            </>
          ) : (
            <>
              <span className="flex gap-0.5">
                <span className="animate-[blink_1s_infinite] h-1.5 w-1.5 rounded-full bg-current" />
                <span className="animate-[blink_1s_infinite_0.2s] h-1.5 w-1.5 rounded-full bg-current" />
                <span className="animate-[blink_1s_infinite_0.4s] h-1.5 w-1.5 rounded-full bg-current" />
              </span>
              Bot is thinking
            </>
          )}
        </div>
      )}

      {/* Completed rounds */}
      {match.round_results.length > 0 && (
        <div className="space-y-2 border-t border-white/8 pt-3">
          <Eyebrow>Scoreboard</Eyebrow>
          {match.round_results.map((r) => (
            <div
              key={r.round}
              className="flex items-center justify-between rounded-md bg-white/[0.03] px-2.5 py-1.5 text-sm"
            >
              <span className="text-muted">
                R{r.round} · Order {r.order_player}
              </span>
              <span className="font-mono text-xs text-ink-text/90">
                {r.order_achieved_five ? `5 in ${r.order_moves}` : "no 5"} ·{" "}
                {r.straight_fours}×4
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
