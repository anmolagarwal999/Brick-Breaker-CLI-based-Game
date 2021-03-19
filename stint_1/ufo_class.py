import numpy as np
import random
import time
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

class UFOClass:

    def __init__(self, paddle_center_c):
        # center_c=paddle_center_c
       
       
        # self._ascii_repr=self.get_ascii_rep_str(self._len_c)
        self.ascii_repr = np.array([         
                     
            ['(','-','(','-','_','(','-','_','-',')','_','-',')','-',')'],
            ['(','-','(','-','_','(','-','_','-',')','_','-',')','-',')']             
            
            ])

        self.len_c=self.ascii_repr.shape[1]
        self.len_r=self.ascii_repr.shape[0]
        self.left_c=paddle_center_c-self.len_c//2
        self.left_r=20

        logging.info(f"Inside init() of UFO class with attributes\n{self.__dict__}\n")

    def chase_paddle(self,paddle_c,right_limit):
        # dx*=4
        # curr_center=self.left_c+self.len_c//2
        logging.info(f"Inside chasing paddle with col {paddle_c}")
        curr_left_c=paddle_c-self.len_c//2
        curr_right_x=curr_left_c+self.len_c-1
        
        logging.info(f"Curr left x is {curr_left_c}")
        logging.info(f"Curr right x is {curr_right_x}")
        if curr_left_c>=0 and curr_right_x<right_limit:
            self.left_c=curr_left_c
        elif curr_left_c<0:
            self.left_c=0
        else:
            self.left_c=right_limit-self.len_c
            logging.info(f"My details are {self.__dict__}\nRight limit is {right_limit}")

        return [self.left_c, self.len_c]

    

        




class BombClass:
    
    def __init__(self,r_num,c_num):
        self._len_c=1
        self._len_r=1 
        self._left_r= r_num 
        self._left_c=c_num
        self._status="in_air" # in_air,active, inactive
        self._vel_r=-1
        self._ascii_repr=np.array([
            ["Q"]
        ])
        logging.info(f"Inside init() of BOMB  class with attributes\n{self.__dict__}\n")

    @property
    def ascii_repr(self):
        return self._ascii_repr

    @property
    def status(self):
        return self._status

    @property
    def left_r(self):
        return self._left_r

    @property
    def left_c(self):
        return self._left_c
    
    @property
    def len_r(self):
        return self._len_r

    @property
    def len_c(self):
        return self._len_c

    def move(self):
        self._left_r += self._vel_r

    # def deactivate_powerup(self, game_obj):
    #     PowerupsClass.tot_active_powerups-=1
    #     logging.debug("Deactivation is redundant for this powerup")

    def eliminate(self):
        self._status="inactive"




