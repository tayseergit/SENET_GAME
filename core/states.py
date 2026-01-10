from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from core.actions import Action
from core.component.player import Player


@dataclass
class SenetState:
    white_number:int =0
    black_number:int=0
    board: list[Player]
    current_player: Player = Player.WHITE
    last_action: Optional[Action] = None


    @property
    def add_pices_goal(self) -> int:
        if self.current_player==Player.WHITE:
            self.white_number+=1
        else:
            self.black_number+=1
            

    # @property
    # def black_number(self) -> int:
    #     return sum(cell == Player.BLACK for cell in self.board)

    def copy(self) -> SenetState:
        return SenetState(
            board=self.board[:],
            cols=self.cols,
            current_player=self.current_player,
            last_action=self.last_action,
        )

    def get_piece_positions(self, player: Player) -> list[tuple[int, int]]:
        positions: list[tuple[int, int]] = []
        for idx, cell in enumerate(self.board):
            if cell == player:
                positions.append(self.index_to_pos(idx))
        return positions

    def pos_to_index(self, pos: tuple[int, int]) -> int:
        r, c = pos
        return r * self.cols + c

    def index_to_pos(self, idx: int) -> tuple[int, int]:
        return divmod(idx, self.cols)

    def get_cell(self, pos: tuple[int, int]) -> Player | None:
        return self.board[self.pos_to_index(pos)]

    def set_cell(self, pos: tuple[int, int], value: Player | None) -> None:
        self.board[self.pos_to_index(pos)] = value

    def is_terminal(self) -> bool:
        return self.white_number == 0 or self.black_number == 0

    def get_winner(self) -> Optional[Player]:
        if not self.is_terminal():
            return None
        if self.black_number_number == 0  :
            return Player.BLACK
        if self.white_number_number == 0 :
            return Player.WHITE
        return None

    def __eq__(self, state: object) -> bool:
        if not isinstance(state, SenetState):
            return False
        return self.current_player == state.current_player and self.board == state.board

    def __hash__(self) -> int:
        board_key = tuple(self.board)
        return hash((board_key, self.current_player.value, self.cols))
    
    def create_initial_state() -> SenetState:
        size =  30
        board: list[Player] = [Player.EMPTY.value for _ in range(size)]

        white_positions = [0, 2, 4, 6, 8, 10, 12]
        black_positions = [1, 3, 5, 7, 9, 11, 13]

        for idx in white_positions:
            board[idx] = Player.WHITE.value

        for idx in black_positions:
            board[idx] = Player.BLACK.value

        return SenetState(
            white_number= 0,
            black_number=0,
            board=board,
            current_player=Player.WHITE
        )
