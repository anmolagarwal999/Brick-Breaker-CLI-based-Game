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

class PaddleClass:

    def __init__(self, paddle_center_c):
        # center_c=paddle_center_c
        self._len_c=conf.DEFAULT_PADDLE_LEN
        self._len_r=1
        self._left_c=paddle_center_c-self._len_c//2
        self._left_r=0
        self._is_magnet=0
        self._is_armed=0
        self._ascii_repr=self.get_ascii_rep_str(self._len_c)
        logging.info(f"Inside init() of paddle class with attributes\n{self.__dict__}\n")

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
    def ascii_repr(self):
        return self._ascii_repr


    #######################################
    @property
    def is_magnet(self):
        return self._is_magnet
    def magnetize(self):
        self._is_magnet+=1
    def demagnetize(self):
        self._is_magnet-=1
    ##################################

    #######################################
    @property
    def is_armed(self):
        return self._is_armed
    def arm(self):
        self._is_armed+=1
        # Taking care if this is 
        self.manipulate_ascii_rep_str()
        

    def dearm(self):
        self._is_armed-=1
        self.manipulate_ascii_rep_str()
    ##################################

    def manipulate_ascii_rep_str(self):
        if self._is_armed>0:
            self._ascii_repr[0][0]="^"
            self._ascii_repr[0][-1]="^"
        else:
            self._ascii_repr[0][0]="["
            self._ascii_repr[0][-1]="]"



    def change_x(self,dx,right_limit):
        dx*=4
        curr_left_c=self._left_c
        curr_right_x=curr_left_c+self._len_c-1
        curr_left_c+=dx
        curr_right_x+=dx
        logging.info(f"Curr left x is {curr_left_c}")
        logging.info(f"Curr right x is {curr_right_x}")
        if curr_left_c>=0 and curr_right_x<right_limit:
            self._left_c+=dx
        elif curr_left_c<0:
            self._left_c=0
        else:
            self._left_c=right_limit-self._len_c
            logging.info(f"My details are {self.__dict__}\nRight limit is {right_limit}")

        return [self._left_c, self._len_c]
        
    
    def get_ascii_rep_str(self,wanted_len):
        arr=['[']
        for i in range(0,wanted_len-2):
            arr.append("-")
        arr.append(']')

        if self._is_armed>0:
            arr[0]='^'
            arr[-1]='^'
        return np.array([
            arr
        ])
        

    def increase_paddle_size(self,tot_width,inc_val):
        # aim to increase by 2 on each size
        logging.debug("Inside increase paddle size")
        exp_len=self._len_c+inc_val
        if exp_len>conf.MAX_PADDLE_LEN:
            return False
        self._len_c+=inc_val
        self._left_c=max(0,self._left_c-inc_val//2)

        # Imperative check: imagine scenario where cannot move +1 as right is blocked by wall, divert entire extension to left
        if self._left_c+self._len_c>=tot_width:
            self._left_c-=1+self._left_c+self._len_c-tot_width
        self._ascii_repr=self.get_ascii_rep_str(self._len_c)
        logging.info(f"Length set is {self._len_c}, length actual is {self.ascii_repr.shape}")
        return True

    
    # def restore_paddle_size(self):
    #     logging.debug("Inside RESTORE paddle size")
    #     self._len_c=conf.DEFAULT_PADDLE_LEN
    #     self._left_c=self._left_c+2
    #     elf.ascii_repr=self.get_ascii_rep_str(self._len_c)
    #     logging.info(f"Length set is {self._len_c}, length actual is {self.ascii_repr.shape}")
    
    def decrease_paddle_size(self,dec_val):
        logging.debug("Inside DECREASE paddle size")
        exp_len=self._len_c-dec_val
        if exp_len<conf.MIN_PADDLE_LEN:
            return False
        self._len_c=exp_len
        self._left_c=self._left_c+dec_val//2
        self._ascii_repr=self.get_ascii_rep_str(self._len_c)
        logging.info(f"Length set is {self._len_c}, length actual is {self.ascii_repr.shape}")
        return True

        

        




