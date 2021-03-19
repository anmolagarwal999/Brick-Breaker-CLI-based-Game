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

    tot_breakable_bricks=0 # keeps track of bricks let to destroy

    def __init__(self,r_num,c_num,seq_id,sum_id,power_factor, is_rainbow=False):
        self._len_c=3
        self._len_r=1 
        self._left_r= r_num 
        self._left_c=c_num 
        self._seq_id=seq_id
        self._sum_id=sum_id
        self._isVisible=True
        self.score_bounty=conf.SCORE_BRICK_DESTROYED[power_factor]
        self.power_factor=1 if power_factor==5 else power_factor
        # self.ascii_repr=np.array([
        #     ['[','T',']']
        # ])

        self.is_brick_rainbow=is_rainbow

        if not is_rainbow:
            self._ascii_repr=np.array([
                ['[',str(power_factor),']']
            ])
        else:
            self._ascii_repr=np.array([
                ['[','R',']']
            ])


    def get_unlucky_friends(self):
        return []

    def move_brick(self, dy):
        self._left_r+=dy
    
    @property
    def ascii_repr(self):
        return self._ascii_repr
    
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
    def isVisible(self):
        return self._isVisible

    # @property
    # def score_bounty(self):
    #     return self._score_bounty

    @property
    def seq_id(self):
        return self._seq_id

    @isVisible.setter
    def isVisible(self, new_val):
        self._isVisible=new_val

    # @property
    # def power_factor(self):
    #     return self.power_factor     
   
        
class UnbreakableBrick(BricksClass):
    
    def __init__(self,r_num,c_num,seq_id,sum_id,power_factor):

        super().__init__(r_num,c_num,seq_id,sum_id,power_factor)        
        # self.ascii_repr=np.array([
        #     ['[',str(power_factor),']']
        # ])
        #logging.info(f"Inside init() of Bricks class with attributes\n{self.__dict__}\n")

    def damage(self,forced=False):
        if forced:
            self.power_factor=0
            self._isVisible=False
            return True
        return False

  
class NormalBrick(BricksClass):
    
    def __init__(self,r_num,c_num,seq_id,sum_id,power_factor):

        super().__init__(r_num,c_num,seq_id,sum_id,power_factor)        
        BricksClass.tot_breakable_bricks+=1

    
    def damage(self,forced=False):
        self.power_factor-=1
        if forced:
            # Through ball present 
            self.power_factor=0

        logging.info(f"Brick trying to break has stuff like {self.__dict__}")        
        if self.power_factor==0:
            self._isVisible=False
            BricksClass.tot_breakable_bricks-=1
            return True
        return False
 

class ExplosiveBrick(BricksClass):
    
    def __init__(self,r_num,c_num,seq_id,sum_id,power_factor):

        super().__init__(r_num,c_num,seq_id,sum_id,5)     
        BricksClass.tot_breakable_bricks+=1
    
    def damage(self,forced=True):
        self.power_factor=0
        logging.info(f"EXPLOSIVE BROKEN with {self.__dict__}")
        self._isVisible=False
        BricksClass.tot_breakable_bricks-=1
        return True

    def get_unlucky_friends(self):
        coordinates=[]        
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                if not (dx==0 and dy==0):
                    coordinates.append([self.left_r+dx,self.seq_id+dy])
        logging.critical(f"coordinates are {coordinates}")
        return coordinates

class RainbowBrick(BricksClass):
    
    def __init__(self,r_num,c_num,seq_id,sum_id,power_factor):
        self.contact_made_yet=False
        super().__init__(r_num,c_num,seq_id,sum_id,power_factor, True)        
        BricksClass.tot_breakable_bricks+=1

    def update_power_factor(self,new_factor):
        if self.contact_made_yet:
            return
        self.score_bounty=conf.SCORE_BRICK_DESTROYED[new_factor]
        self.power_factor=new_factor
     
    def damage(self,forced=False):
        self.power_factor-=1
        self.contact_made_yet=True
        if forced:
            # Through ball present 
            self.power_factor=0

        logging.info(f"Brick trying to break has stuff like {self.__dict__}")        
        if self.power_factor==0:
            self._isVisible=False
            BricksClass.tot_breakable_bricks-=1
            return True
        return False
 

   
