import type { RoundState, Symbol } from "../types";
import Cell from "./Cell";

interface Props {
  round: RoundState;
  isInteractive: boolean;
  pendingCell: { row: number; col: number } | null;
  onCellClick: (row: number, col: number) => void;
  onPick: (symbol: Symbol) => void;
  onCancelPicker: () => void;
}

export default function Board({
  round,
  isInteractive,
  pendingCell,
  onCellClick,
  onPick,
  onCancelPicker,
}: Props) {
  const winning = new Set((round.winning_line ?? []).map(([r, c]) => `${r},${c}`));
  const last = round.move_history.at(-1);
  const lastKey = last ? `${last.row},${last.col}` : null;

  return (
    <div className="relative rounded-2xl bg-accent/20 p-px shadow-[0_0_60px_-12px_var(--accent)]">
      <div className="grid grid-cols-6 gap-1.5 rounded-2xl bg-ink-2/80 p-2.5 ring-1 ring-white/5 backdrop-blur-sm">
        {round.board.map((row, r) =>
          row.map((value, c) => (
            <Cell
              key={`${r},${c}`}
              value={value}
              isWinning={winning.has(`${r},${c}`)}
              isLast={lastKey === `${r},${c}`}
              isInteractive={isInteractive}
              showPicker={pendingCell?.row === r && pendingCell?.col === c}
              onClick={() => onCellClick(r, c)}
              onPick={onPick}
              onCancelPicker={onCancelPicker}
            />
          )),
        )}
      </div>
    </div>
  );
}
