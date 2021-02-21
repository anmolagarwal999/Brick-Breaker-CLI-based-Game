import numpy as np
from ball_class import BallClass
import config as conf
import sys
from time import monotonic as clock, sleep
###############################################################
import logging
def part():
    logging.debug("----------------------------------------")
logging.basicConfig(filename='test.log',
                    level=logging.DEBUG,
                    filemode='w',
                    format='%(levelname)s:%(message)s')
##############################################################

class PowerupsClass:

    tot_active_powerups=0

    def __init__(self,r_num,c_num,powerup_symbol):
        self._len_c=1
        self._len_r=1 
        self._left_r= r_num 
        self._left_c=c_num
        self._status="in_air" # in_air,active, inactive
        self._vel_r=-1
        self._ascii_repr=np.array([
            [powerup_symbol]
        ])
        logging.info(f"Inside init() of POWERUPS class with attributes\n{self.__dict__}\n")

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

    def deactivate_powerup(self, game_obj):
        PowerupsClass.tot_active_powerups-=1
        logging.debug("Deactivation is redundant for this powerup")

    def eliminate(self):
        self._status="inactive"

  
'''
1. Expand Paddle: Increases the size of the paddle by a certain amount.
2. Shrink Paddle: Reduce the size of the paddle by a certain amount but not completely.
3. Ball Multiplier: Each of the balls which are present will be further divided into two.
4. Fast Ball: Increases the speed of the ball.
5. Thru-ball: This enables the ball to destroy and go through any brick it touches, irrespective of the
strength of the wall.(Even the unbreakable ones which you couldn’t previously destroy)
6. Paddle Grab:Allows the paddle to grab the ball on contact and relaunch the ball at will. The ball will
follow the same expected trajectory after release, similar to the movement expected without the grab.
'''

class ExpandPaddle(PowerupsClass):
    
    increment_val=4

    def __init__(self,r_num,c_num):
        super().__init__(r_num,c_num,"+")
        
        logging.info(f"Inside init() of POWERUPS class with attributes\n{self.__dict__}\n")

    def activate_powerup(self, game_obj):
        self._status="active"
        PowerupsClass.tot_active_powerups+=1
        self.activate_time=clock()
        self.had_impact_on_paddle=game_obj.game_paddle.increase_paddle_size(game_obj.just_game_cols,ExpandPaddle.increment_val)
        return True

    def deactivate_powerup(self, game_obj):
        PowerupsClass.tot_active_powerups-=1

        if self.had_impact_on_paddle:
            game_obj.game_paddle.decrease_paddle_size(ExpandPaddle.increment_val)


class ShrinkPaddle(PowerupsClass):
    decrement_val=4

    def __init__(self,r_num,c_num):
        super().__init__(r_num,c_num,"?")
        
        logging.info(f"Inside init() of POWERUPS class with attributes\n{self.__dict__}\n")

    def activate_powerup(self, game_obj):
        self._status="active"
        PowerupsClass.tot_active_powerups+=1
        self.activate_time=clock()
        self.had_impact_on_paddle=game_obj.game_paddle.decrease_paddle_size(ShrinkPaddle.decrement_val)
        return True

    def deactivate_powerup(self, game_obj):
        logging.info("")
        PowerupsClass.tot_active_powerups-=1

        if self.had_impact_on_paddle:
            game_obj.game_paddle.increase_paddle_size(game_obj.just_game_cols,ShrinkPaddle.decrement_val)

class FastBall(PowerupsClass):
    
    def __init__(self,r_num,c_num):
        super().__init__(r_num,c_num,"&")
        
        logging.info(f"Inside init() of POWERUPS class with attributes\n{self.__dict__}\n")

    def activate_powerup(self, game_obj):
        self.activate_time=clock()
        PowerupsClass.tot_active_powerups+=1
        self._status="active"
        self.affected_balls=[]

        # Store only those balls which were there during the time when this powerup hit the paddle
        for ball_obj in game_obj.balls_list:
            if ball_obj.boost_velocity(1):
                self.affected_balls.append(ball_obj)
        return True

    def deactivate_powerup(self, game_obj):
        # TAKE CARE OF THIS, you might decrease speed of ball which was not even born when this powerup was activated
        PowerupsClass.tot_active_powerups-=1
        
        for ball_obj in self.affected_balls:
            ball_obj.deboost_velocity(1)


class ThruBall(PowerupsClass):

    cnt=0    
    def __init__(self,r_num,c_num):
        super().__init__(r_num,c_num,"@")
        
        logging.info(f"Inside init() of POWERUPS class with attributes\n{self.__dict__}\n")

    def activate_powerup(self, game_obj):
        self.activate_time=clock()
        self._status="active"
        PowerupsClass.tot_active_powerups+=1
        ThruBall.cnt+=1
        for ball_obj in game_obj.balls_list:
            ball_obj.is_boss_cnt+=1

    def deactivate_powerup(self, game_obj):
        # TAKE CARE OF THIS, you might decrease speed of ball which was not even born when this powerup was activated
        ThruBall.cnt-=1
        PowerupsClass.tot_active_powerups-=1

        for ball_obj in game_obj.balls_list:
            ball_obj.is_boss_cnt-=1
   
class PaddleGrab(PowerupsClass):
    cnt=0
    
    def __init__(self,r_num,c_num):
        super().__init__(r_num,c_num,"$")
        
        logging.info(f"Inside init() of POWERUPS class with attributes\n{self.__dict__}\n")

    def activate_powerup(self, game_obj):
        self.activate_time=clock()+5
        self._status="active"
        PowerupsClass.tot_active_powerups+=1
        PaddleGrab.cnt+=1
        game_obj.game_paddle.magnetize()

    def deactivate_powerup(self, game_obj):
        PaddleGrab.cnt-=1
        PowerupsClass.tot_active_powerups-=1
        game_obj.game_paddle.demagnetize()


class BallMultiplier(PowerupsClass):
    
    def __init__(self,r_num,c_num):
        super().__init__(r_num,c_num,"%")
        
        logging.info(f"Inside init() of POWERUPS class with attributes\n{self.__dict__}\n")

    def activate_powerup(self, game_obj):
        self.activate_time=clock()
        PowerupsClass.tot_active_powerups+=1
        self._status="active"
        logging.info(f"Activation of BallMultiplier with length as {len(game_obj.balls_list)}")
        if len(game_obj.balls_list)==0:
            sys.exit('Number of balls is ZERO here, so duplication isn\'t possible')
            pass

        backup_list=game_obj.balls_list.copy()
        for demo_ball in backup_list:            
            # 
            new_ball=BallClass(demo_ball.left_c, demo_ball.left_r, demo_ball.is_stuck,demo_ball.vel_r,-demo_ball.vel_c)
            logging.info("New ball appended")
            game_obj.balls_list.append(new_ball)
        return True

