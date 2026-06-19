import type { CellValue, Symbol } from "../types";
import SymbolPicker from "./SymbolPicker";

interface Props {
  value: CellValue;
  isWinning: boolean;
  isInteractive: boolean;
  showPicker: boolean;
  onClick: () => void;
  onPick: (symbol: Symbol) => void;
  onCancelPicker: () => void;
}

const symbolColor: Record<Symbol, string> = {
  X: "text-cyan-300",
  O: "text-amber-300",
};

export default function Cell({
  value,
  isWinning,
  isInteractive,
  showPicker,
  onClick,
  onPick,
  onCancelPicker,
}: Props) {
  const clickable = isInteractive && value === null;
  return (
    // A div (not a button) so the X/O picker's buttons aren't nested in a button.
    <div
      role="button"
      aria-disabled={!clickable}
      tabIndex={clickable ? 0 : -1}
      onClick={clickable ? onClick : undefined}
      onKeyDown={
        clickable
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") onClick();
            }
          : undefined
      }
      data-testid="cell"
      className={[
        "relative flex aspect-square select-none items-center justify-center rounded-md text-3xl font-bold transition-colors sm:text-4xl",
        isWinning ? "bg-emerald-500/30 ring-2 ring-emerald-400" : "bg-slate-800",
        clickable ? "cursor-pointer hover:bg-slate-700" : "",
        value ? symbolColor[value] : "text-transparent",
      ].join(" ")}
    >
      {value ?? ""}
      {showPicker && <SymbolPicker onPick={onPick} onCancel={onCancelPicker} />}
    </div>
  );
}
