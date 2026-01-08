'''
enum class for black player and white player to handle what is the current player is 

'''


from enum import Enum

class Player(Enum):
    BLACK = 1
    WHITE = 2

    @property
    def opponent(self):
        # تبديل الدور للاعب الخصم
        return Player.WHITE if self == Player.BLACK else Player.BLACK
