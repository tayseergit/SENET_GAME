'''

class action 

- `available_actions(state, roll)` - returns legal moves (list of [current index : new availble index]) depend on probapility class ,for current player (ACTIONS function)
- `_is_valid_move(state, from_pos, roll)` - checks if move is legal
- `_can_exit_board(state, from_pos, roll)` - checks if piece can exit
- `_apply_special_square_effects(state, pos)` - applies special square rules
- `get_legal_moves(state, roll)` - legacy function returning positions


'''

from core.component.main_house import *


class Action:
    def __init__(self):
        self.from_position = None
        self.steps = None
 
    def available_actions(self, state, roll):
        # إرجاع قائمة بالتحركات المتاحة للاعب الحالي
        legal_moves = []
        current_player = state.current_player
        
        for pos, piece in enumerate(state.board):
            if piece == current_player:
                if self._is_valid_move(state, pos, roll):
                    target_pos = pos + roll
                    # تطبيق تأثيرات المربعات الخاصة فوراً لتحديد الموقع النهائي
                    final_pos = self._apply_special_square_effects(state, target_pos)
                    legal_moves.append({pos: final_pos})
        
        return legal_moves

    #التحقق مما إذا كانت الحركة قانونية
    def _is_valid_move(self, state, from_pos, roll):
        
        
        target_pos = from_pos + roll

        #  التحقق من خروج القطعة
        if target_pos >= HOUSE_OF_HORUS:
            return self._can_exit_board(state, from_pos, roll)

        # اذا المربع المستهدف مشغول بقطعة لنفس اللاعب
        if state.board[target_pos] == state.current_player:
            return False

        return True
    
    
    """التحقق مما إذا كانت القطعة في وضع يسمح لها بالخروج"""
    def _can_exit_board(self, state, from_pos, roll):
        
        if from_pos >= 25:
            return (from_pos + roll) == HOUSE_OF_HORUS
        return False
    
    """تطبيق قاعدة الغرق في مربع الماء"""
    def _apply_special_square_effects(self, state, pos):
        
        if pos == self.HOUSE_OF_WATER:
            # العودة إلى بيت الولادة إذا كان فارغاً، وإلا العودة لأقرب مربع فاضي
            rebirth_index = HOUSE_OF_REBIRTH 
            
            # التأكد ما إذا كان مربع الولادة محجوزاً
            if state.board[rebirth_index] is not None:
                # البحث عن أقرب مربع فارغ قبل المربع 15 
                for i in range(rebirth_index , -1, -1):
                    if state.board[i] is None:
                        return i
                return 0 #ُإذا لم يكن هناك مربع فارغ، العودة إلى البداية
            return rebirth_index
            
        return pos

    """دالة  ترجع قائمة بالمواقع الجديدة المتاحة """
    def get_legal_moves(self, state, roll):
        actions = self.available_actions(state, roll)
        return [list(a.values())[0] for a in actions]