import random

class Probability:
    def __init__(self):
        self._rolls = [1, 2, 3, 4, 5]
    """ رمي 4 عصي وحساب النتيجة رياضياُ"""
    def throw_sticks(self):
        
        sticks = [random.choice([0, 1]) for _ in range(4)]
        white_faces = sum(sticks) 
        
        if white_faces == 1:
            return 1
        elif white_faces == 2:
            return 2
        elif white_faces == 3:
            return 3
        elif white_faces == 4:
            return 4
        elif white_faces == 0:
            return 5 
            
    """إرجاع احتمالية وقوع رمية معينة"""
    def get_probability(self, roll):
        
        total = 16
        
        probabilities = {
            1: 4 / total,
            2: 6 / total,
            3: 4 / total,
            4: 1 / total,
            5: 1 / total
        }
        
        return probabilities.get(roll, 0)