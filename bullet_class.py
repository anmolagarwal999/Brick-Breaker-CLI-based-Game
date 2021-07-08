import numpy as np
import math
from time import monotonic as clock, sleep
import config as conf

###############################################################
import logging
def part():
    logging.debug("----------------------------------------")
logging.basicConfig(filename='test.log',
                    level=logging.DEBUG,
                    filemode='w',
                    format='%(levelname)s:%(message)s')
##############################################################


class BulletClass:
    def __init__(self, wanted_left_c, wanted_left_r,
                 wanted_vel_r):

        self._len_c = 1
        self._len_r = 1
        self._left_c = wanted_left_c 
        self._left_r = wanted_left_r  
        self._isVisible = True
        self._vel_r = wanted_vel_r  
        self._vel_c = 0
        self.bullet_last_tended_v = clock()

        self.ascii_repr = np.array([['*']])
        logging.info(
            f"Inside init() of BULLET class with attributes\n{self.__dict__}\n")

    @property
    def left_c(self):
        return self._left_c

    @property
    def left_r(self):
        return self._left_r

    @property
    def len_c(self):
        return self._len_c

    @property
    def len_r(self):
        return self._len_r
    
    @property
    def vel_c(self):
        return self._vel_c

    @property
    def vel_r(self):
        return self._vel_r


    @property
    def isVisible(self):
        return self._isVisible    

    def get_vertical_prediction(self):        
        prob_r = self._left_r + self._vel_r
        return prob_r

    def move_vertically(self):      
        self._left_r +=self._vel_r
        # logging.critical(f"Vertical row of BULLET is {self._left_r}")

   
