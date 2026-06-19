import type { MatchState } from "../types";

interface Props {
  match: MatchState;
}

function roleBadge(role: "ORDER" | "CHAOS") {
  const styles =
    role === "ORDER"
      ? "bg-cyan-500/20 text-cyan-300"
      : "bg-fuchsia-500/20 text-fuchsia-300";
  return (
    <span className={`rounded px-2 py-0.5 text-xs font-semibold ${styles}`}>
      {role}
    </span>
  );
}

export default function StatusPanel({ match }: Props) {
  const yourTurn = match.current_player_id === "P1";
  const goal =
    match.human_role === "ORDER"
      ? "Make a line of 5 identical symbols."
      : "Stop the bot from making a line of 5.";

  return (
    <div className="w-full max-w-xs space-y-4 rounded-xl bg-slate-800/60 p-4 text-slate-200">
      <div className="flex items-center justify-between">
        <span className="text-sm text-slate-400">Round</span>
        <span className="text-lg font-bold">{match.current_round} / 2</span>
      </div>

      <div className="flex items-center justify-between">
        <span className="text-sm text-slate-400">You are</span>
        {roleBadge(match.human_role)}
      </div>

      <p className="text-sm text-slate-400">{goal}</p>

      {match.status === "IN_PROGRESS" && (
        <div
          className={`rounded-lg px-3 py-2 text-center text-sm font-semibold ${
            yourTurn
              ? "bg-emerald-500/20 text-emerald-300"
              : "bg-slate-700/60 text-slate-300"
          }`}
        >
          {yourTurn ? "Your turn — click a cell" : "Bot is thinking…"}
        </div>
      )}

      {match.round_results.length > 0 && (
        <div className="space-y-2 border-t border-slate-700 pt-3">
          <p className="text-xs uppercase tracking-wide text-slate-500">
            Completed rounds
          </p>
          {match.round_results.map((r) => (
            <div key={r.round} className="text-sm text-slate-300">
              <span className="font-semibold">R{r.round}</span> — Order ({r.order_player}){" "}
              {r.order_achieved_five
                ? `made a 5 in ${r.order_moves} moves`
                : "made no 5"}
              , {r.straight_fours} straight-4s
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
