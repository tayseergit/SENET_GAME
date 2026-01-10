from core.component.main_house import *
from core.states import SenetState
from core.component.player import Player


class Result:
 
    def result(self, state: SenetState, action: tuple[int, int], roll: int) -> SenetState:
        return self.update_game(state, action, roll)

    def _is_empty(self, cell) -> bool:
        return cell  == Player.EMPTY.value

    def _empty_symbol_like(self, board) -> object:
        # لو اللوح يستخدم None أو "." نحافظ على نفس الأسلوب
        return None if any(cell is None for cell in board) else "."

    def _piece_symbol(self, player: Player) -> object:
        # لو اللوح يخزن Player نفسه أو value
        return player.value if hasattr(player, "value") else player

    def _send_to_rebirth(self, state: SenetState, piece_symbol: object) -> None:
        rebirth_idx = HOUSE_OF_REBIRTH - 1

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
        total = len(board)
        if total != 30:
            # لوح غير متوافق مع سنِت القياسي
            return new_state

        current_player = new_state.current_player
        piece = self._piece_symbol(current_player)
        empty_sym = self._empty_symbol_like(board)

        start_idx, end_idx = action

        # -----------------------------
        # 0) قاعدة بيت حورس (30): إذا كان لديك حجر على 30 ولم تحركه هذا الدور -> يعود للبعث
        # -----------------------------
        horus_idx = HOUSE_OF_HORUS - 1  # 29
        if board[horus_idx] == piece and start_idx != horus_idx:
            board[horus_idx] = empty_sym
            self._send_to_rebirth(new_state, piece)

        # تحقق حدود البداية
        if not (0 <= start_idx < total):
            return new_state

        # يجب أن تكون قطعة اللاعب في خانة البداية
        if board[start_idx] != piece:
            return new_state

        # -----------------------------
        # 1) بيت السعادة (26): ممنوع القفز فوقه — لازم تهبط عليه مباشرة إذا كنت ستعبره
        # -----------------------------
        happiness_idx = HOUSE_OF_HAPPINESS - 1  # 25
        if start_idx < happiness_idx and end_idx > happiness_idx and end_idx != happiness_idx:
            # قفز فوق 26 => حركة غير قانونية
            return new_state

        # -----------------------------
        # 2) بيت الحقائق الثلاث (28): في الدور التالي لا تخرج إلا برمية 3 وإلا تعود للبعث
        # تطبيقها عند محاولة تحريك حجر موجود على 28
        # -----------------------------
        three_truths_idx = HOUSE_OF_THREE_TRUTHS - 1  # 27
        if start_idx == three_truths_idx and roll != 3:
            # لا يسمح بتحريكه بهذه الرمية -> يرجع للبعث
            board[start_idx] = empty_sym
            self._send_to_rebirth(new_state, piece)
            new_state.current_player = new_state.current_player.opponent
            return new_state

        # -----------------------------
        # 3) بيت إعادة أتوم (29): في الدور التالي لا تخرج إلا برمية 2 وإلا تعود للبعث
        # -----------------------------
        re_atoum_idx = HOUSE_OF_RE_ATOUM - 1  # 28
        if start_idx == re_atoum_idx and roll != 2:
            board[start_idx] = empty_sym
            self._send_to_rebirth(new_state, piece)
            new_state.current_player = new_state.current_player.opponent
            return new_state

        # -----------------------------
        # 4) بيت حورس (30): إذا حركته هذا الدور، يسمح بالخروج بأي رمية
        # (يعني الحركة من 30 إلى خارج اللوح مسموحة)
        # -----------------------------
        if start_idx == horus_idx and end_idx >= total:
            board[start_idx] = empty_sym  # خرج من اللوح
            new_state.current_player = new_state.current_player.opponent
            return new_state

        # -----------------------------
        # 5) محاولة الخروج من اللوح من غير (30) تحتاج قواعد أخرى (إن أردت)
        # هنا: نمنع الخروج إلا إذا كان من 30 (حسب النص الذي أعطيتني)
        # -----------------------------
        if end_idx >= total:
            return new_state

        # -----------------------------
        # 6) منع الهبوط على قطعة لنفس اللاعب
        # -----------------------------
        if board[end_idx] == piece:
            return new_state

        # نفذ النقل العادي
        board[start_idx] = empty_sym
        board[end_idx] = piece

        # -----------------------------
        # 7) بيت الماء (27): إذا هبط حجر عليه يعود فوراً إلى بيت البعث
        # -----------------------------
        water_idx = HOUSE_OF_WATER - 1  # 26
        if end_idx == water_idx:
            board[water_idx] = empty_sym
            self._send_to_rebirth(new_state, piece)

        # تبديل الدور
        new_state.current_player = new_state.current_player.opponent
        return new_state
