from typing import Callable, Optional, Tuple
import time
from core.actions import Action
from core.controller.probability import Probability
from core.results import Result
from core.states import SenetState
from core.controller.heuristic import Heuristic

class Expectiminimax:
    
    def __init__(self, ui_callback: Optional[Callable[[], None]] = None, 
                 max_depth: int = 3, verbose: bool = True):
        self.probability = Probability()
        self.actions = Action()
        self.result = Result()
        self.ui_callback = ui_callback
        self.max_depth = max_depth
        self.verbose = verbose
        self.nodes_explored = 0
        
        self.transposition_table = {}
        self.tt_hits = 0
        

    def choose_move(self, state: SenetState, roll: int) -> Tuple[Optional[tuple], float]:

        self.nodes_explored = 0
        self.tt_hits = 0
        self.transposition_table.clear()

        start_time = time.time()

        if self.verbose:
            print("\n" + "="*60)
            print(f"EXPECTIMINIMAX: Roll={roll}, Depth={self.max_depth}")
            print("="*60)
        
        legal_moves = self.actions.available_actions(state, roll)
        
        if not legal_moves:
            return None, Heuristic.evaluate(state)
        
        best_action = None
        best_value = float('-inf')

        for i, move in enumerate(legal_moves, 1):
            from_idx, to_idx = list(move.items())[0]
            action = (from_idx, to_idx)
            
            new_state = self.result.result(state, action)
            value = self._expectiminimax(new_state, self.max_depth - 1, False)
            
            if self.verbose:
                status = "New best evaluation value" if value > best_value else ""
                print(f"  [{i}] {from_idx}→{to_idx}: {value:.2f} {status}")
            
            if value > best_value:
                best_value = value
                best_action = action

        end_time = time.time()
        elapsed_time = end_time - start_time
        
        if self.verbose:
            print(f"\nChosen action: {best_action} = {best_value:.2f}")
            print(f"Total nodes explored: {self.nodes_explored} | TT Hits: {self.tt_hits}")
            print(f"Time taken: {elapsed_time:.4f} seconds")
            print("="*60 + "\n")
        
        return best_action, best_value

    def _expectiminimax(self, state: SenetState, depth: int, is_max_player: bool) -> float:
        self.nodes_explored += 1
        
        if state.is_terminal():
            eval_value = Heuristic.evaluate(state)
            return eval_value
        
        if depth == 0:
            eval_value = Heuristic.evaluate(state)
            return eval_value
        
        state_key = (tuple(state.board), state.current_player, depth, is_max_player)
        if state_key in self.transposition_table:
            self.tt_hits += 1
            return self.transposition_table[state_key]
        
        value = self._chance_node(state, depth, is_max_player)
        
        self.transposition_table[state_key] = value
        
        return value

    def _chance_node(self, state: SenetState, depth: int, is_max_player: bool) -> float:
        expected_value = 0.0
        
        for roll in [1, 2, 3, 4, 5]:
            probability = self.probability.get_probability(roll)
            legal_moves = self.actions.available_actions(state, roll)
            
            if not legal_moves:
                new_state = state.copy()
                new_state.current_player = new_state.current_player.opponent()
                value = self._expectiminimax(new_state, depth - 1, not is_max_player)
                expected_value += probability * value
            else:
                if is_max_player:
                    max_value = float('-inf')
                    for move in legal_moves:
                        from_idx, to_idx = list(move.items())[0]
                        new_state = self.result.result(state, (from_idx, to_idx))
                        value = self._expectiminimax(new_state, depth - 1, False)
                        if value > max_value:
                            max_value = value
                    expected_value += probability * max_value
                else:
                    min_value = float('inf')
                    for move in legal_moves:
                        from_idx, to_idx = list(move.items())[0]
                        new_state = self.result.result(state, (from_idx, to_idx))
                        value = self._expectiminimax(new_state, depth - 1, True)
                        if value < min_value:
                            min_value = value
                    expected_value += probability * min_value
        
        return expected_value

    def execute_turn(self, state: SenetState, roll: int) -> SenetState:
        best_action, value = self.choose_move(state, roll)
        
        if best_action is None:
            new_state = state.copy()
            new_state.current_player = new_state.current_player.opponent()
            if self.ui_callback:
                self.ui_callback()
            return new_state
        
        new_state = self.result.result(state, best_action)
        
        if self.ui_callback:
            self.ui_callback()
        
        return new_state

    def set_ui_callback(self, callback: Callable[[], None]) -> None:
        self.ui_callback = callback
