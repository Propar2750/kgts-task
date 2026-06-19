import type { Symbol } from "../types";

interface Props {
  onPick: (symbol: Symbol) => void;
  onCancel: () => void;
}

/** Small popover anchored over a clicked cell to choose X or O. */
export default function SymbolPicker({ onPick, onCancel }: Props) {
  return (
    <div
      className="absolute inset-0 z-20 flex items-center justify-center gap-1 rounded-md bg-slate-900/95 ring-2 ring-slate-500"
      onClick={(e) => e.stopPropagation()}
    >
      <button
        className="flex h-8 w-8 items-center justify-center rounded bg-cyan-500/20 text-lg font-bold text-cyan-300 hover:bg-cyan-500/40"
        onClick={() => onPick("X")}
        aria-label="Place X"
      >
        X
      </button>
      <button
        className="flex h-8 w-8 items-center justify-center rounded bg-amber-500/20 text-lg font-bold text-amber-300 hover:bg-amber-500/40"
        onClick={() => onPick("O")}
        aria-label="Place O"
      >
        O
      </button>
      <button
        className="absolute -right-2 -top-2 flex h-5 w-5 items-center justify-center rounded-full bg-slate-700 text-xs text-slate-300 hover:bg-slate-600"
        onClick={onCancel}
        aria-label="Cancel"
      >
        ×
      </button>
    </div>
  );
}
