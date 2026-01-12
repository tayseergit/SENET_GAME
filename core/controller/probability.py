import random

class Probability:
    def __init__(self):
        self._rolls = [1, 2, 3, 4, 5]
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
        return 5
             
    def get_probability(self, roll):

        probabilities = {
            1: 0.25,
            2: 0.375,
            3: 0.25,
            4: 0.0625,
            5: 0.0625
        }
        
        return probabilities.get(roll, 0)