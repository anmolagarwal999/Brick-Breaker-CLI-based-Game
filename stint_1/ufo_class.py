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
        self.left_r=18

        logging.info(f"Inside init() of UFO class with attributes\n{self.__dict__}\n")

    

        

        




