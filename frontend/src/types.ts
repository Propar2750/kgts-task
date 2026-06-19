// Types mirroring the backend's serialized match state (order_chaos/match.py).

export type Symbol = "X" | "O";
export type CellValue = Symbol | null;
export type Role = "ORDER" | "CHAOS";
export type PlayerId = "P1" | "P2";
export type RoundStatus = "IN_PROGRESS" | "ORDER_WIN" | "CHAOS_WIN";
export type MatchStatus = "IN_PROGRESS" | "COMPLETE";

export interface RoundState {
  board: CellValue[][];
  current_player: Role;
  status: RoundStatus;
  winning_line: [number, number][] | null;
  order_moves: number;
  move_history: { row: number; col: number; symbol: Symbol; player: Role }[];
}

export interface RoundResult {
  round: number;
  order_player: PlayerId;
  order_achieved_five: boolean;
  order_moves: number;
  straight_fours: number;
  round_winner_role: Role | null;
  final_board: CellValue[][] | null;
}

export interface MatchState {
  current_round: number;
  round: RoundState;
  round_results: RoundResult[];
  status: MatchStatus;
  overall_winner: PlayerId | "DRAW" | null;
  winner_reason: string | null;
  current_player_id: PlayerId | null;
  human_role: Role;
}

export interface BotMove {
  row: number;
  col: number;
  symbol: Symbol;
}

export interface MoveResponse {
  state: MatchState;
  bot_moves: BotMove[];
}
