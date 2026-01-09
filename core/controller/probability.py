

import random

class Probability:
    def __init__(self):
        self._rolls = [1, 2, 3, 4, 5]
        self._weights = [0.25, 0.375, 0.25, 0.0625, 0.0625]
    
    """إرجاع رمية عشوائية (1-5) مع احتماليتها"""
    def throw_sticks(self):
        roll = random.choices(self._rolls, weights=self._weights, k=1)[0]
        return roll
    
    """إرجاع احتمالية وقوع رمية معينة"""
    def get_probability(self, roll):
        
        if roll in self._rolls:
            index = self._rolls.index(roll)
            return self._weights[index]
        return 0.0