import type { Difficulty } from "../types";

interface Props {
  value: Difficulty;
  onChange: (d: Difficulty) => void;
}

const LEVELS: { id: Difficulty; label: string; hint: string }[] = [
  { id: "easy", label: "Easy", hint: "shallow + random" },
  { id: "medium", label: "Medium", hint: "3-ply search" },
  { id: "hard", label: "Hard", hint: "4-ply search" },
];

/** Segmented control choosing the bot's minimax depth. */
export default function DifficultySelector({ value, onChange }: Props) {
  return (
    <div>
      <p className="mb-1 text-xs uppercase tracking-wide text-slate-500">
        Bot difficulty
      </p>
      <div className="flex gap-1 rounded-lg bg-slate-900/60 p-1" role="group">
        {LEVELS.map((lvl) => (
          <button
            key={lvl.id}
            onClick={() => onChange(lvl.id)}
            title={lvl.hint}
            aria-pressed={value === lvl.id}
            className={[
              "flex-1 rounded-md px-2 py-1.5 text-sm font-semibold transition-colors",
              value === lvl.id
                ? "bg-emerald-500 text-slate-900"
                : "text-slate-300 hover:bg-slate-700",
            ].join(" ")}
          >
            {lvl.label}
          </button>
        ))}
      </div>
    </div>
  );
}
