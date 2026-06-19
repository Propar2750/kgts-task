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
    ? `Order (${result.order_player}) completed a straight-5 in ${result.order_moves} moves.`
    : `Order (${result.order_player}) failed to make a straight-5 — Chaos held them off.`;

  return (
    <Overlay>
      <h2 className="text-2xl font-bold text-slate-100">Round {result.round} complete</h2>
      <p className="text-slate-300">{orderLine}</p>
      <p className="text-sm text-slate-400">
        Straight-4s created: {result.straight_fours}
      </p>
      <div className="mt-2 rounded-lg bg-slate-800 p-3 text-center text-slate-200">
        Round 2 — you now play as{" "}
        <span className="font-bold text-cyan-300">{nextHumanRole}</span>.
      </div>
      <button
        className="mt-2 rounded-lg bg-emerald-500 px-6 py-2 font-semibold text-slate-900 hover:bg-emerald-400"
        onClick={onContinue}
      >
        Start Round 2
      </button>
    </Overlay>
  );
}

function Overlay({ children }: { children: ReactNode }) {
  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/70 p-4">
      <div className="flex w-full max-w-md flex-col items-center gap-3 rounded-2xl bg-slate-900 p-6 text-center shadow-2xl ring-1 ring-slate-700">
        {children}
      </div>
    </div>
  );
}
