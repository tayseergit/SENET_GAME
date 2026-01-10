
from typing import Callable, Optional

from core.actions import Action
from core.controller.probability import Probability
from core.results import Result
from core.states import SenetState
from core.component.player import Player


class Expectiminimax:
    def __init__(self, ui_callback: Optional[Callable[[], None]] = None):
        self.probability = Probability()
        self.actions = Action()
        self.result = Result()
        self.ui_callback = ui_callback

    def execute_turn(self, state: SenetState) -> SenetState:
        roll = self.probability.throw_sticks()
        legal_moves = self.actions.available_actions(state, roll)

        if not legal_moves:
            new_state = state.copy()
            new_state.current_player = new_state.current_player.opponent
            if self.ui_callback:
                self.ui_callback()
            return new_state

        move = legal_moves[0]
        from_idx, to_idx = list(move.items())[0]

        new_state = self.result.result(state, (from_idx, to_idx), roll)

        if self.ui_callback:
            self.ui_callback()

        return new_state

    def set_ui_callback(self, callback: Callable[[], None]) -> None:
        self.ui_callback = callback