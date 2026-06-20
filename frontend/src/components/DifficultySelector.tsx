import type { Difficulty } from "../types";

interface Props {
  value: Difficulty;
  onChange: (d: Difficulty) => void;
}

const LEVELS: { id: Difficulty; label: string; hint: string }[] = [
  { id: "easy", label: "Easy", hint: "depth 2, plays loose" },
  { id: "medium", label: "Medium", hint: "depth 3" },
  { id: "hard", label: "Hard", hint: "depth 4, looks ahead" },
];

/** Segmented control choosing the bot's minimax search depth. */
export default function DifficultySelector({ value, onChange }: Props) {
  return (
    <div className="rounded-2xl bg-ink-2/70 p-5 ring-1 ring-white/5 backdrop-blur-sm">
      <p className="mb-2 font-mono text-[10px] uppercase tracking-[0.18em] text-muted">
        Bot difficulty
      </p>
      <div className="flex gap-1 rounded-lg bg-black/30 p-1" role="group">
        {LEVELS.map((lvl) => {
          const active = value === lvl.id;
          return (
            <button
              key={lvl.id}
              onClick={() => onChange(lvl.id)}
              title={lvl.hint}
              aria-pressed={active}
              className={[
                "flex-1 rounded-md px-2 py-1.5 text-sm font-semibold transition",
                active ? "text-ink" : "text-muted hover:text-ink-text",
              ].join(" ")}
              style={active ? { background: "var(--accent)" } : undefined}
            >
              {lvl.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
