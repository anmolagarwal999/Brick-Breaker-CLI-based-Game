import numpy as np
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

class BricksClass:

    def __init__(self,r_num,c_num,seq_id,sum_id,power_factor):


        self.len_c=3
        self.len_r=1 
        #self.left_c=self.center_c-self.len_c//2
        self.left_r= r_num # let's make this the center column of the paddle for now
        self.left_c=c_num # row number will be 1
        self.seq_id=seq_id
        self.sum_id=sum_id
        self.isVisible=True
        self.score_bounty=conf.SCORE_BRICK_DESTROYED[power_factor]
        self.power_factor=power_factor
        self.ascii_repr=np.array([
            ['[',str(power_factor),']']
        ])
        #logging.info(f"Inside init() of Bricks class with attributes\n{self.__dict__}\n")

    def get_unlucky_friends(self):
        return []
        
class UnbreakableBrick(BricksClass):
    
    def __init__(self,r_num,c_num,seq_id,sum_id,power_factor):

        super().__init__(r_num,c_num,seq_id,sum_id,power_factor)        
        self.ascii_repr=np.array([
            ['[',str(power_factor),']']
        ])
        #logging.info(f"Inside init() of Bricks class with attributes\n{self.__dict__}\n")

    def damage(self,forced=False):
        if forced:
            self.power_factor=0
            self.isVisible=False
            return True
        return False

  
class NormalBrick(BricksClass):
    
    def __init__(self,r_num,c_num,seq_id,sum_id,power_factor):

        super().__init__(r_num,c_num,seq_id,sum_id,power_factor)        
        self.ascii_repr=np.array([
            ['[',str(power_factor),']']
        ])
    
    def damage(self,forced=False):
        self.power_factor-=1
        if forced:
            self.power_factor=0
        # logging.info(f"Brick trying to break has stuff like {self.__dict__}")
        
        if self.power_factor==0:
            self.isVisible=False
            return True
        return False
 

class ExplosiveBrick(BricksClass):
    
    def __init__(self,r_num,c_num,seq_id,sum_id,power_factor):

        super().__init__(r_num,c_num,seq_id,sum_id,1)       
        self.ascii_repr=np.array([
            ['[',str(power_factor),']']
        ])
        #logging.info(f"Inside init() of Bricks class with attributes\n{self.__dict__}\n")

    def get_unlucky_friends(self):
        coordinates=[]        
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                coordinates.append([self.left_r+dx,self.seq_id+dy])
        logging.critical(f"coordinates are {coordinates}")
        return coordinates
    
    def damage(self,forced=True):
        self.power_factor=0
        logging.info(f"UNBREAKABLE BROKEN with {self.__dict__}")
        self.isVisible=False
        return True

 

   
