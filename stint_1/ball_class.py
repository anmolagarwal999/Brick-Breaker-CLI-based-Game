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


class BallClass:
    def __init__(self, wanted_left_c, wanted_left_r, wanted_is_stuck,
                 wanted_vel_r, wanted_vel_c):

        self.len_c = 1
        self.len_r = 1
        #self.left_c=self.center_c-self.len_c//2
        self._left_c = wanted_left_c  # let's make this the center column of the paddle for now
        self._left_r = wanted_left_r  # row number will be 1
        self._is_stuck = wanted_is_stuck
        self.offset_from_center = 0
        self.isVisible = True
        self._vel_r = wanted_vel_r  # vertical vel is 1
        self._vel_c = wanted_vel_c  # horizontal vel is zero
        self.is_boss = False
        self.ball_last_tended = clock()
        self.ascii_repr = np.array([['O']])
        logging.info(
            f"Inside init() of BALL class with attributes\n{self.__dict__}\n")

    @property
    def left_c(self):
        return self._left_c

    @property
    def left_r(self):
        return self._left_r
    
    @property
    def vel_c(self):
        return self._vel_c

    @property
    def vel_r(self):
        return self._vel_r

    @property
    def is_stuck(self):
        return self._is_stuck

    def release(self):
        self._is_stuck=False
    
    def follow_paddle(self, paddle_center):
        self._left_c=paddle_center+self.offset_from_center


    def get_horizontal_prediction(self):
        # move only if unstuck
        logging.info("horizontal prediction called")
        if self._is_stuck == True:
            logging.info(f"Returning {self._left_c}")
            return self._left_c
        vel_sign = 0
        if self._vel_c != 0:
            vel_sign = 1 if (self._vel_c > 0) else -1
        prob_c = self._left_c + vel_sign
        logging.info(f"Returning {prob_c}")
        return prob_c

    def move_horizontally(self):
        # move only if unstuck
        if self._is_stuck == True:
            return
        vel_sign = 0
        if self._vel_c != 0:
            vel_sign = 1 if (self._vel_c > 0) else -1
        self._left_c += vel_sign

    def flip_horizontal_velocity(self):
        self._vel_c *= -1

    def get_vertical_prediction(self):
        # move only if unstuck
        logging.info("vertical prediction called")
        if self._is_stuck == True:
            logging.info(f"Returning {self._left_r}")
            return self._left_r
        vel_sign = 0
        if self._vel_r != 0:
            vel_sign = 1 if (self._vel_r > 0) else -1
        prob_r = self._left_r + vel_sign
        logging.info(f"Returning {prob_r}")
        return prob_r

    def move_vertically(self):
        # move only if unstuck
        if self._is_stuck == True:
            return
        vel_sign = 0
        if self._vel_r != 0:
            vel_sign = 1 if (self._vel_r > 0) else -1
        self._left_r += vel_sign

    def flip_vertical_velocity(self):
        self._vel_r *= -1

    def impact_velocity(self,dv):
        self._vel_c+=dv

    def get_ball_speed_magnitude(self):
        ans = math.sqrt(self._vel_r * self._vel_r + self._vel_c * self._vel_c)
        return ans
