from __future__ import annotations

from dataclasses import dataclass

from core.actions import Action
from core.component.player import Player
from core.states import SenetState


class Result:
    @staticmethod
    def result(self,state: SenetState, action) -> SenetState:
        return self.update_game(state, action)

 
    def update_game(self, state, action,player) -> SenetState:
         new_state = state.copy()
         new_state.last_action = action
         current_player = new_state.current_player
         start_index= action[0]
         end_index= action[1]
         
 

         return new_state

 