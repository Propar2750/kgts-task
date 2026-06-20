import type { CellValue, Symbol } from "../types";
import SymbolPicker from "./SymbolPicker";

interface Props {
  value: CellValue;
  isWinning: boolean;
  isLast: boolean;
  isInteractive: boolean;
  showPicker: boolean;
  onClick: () => void;
  onPick: (symbol: Symbol) => void;
  onCancelPicker: () => void;
}

const symbolStyle: Record<Symbol, string> = {
  X: "text-symx [text-shadow:0_0_18px_color-mix(in_srgb,var(--color-symx)_70%,transparent)]",
  O: "text-symo [text-shadow:0_0_18px_color-mix(in_srgb,var(--color-symo)_70%,transparent)]",
};

export default function Cell({
  value,
  isWinning,
  isLast,
  isInteractive,
  showPicker,
  onClick,
  onPick,
  onCancelPicker,
}: Props) {
  const clickable = isInteractive && value === null;

  return (
    <div
      role="button"
      aria-disabled={!clickable}
      aria-label={value ? `${value} placed` : "empty cell"}
      tabIndex={clickable ? 0 : -1}
      onClick={clickable ? onClick : undefined}
      onKeyDown={
        clickable
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onClick();
              }
            }
          : undefined
      }
      data-testid="cell"
      className={[
        "group relative flex aspect-square select-none items-center justify-center rounded-lg",
        "font-display text-3xl font-bold sm:text-4xl",
        "border border-white/5 transition duration-150",
        isWinning
          ? "animate-win bg-win/15"
          : "bg-white/[0.03] " + (clickable ? "hover:border-accent/60 hover:bg-accent/10" : ""),
        isLast && !isWinning ? "ring-1 ring-accent/70" : "",
        clickable ? "cursor-pointer" : "",
      ].join(" ")}
    >
      {value ? (
        <span key={value} className={`animate-pop ${symbolStyle[value]}`}>
          {value}
        </span>
      ) : (
        clickable && (
          <span className="h-1.5 w-1.5 rounded-full bg-accent opacity-0 transition group-hover:opacity-60" />
        )
      )}
      {showPicker && <SymbolPicker onPick={onPick} onCancel={onCancelPicker} />}
    </div>
  );
}
