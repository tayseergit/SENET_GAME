from core.component.main_house import *
from core.states import SenetState
from core.component.player import Player


class Result:
    def _is_empty(self, cell) -> bool:
        return cell  == Player.EMPTY.value


    def _send_to_rebirth(self, state: SenetState, piece_symbol: object) -> None:
        rebirth_idx = HOUSE_OF_REBIRTH

        if self._is_empty(state.board[rebirth_idx]):
            state.board[rebirth_idx] = piece_symbol
            return

        for i in range(rebirth_idx - 1, -1, -1):
            if self._is_empty(state.board[i]):
                state.board[i] = piece_symbol
                return


    def result(self, state: SenetState, action: tuple[int, int]) -> SenetState:
        new_state = state.copy()
        new_state.last_action = action
        board = new_state.board

        piece = new_state.current_player.value
        start_idx, end_idx = action

        if end_idx >= 30:
            board[start_idx] = Player.EMPTY.value
            new_state.add_piece_to_goal(new_state.current_player)
        elif not self._is_empty(board[end_idx]):
            temp =board[end_idx]
            board[end_idx] =board[start_idx]
            board[start_idx] =temp
        else:
            board[end_idx] = piece
            board[start_idx] = Player.EMPTY.value

        for house_idx in [HOUSE_OF_HORUS, HOUSE_OF_THREE_TRUTHS, HOUSE_OF_RE_ATOUM]:
            if board[house_idx] == piece and start_idx!=house_idx and end_idx!=house_idx:
                board[house_idx] = Player.EMPTY.value
                self._send_to_rebirth(new_state, piece)

        new_state.current_player = new_state.current_player.opponent()
        return new_state
