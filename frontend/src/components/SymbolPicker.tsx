import type { Symbol } from "../types";

interface Props {
  onPick: (symbol: Symbol) => void;
  onCancel: () => void;
}

/** Popover anchored over a clicked cell to choose which symbol to place. */
export default function SymbolPicker({ onPick, onCancel }: Props) {
  return (
    <div
      className="animate-pop absolute inset-0 z-20 flex items-center justify-center gap-1.5 rounded-lg bg-ink-2/95 ring-1 ring-white/15 backdrop-blur-sm"
      onClick={(e) => e.stopPropagation()}
    >
      <button
        className="flex h-9 w-9 items-center justify-center rounded-md font-display text-xl font-bold text-symx ring-1 ring-symx/40 transition hover:bg-symx/20"
        onClick={() => onPick("X")}
        aria-label="Place X"
      >
        X
      </button>
      <button
        className="flex h-9 w-9 items-center justify-center rounded-md font-display text-xl font-bold text-symo ring-1 ring-symo/40 transition hover:bg-symo/20"
        onClick={() => onPick("O")}
        aria-label="Place O"
      >
        O
      </button>
      <button
        className="absolute -right-2 -top-2 flex h-5 w-5 items-center justify-center rounded-full bg-white/15 text-xs text-white/80 transition hover:bg-white/30"
        onClick={onCancel}
        aria-label="Cancel"
      >
        ×
      </button>
    </div>
  );
}
