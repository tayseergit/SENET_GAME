from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from core.actions import Action
from core.component.player import Player


BOARD_SIZE = 30
BOARD_COLS = 10


@dataclass
class SenetState:
    board: list[str]
    current_player: Player = Player.WHITE
    last_action: Optional[Action] = None
    white_goal_count: int = 0
    black_goal_count: int = 0

    @property
    def white_number(self) -> int:
        return sum(cell == Player.WHITE.value for cell in self.board)

    @property
    def black_number(self) -> int:
        return sum(cell == Player.BLACK.value for cell in self.board)

    def copy(self) -> SenetState:
        return SenetState(
            board=self.board[:],
            current_player=self.current_player,
            last_action=self.last_action,
            white_goal_count=self.white_goal_count,
            black_goal_count=self.black_goal_count,
        )

    def pos_to_index(self, pos: tuple[int, int]) -> int:
        r, c = pos
        return r * BOARD_COLS + c

    def index_to_pos(self, idx: int) -> tuple[int, int]:
        return divmod(idx, BOARD_COLS)

    def get_cell(self, pos: tuple[int, int]) -> str:
        return self.board[self.pos_to_index(pos)]

    def set_cell(self, pos: tuple[int, int], value: str) -> None:
        self.board[self.pos_to_index(pos)] = value

    def add_piece_to_goal(self, player: Player) -> None:
        if player == Player.WHITE:
            self.white_goal_count += 1
        else:
            self.black_goal_count += 1

    def is_terminal(self) -> bool:
        return self.white_number == 0 or self.black_number == 0

    def get_winner(self) -> Optional[Player]:
        if not self.is_terminal():
            return None
        if self.white_number == 0 and self.black_number > 0:
            return Player.BLACK
        if self.black_number == 0 and self.white_number > 0:
            return Player.WHITE
        return None

    def __eq__(self, state: object) -> bool:
        if not isinstance(state, SenetState):
            return False
        return (
            self.current_player == state.current_player
            and self.board == state.board
            and self.white_goal_count == state.white_goal_count
            and self.black_goal_count == state.black_goal_count
        )

    def __hash__(self) -> int:
        board_key = tuple(self.board)
        return hash((board_key, self.current_player.value, self.white_goal_count, self.black_goal_count))


def create_initial_state() -> SenetState:
    board: list[str] = [Player.EMPTY.value for _ in range(BOARD_SIZE)]
    white_positions = [0, 2, 4, 6, 8, 10, 12]
    black_positions = [1, 3, 5, 7, 9, 11, 13]

    for idx in white_positions:
        board[idx] = Player.WHITE.value

    for idx in black_positions:
        board[idx] = Player.BLACK.value

    return SenetState(board=board, current_player=Player.WHITE)
