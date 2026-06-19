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
  const winning = new Set(
    (round.winning_line ?? []).map(([r, c]) => `${r},${c}`),
  );

  return (
    <div className="grid grid-cols-6 gap-1.5 rounded-xl bg-slate-950/60 p-2 shadow-xl">
      {round.board.map((row, r) =>
        row.map((value, c) => (
          <Cell
            key={`${r},${c}`}
            value={value}
            isWinning={winning.has(`${r},${c}`)}
            isInteractive={isInteractive}
            showPicker={pendingCell?.row === r && pendingCell?.col === c}
            onClick={() => onCellClick(r, c)}
            onPick={onPick}
            onCancelPicker={onCancelPicker}
          />
        )),
      )}
    </div>
  );
}
