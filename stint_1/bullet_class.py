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

    # def get_horizontal_prediction(self):
    #     # move only if unstuck
    #     #logging.info("horizontal prediction called")
    #     if self._is_stuck == True:
    #         #logging.info(f"Returning {self._left_c}")
    #         return self._left_c
    #     vel_sign = 0
    #     if self._vel_c != 0:
    #         vel_sign = 1 if (self._vel_c > 0) else -1
    #     prob_c = self._left_c + vel_sign
    #     #logging.info(f"Returning {prob_c}")
    #     return prob_c

    # def move_horizontally(self):
    #     # move only if unstuck
    #     if self._is_stuck == True:
    #         return
    #     vel_sign = 0
    #     if self._vel_c != 0:
    #         vel_sign = 1 if (self._vel_c > 0) else -1
    #     self._left_c += vel_sign

    # def flip_horizontal_velocity(self):
    #     self._vel_c *= -1

    def get_vertical_prediction(self):
        # move only if unstuck
        #logging.info("vertical prediction called")
        # if self._is_stuck == True:
        #     #logging.info(f"Returning {self._left_r}")
        #     return self._left_r
        # vel_sign = 0
        # if self._vel_r != 0:
        #     vel_sign = 1 if (self._vel_r > 0) else -1
        prob_r = self._left_r + self._vel_r
        #logging.info(f"Returning {prob_r}")
        return prob_r

    def move_vertically(self):      
        self._left_r +=self._vel_r
        logging.critical(f"Vertical row of BULLET is {self._left_r}")

    # def flip_vertical_velocity(self):
    #     logging.critical("Vertical velocity FLIPPED")
    #     self._vel_r *= -1

    # def impact_velocity(self,dv):
    #     self._vel_c+=dv
    
    # def boost_velocity(self,dv, influence_vertical=False):        
    #     if self._vel_c>0:
    #         self._vel_c+=abs(dv)
    #     elif self._vel_c<0:
    #         self._vel_c-=abs(dv)
    #     else:
    #         # no change
    #         return False

    #     if influence_vertical==True:
    #         if self._vel_r>=0:
    #             self._vel_r+=abs(dv)
    #         else:
    #             self._vel_r-=abs(dv)

    #     return True
        
    # def deboost_velocity(self,dv,influence_vertical=False):   
    #     if self._vel_c>0:
    #         self._vel_c-=abs(dv)
    #     elif self._vel_c<0:
    #         self._vel_c+=abs(dv)
    #     else:
    #         # no change
    #         pass

    #     if influence_vertical==True:
    #         if self._vel_r>=0:
    #             self._vel_r-=abs(dv)
    #         else:
    #             self._vel_r+=abs(dv)

        

    # def get_ball_speed_magnitude(self):
    #     ans = math.sqrt(self._vel_r * self._vel_r + self._vel_c * self._vel_c)
    #     return ans
