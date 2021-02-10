import numpy as np
from ball_class import BallClass
import config as conf
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

    def __init__(self,r_num,c_num,powerup_symbol):
        self.len_c=1
        self.len_r=1 
        self.left_r= r_num 
        self.left_c=c_num
        self.status="in_air" # in_air,active, inactive
        self.vel_r=-1
        self.ascii_repr=np.array([
            [powerup_symbol]
        ])
        logging.info(f"Inside init() of POWERUPS class with attributes\n{self.__dict__}\n")


    def deactivate_powerup(self, game_obj):
        logging.debug("Deactivation is redundant for this powerup")

  
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
        self.activate_time=clock()
        self.had_impact_on_paddle=game_obj.game_paddle.increase_paddle_size(game_obj.just_game_cols,ExpandPaddle.increment_val)

    def deactivate_powerup(self, game_obj):
        if self.had_impact_on_paddle:
            game_obj.game_paddle.decrease_paddle_size(ExpandPaddle.increment_val)


class ShrinkPaddle(PowerupsClass):
    decrement_val=4

    def __init__(self,r_num,c_num):
        super().__init__(r_num,c_num,"?")
        
        logging.info(f"Inside init() of POWERUPS class with attributes\n{self.__dict__}\n")

    def activate_powerup(self, game_obj):
        self.activate_time=clock()
        self.had_impact_on_paddle=game_obj.game_paddle.decrease_paddle_size(ShrinkPaddle.decrement_val)

    def deactivate_powerup(self, game_obj):
        logging.info("")
        if self.had_impact_on_paddle:
            game_obj.game_paddle.increase_paddle_size(game_obj.just_game_cols,ShrinkPaddle.decrement_val)

class FastBall(PowerupsClass):
    
    def __init__(self,r_num,c_num):
        super().__init__(r_num,c_num,"&")
        
        logging.info(f"Inside init() of POWERUPS class with attributes\n{self.__dict__}\n")

    def activate_powerup(self, game_obj):
        self.activate_time=clock()
        self.affected_balls=[]
        for ball_obj in game_obj.balls_list:
            self.affected_balls.append(ball_obj)
            ball_obj.vel_r+=1 if ball_obj.vel_r>0 else -1

    def deactivate_powerup(self, game_obj):
        # TAKE CARE OF THIS, you might decrease speed of ball which was not even born when this powerup was activated
        
        for ball_obj in self.affected_balls:
            ball_obj.vel_r-=1 if ball_obj.vel_r>0 else -1

class ThruBall(PowerupsClass):
    
    def __init__(self,r_num,c_num):
        super().__init__(r_num,c_num,"@")
        
        logging.info(f"Inside init() of POWERUPS class with attributes\n{self.__dict__}\n")

    def activate_powerup(self, game_obj):
        self.activate_time=clock()
        for ball_obj in game_obj.balls_list:
            ball_obj.is_boss=True

    def deactivate_powerup(self, game_obj):
        # TAKE CARE OF THIS, you might decrease speed of ball which was not even born when this powerup was activated
        for ball_obj in game_obj.balls_list:
            ball_obj.is_boss=False
   
class PaddleGrab(PowerupsClass):
    
    def __init__(self,r_num,c_num):
        super().__init__(r_num,c_num,"$")
        
        logging.info(f"Inside init() of POWERUPS class with attributes\n{self.__dict__}\n")

    def activate_powerup(self, game_obj):
        self.activate_time=clock()+5
        game_obj.game_paddle.is_magnet=True

    def deactivate_powerup(self, game_obj):
        game_obj.game_paddle.is_magnet=False

class BallMultiplier(PowerupsClass):
    
    def __init__(self,r_num,c_num):
        super().__init__(r_num,c_num,"%")
        
        logging.info(f"Inside init() of POWERUPS class with attributes\n{self.__dict__}\n")

    def activate_powerup(self, game_obj):
        self.activate_time=clock()
        if len(game_obj.balls_list)==0:
            sys.exit('Number of balls is ZERO here, so duplication isn\'t possible')

        backup_list=game_obj.balls_list.copy()
        for demo_ball in backup_list:            
            new_ball=BallClass(demo_ball.left_c, demo_ball.left_r, demo_ball.is_stuck,demo_ball.vel_r,-demo_ball.vel_c)
            game_obj.balls_list.append(new_ball)


    # def deactivate_powerup(self, game_obj):
    #     game_obj.game_paddle.is_magnet=False