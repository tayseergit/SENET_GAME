from core.states import SenetState
from core.component.player import Player

class Heuristic:
    
    def evaluate(state: SenetState) -> float:
        white_count = state.white_number()
        black_count = state.black_number()
        
        if white_count == 0:
            return -10000
        if black_count == 0:
            return 10000
        
        score = (state.white_goal_count - state.black_goal_count) * 1000
        
        score += (white_count - black_count) * 50
        
        white_positions = []
        black_positions = []
        
        for i, cell in enumerate(state.board):
            if cell == Player.WHITE.value:
                white_positions.append(i)
                score += i * 10
                if i == 25:
                    score += 50
                elif i in {27, 28, 29}:
                    score -= 50
                    
            elif cell == Player.BLACK.value:
                black_positions.append(i)
                score -= i * 10
                if i == 25:
                    score -= 50
                elif i in {27, 28, 29}:
                    score += 50
        
        for w_pos in white_positions:
            blocking = sum(1 for b_pos in black_positions if w_pos > b_pos)
            score += blocking * 5
        
        for b_pos in black_positions:
            blocking = sum(1 for w_pos in white_positions if b_pos > w_pos)
            score -= blocking * 5
        
        for w_pos in white_positions:
            if any(0 < w_pos - b_pos <= 5 for b_pos in black_positions):
                score -= 15
        
        for b_pos in black_positions:
            if any(0 < b_pos - w_pos <= 5 for w_pos in white_positions):
                score += 15
        
        return score