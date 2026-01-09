from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Player(str, Enum):
    WHITE = "W"
    BLACK = "B"
    EMPTY = "*"


@dataclass(frozen=True)
class Action:
    from_position: tuple[int, int]
    roll: int


@dataclass
class SenetState:
    white_number=0
    black_number=0
    board: list[list[str]]
    current_player: Player = Player.WHITE
    last_action: Optional[Action] = None

 
    def copy(self) :
        return SenetState(
            board=[row[:] for row in self.board],
            current_player=self.current_player,
            last_action=self.last_action,
        )

    def get_piece_positions(self, player: Player) -> list[tuple[int, int]]:
        target = player.value
        positions: list[tuple[int, int]] = []
        for r, row in enumerate(self.board):
            for c, cell in enumerate(row):
                if cell == target:
                    positions.append((r, c))
        return positions

    def is_terminal(self) -> bool:
        return self.white_number == 0 or self.black_number == 0

    def get_winner(self) :
        if not self.is_terminal():
            return None
        elif self.white_number == 0 :
            return Player.WHITE
        elif self.black_number == 0:
            return Player.BLACK
        return None

    def __eq__(self, state):
        if not isinstance(state, SenetState):
            return False
        return self.current_player == state.current_player and self.board == state.board

    def __hash__(self) -> int:
        board_key = tuple(tuple(row) for row in self.board)
        return hash((board_key, self.current_player.value))


def create_initial_state(rows: int = 3, cols: int = 10) -> SenetState:
    board = [[Player.EMPTY.value for _ in range(cols)] for _ in range(rows)]
    if rows >= 2 and cols >= 10:
        first_row = [Player.WHITE.value, Player.BLACK.value] * (cols // 2)
        board[0][: len(first_row)] = first_row
        second_row = [Player.BLACK.value, Player.WHITE.value] * (cols // 2)
        board[1][: len(second_row)] = second_row
    return SenetState(board=board, current_player=Player.WHITE)