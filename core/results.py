from core.component.main_house import *
from core.states import SenetState
from core.component.player import Player


class Result:
 
    def result(self, state: SenetState, action: tuple[int, int], roll: int) -> SenetState:
        return self.update_game(state, action, roll)

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


    def update_game(self, state: SenetState, action: tuple[int, int], roll: int) -> SenetState:
        new_state = state.copy()
        new_state.last_action = action

        board = new_state.board
    

        piece = new_state.current_player.value
        start_idx, end_idx = action

        #   إذا كان  حجر على 30 ولم تحركه   يعود للبعث
        if board[HOUSE_OF_HORUS] == piece and start_idx != HOUSE_OF_HORUS:
            board[HOUSE_OF_HORUS] = Player.EMPTY.value
            self._send_to_rebirth(new_state, piece)

 

        # -----------------------------
        # 2) بيت الحقائق الثلاث (28): في الدور التالي لا تخرج إلا برمية 3 وإلا تعود للبعث
        # تطبيقها عند محاولة تحريك حجر موجود على 28
        # -----------------------------
        if start_idx == HOUSE_OF_THREE_TRUTHS and roll != 3:
            # لا يسمح بتحريكه بهذه الرمية -> يرجع للبعث
            board[start_idx] = Player.EMPTY.value
            self._send_to_rebirth(new_state, piece)
 
        # -----------------------------
        # 3) بيت إعادة أتوم (29): في الدور التالي لا تخرج إلا برمية 2 وإلا تعود للبعث
        # -----------------------------
        if start_idx == HOUSE_OF_RE_ATOUM and roll != 2:
            board[start_idx] = Player.EMPTY.value
            self._send_to_rebirth(new_state, piece)
 
        # -----------------------------
        # 4) بيت حورس (30): إذا حركته هذا الدور، يسمح بالخروج بأي رمية
        # (يعني الحركة من 30 إلى خارج اللوح مسموحة)
        # -----------------------------
        if start_idx == HOUSE_OF_HORUS and end_idx >= 30:
            board[start_idx] = Player.EMPTY.value
            new_state.add_piece_to_goal(new_state.current_player)
   
 
        #  نفذ النقل العادي او التبديل
        if  not self._is_empty(board[end_idx]):
            temp =board[end_idx]
            board[end_idx] =board[start_idx]
            board[start_idx] =temp
        else: 
            board[start_idx] = Player.EMPTY.value
            board[end_idx] = piece

        #   الماء   هبط  عليه يعود  البعث
        if end_idx == HOUSE_OF_WATER:
            board[HOUSE_OF_WATER] =Player.EMPTY.value
            self._send_to_rebirth(new_state, piece)

        # تبديل الدور
        new_state.current_player = new_state.current_player.opponent
        return new_state
