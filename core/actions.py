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
        board = state.board
        
        for pos in range(len(board)):
            if board[pos] == current_player_symbol:
                if self._is_valid_move(state, pos, roll):
                    target_pos = pos + roll
                    if target_pos > HOUSE_OF_HORUS:
                        final_pos = 30 
                    else:
                        final_pos = self._apply_special_square_effects(state, target_pos)
                    
                    legal_moves.append({pos: final_pos})
        
        return legal_moves

    def _is_valid_move(self, state, from_pos, roll):
        current_player_symbol = state.current_player.value
        target_pos = from_pos + roll

        if from_pos < HOUSE_OF_HAPPINESS < target_pos:
            return False

        if target_pos > HOUSE_OF_HORUS:
            return self._can_exit_board(state, from_pos)

        if target_pos <= HOUSE_OF_HORUS:
            if state.board[target_pos] == current_player_symbol:
                return False

        return True
    
    def _can_exit_board(self, from_pos, roll):
        if from_pos >= HOUSE_OF_HAPPINESS:
            return (from_pos + roll) == 30
        return False
    
    def _apply_special_square_effects(self, state, pos):
        if pos == HOUSE_OF_WATER:
            rebirth_idx = HOUSE_OF_REBIRTH 
            
            if self._is_empty(state.board[rebirth_idx]):
                 return rebirth_idx
            
            for i in range(rebirth_idx - 1, -1, -1):
                if self._is_empty(state.board[i]):
                    return i
            return 0 
            
        return pos

    def get_legal_moves(self, state, roll):
        actions = self.available_actions(state, roll)
        return [list(a.values())[0] for a in actions]