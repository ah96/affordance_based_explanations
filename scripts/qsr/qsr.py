import math

# global variables
PI = math.pi

class QSR(object):
    # constructor
    def __init__(self, binary_qsr_choice, ternary_qsr_choice, R):
        self.binary_qsr_choice = 1
        self.ternary_qsr_choice = 3
        self.R = 1    
        self.PI = PI

        self.defineBinaryQsrCalculus()

        self.defineTernaryQsrCalculus()

    # define binary QSR calculus
    def defineBinaryQsrCalculus(self):
        if self.binary_qsr_choice == 0:
            self.binary_qsr_dict = {
                'left': 0,
                'right': 1
            }

        elif self.binary_qsr_choice == 1:
            self.binary_qsr_dict = {
                'front': 0,
                'back': 1
            }

        elif self.binary_qsr_choice == 2:
            self.binary_qsr_dict = {
                'left': 0,
                'right': 1,
                'front': 2,
                'back': 3
            }

        elif self.binary_qsr_choice == 3:
            self.binary_qsr_dict = {
                'left/front': 0,
                'right/front': 1,
                'left/back': 2,
                'right/back': 3
            }

        # used for deriving NLP annotations
        self.binary_qsr_dict_inv = {v: k for k, v in self.binary_qsr_dict.items()}

    # get binary QSR value
    def getBinaryQsrValue(self, angle):
        value = ''    

        if self.binary_qsr_choice == 0:
            if -self.PI/2 <= angle < self.PI/2:
                value += 'right'
            elif self.PI/2 <= angle < self.PI or -self.PI <= angle < -self.PI/2:
                value += 'left'

        if self.binary_qsr_choice == 1:
            if 0 <= angle < self.PI:
                value += 'front'
            elif - self.PI <= angle < 0:
                value += 'back'

        elif self.binary_qsr_choice == 2:
            if 3*self.PI/4 <= angle < self.PI or -self.PI <= angle < -3*self.PI/4:
                value += 'left'
            elif -self.PI/4 <= angle < self.PI/4:
                value += 'right'
            elif self.PI/4 <= angle < 3*self.PI/4:
                value += 'front'
            elif -3*self.PI/4 <= angle < -self.PI/4:
                value += 'back'

        elif self.binary_qsr_choice == 3:
            if 0 <= angle < self.PI/2:
                value += 'left/front'
            elif self.PI/2 <= angle <= self.PI:
                value += 'left/back'
            elif -self.PI/2 <= angle < 0:
                value += 'right/front'
            elif -self.PI <= angle < -self.PI/2:
                value += 'right/back'

        return value

    # define ternary QSR calculus
    def defineTernaryQsrCalculus(self):
        if self.ternary_qsr_choice == 0:
            self.ternary_qsr_dict = {
                'left': 0,
                'right': 1
            }

        if self.ternary_qsr_choice == 1:
            self.ternary_qsr_dict = {
                'front': 0,
                'back': 1
            }

        elif self.ternary_qsr_choice == 2:
            self.ternary_qsr_dict = {
                'left': 0,
                'right': 1,
                'front': 2,
                'back': 3
            }

        elif self.ternary_qsr_choice == 3:
            self.ternary_qsr_dict = {
                'left/front': 0,
                'right/front': 1,
                'left/back': 2,
                'right/back': 3
            }

        elif self.ternary_qsr_choice == 4:
            self.ternary_qsr_dict = {
                'cl': 0,
                'dl': 1,
                'cr': 2,
                'dr': 3,
                'cb': 4,
                'db': 5,
                'cf': 6,
                'df': 7
                }

        # used for deriving NLP annotations
        self.ternary_qsr_dict_inv = {v: k for k, v in self.ternary_qsr_dict.items()}

    # get ternary QSR value
    def getTernaryQsrValue(self, r, angle, R):
        value = ''    

        if self.ternary_qsr_choice == 0:
            if -self.PI <= angle < 0:
                value += 'right'
            else:
                value += 'left'

        
        elif self.ternary_qsr_choice == 1:
            if -self.PI/2 <= angle < self.PI/2:
                value += 'front'
            else:
                value += 'back'

        elif self.ternary_qsr_choice == 2:
            if -self.PI/4 <= angle <= self.PI/4:
                value += 'front'
            elif self.PI/4 < angle < 3*self.PI/4:
                value += 'left'
            elif 3*self.PI/4 <= angle or angle <= -3*self.PI/4:
                value += 'back'
            elif -3*self.PI/4 < angle < -self.PI/4:
                value += 'right'     

        elif self.ternary_qsr_choice == 3:
            if 0 <= angle < self.PI/2:
                value += 'left/front'
            elif self.PI/2 <= angle <= self.PI:
                value += 'left/back'
            elif -self.PI/2 <= angle < 0:
                value += 'right/front'
            elif -self.PI <= angle < -self.PI/2:
                value += 'right/back'

        elif self.ternary_qsr_choice == 4:
            if r<=R:
                value += 'c'
            else:
                value += 'd'

            if -self.PI/4 <= angle <= self.PI/4:
                value += 'front'
            elif self.PI/4 < angle < 3*self.PI/4:
                value += 'left'
            elif 3*self.PI/4 <= angle or angle <= -3*self.PI/4:
                value += 'back'
            elif -3*self.PI/4 < angle < -self.PI/4:
                value += 'right' 

        return value