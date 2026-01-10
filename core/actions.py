'''

class action 

- `available_actions(state, roll)` - returns legal moves (list of [current index : new availble index]) depend on probapility class ,for current player (ACTIONS function)
- `_is_valid_move(state, from_pos, roll)` - checks if move is legal
- `_can_exit_board(state, from_pos, roll)` - checks if piece can exit
- `_apply_special_square_effects(state, pos)` - applies special square rules
- `get_legal_moves(state, roll)` - legacy function returning positions


'''

from core.component.main_house import *
from core.component.player import Player

class Action:
    def __init__(self):
        self.from_position = None
        self.steps = None
 
    def _is_empty(self, cell) -> bool:
        return cell == Player.EMPTY.value
 
    def available_actions(self, state, roll):
        legal_moves = []
        current_player_symbol = state.current_player.value
        
        for pos, piece in enumerate(state.board):
            if piece == current_player_symbol:
                if self._is_valid_move(state, pos, roll):
                    target_pos = pos + roll
                    
                    # إذا كانت الحركة تؤدي للخروج
                    if target_pos > HOUSE_OF_HORUS:
                        final_pos = 30 
                    else:
                        final_pos = self._apply_special_square_effects(state, target_pos)
                    
                    legal_moves.append({pos: final_pos})
        
        return legal_moves

    def _is_valid_move(self, state, from_pos, roll):
        current_player_symbol = state.current_player.value
        target_pos = from_pos + roll

        #  شرط المرور الإجباري على بيت السعادة 
        if from_pos < HOUSE_OF_HAPPINESS and target_pos > HOUSE_OF_HAPPINESS:
            return False

        # . التحقق من خروج القطعة 
        if target_pos > HOUSE_OF_HORUS:
            return self._can_exit_board(state, from_pos, roll)

        # 3. التحقق من المربعات المشغولة بقطع الصديق
        if target_pos <= HOUSE_OF_HORUS:
            if state.board[target_pos] == current_player_symbol:
                return False

        return True
    
    def _can_exit_board(self, state, from_pos, roll):
        # قاعدة الخروج 
        # ولا يسمح بالخروج إلا للقطع التي اجتازت أو تقف في بيت السعادة 
        if from_pos >= HOUSE_OF_HAPPINESS:
            return (from_pos + roll) == 30
        return False
    
    def _apply_special_square_effects(self, state, pos):
        # إذا كان المربع هو بيت الماء 
        if pos == HOUSE_OF_WATER:
            rebirth_idx = HOUSE_OF_REBIRTH 
            
            # إذا كان بيت الولادة (14) فارغاً،  
            if self._is_empty(state.board[rebirth_idx]):
                 return rebirth_idx
            
            # وإلا نبحث عن أول مربع فارغ للخلف من المربع 14
            for i in range(rebirth_idx - 1, -1, -1):
                if self._is_empty(state.board[i]):
                    return i
            return 0 
            
        return pos

    def get_legal_moves(self, state, roll):
        actions = self.available_actions(state, roll)
        return [list(a.values())[0] for a in actions]