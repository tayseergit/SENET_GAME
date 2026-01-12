from enum import Enum

class Player(str, Enum):
    WHITE = "W"
    BLACK = "B"
    EMPTY = "."

    def opponent(self):
        return Player.WHITE if self == Player.BLACK else Player.BLACK