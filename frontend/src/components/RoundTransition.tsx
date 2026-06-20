import type { ReactNode } from "react";
import type { RoundResult } from "../types";

interface Props {
  result: RoundResult;
  nextHumanRole: "ORDER" | "CHAOS";
  onContinue: () => void;
}

/** Shown after round 1 completes, before round 2 begins. */
export default function RoundTransition({
  result,
  nextHumanRole,
  onContinue,
}: Props) {
  const orderLine = result.order_achieved_five
    ? `Order (${result.order_player}) forged a line of five in ${result.order_moves} moves.`
    : `Order (${result.order_player}) never completed a five — Chaos held the line.`;

  return (
    <Overlay>
      <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-muted">
        Round {result.round} complete
      </p>
      <h2 className="font-display text-2xl font-bold">The board is reset.</h2>
      <p className="text-ink-text/85">{orderLine}</p>
      <p className="font-mono text-xs text-muted">
        Straight-4s created: {result.straight_fours}
      </p>
      <div className="mt-1 w-full rounded-xl bg-white/[0.04] px-4 py-3 text-center">
        Round 2 — you now play as{" "}
        <span className="font-display font-bold text-chaos">{nextHumanRole}</span>.
        Beat the bot's first round.
      </div>
      <button
        className="mt-1 rounded-lg bg-chaos px-6 py-2.5 font-semibold text-ink transition hover:brightness-110"
        onClick={onContinue}
        autoFocus
      >
        Start Round 2
      </button>
    </Overlay>
  );
}

function Overlay({ children }: { children: ReactNode }) {
  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center bg-ink/80 p-4 backdrop-blur-sm">
      <div className="animate-rise flex w-full max-w-md flex-col items-center gap-3 rounded-2xl bg-ink-2 p-7 text-center ring-1 ring-white/10 shadow-2xl">
        {children}
      </div>
    </div>
  );
}
