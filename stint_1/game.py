import os
import sys
import time
import math, random
import numpy as np
import colorama
from colorama import Fore, Back, Style
colorama.init(autoreset=False)
import termios
from input_fd import InputHelper
from canvas import Canvas
import config as conf
import random
from time import monotonic as clock, sleep
from paddle import PaddleClass
from ball_class import BallClass
from bullet_class import BulletClass
from bricks_class import BricksClass, UnbreakableBrick, NormalBrick, ExplosiveBrick, RainbowBrick
from powerups import PowerupsClass, ExpandPaddle, ShrinkPaddle, FastBall, ThruBall, PaddleGrab, BallMultiplier, PaddleShoot

###############################################################
import logging

from ufo_class import UFOClass
from ufo_class import BombClass


# tail -f your.log
def part():
    logging.debug("----------------------------------------")


logging.basicConfig(filename='test.log',
                    level=logging.DEBUG,
                    filemode='w',
                    format='%(levelname)s:%(message)s')
##############################################################


class Game:

    # https://stackoverflow.com/a/56335
    RESET_CURSOR_ANSI = "\033[0;0H"

    # https://stackoverflow.com/a/1348624
    CLEAR_ANSI = "\033[2J"

    def __init__(self):
        # https://stackoverflow.com/a/943921
        rows, cols = os.popen('stty size', 'r').read().split()
        self._entire_screen_rows = int(rows)
        self._just_game_rows = int(rows) - conf.INFO_DOWN
        self._entire_screen_cols = int(cols)
        self.just_game_cols = int(cols) - conf.INFO_RIGHT
        self._info_box_height = self._entire_screen_rows - self._just_game_rows - 3

        ##################################################################
        logging.debug(f"rows are {rows}")
        logging.debug(f"columns are are {cols}")
        part()
        logging.debug(f"conf.min height is   {conf.MIN_HEIGHT}")
        logging.debug(f"conf.min width is   {conf.MIN_WIDTH}")
        part()
        logging.debug(f"conf.BUFFER DOWN IS is   {conf.INFO_DOWN}")
        logging.debug(f"conf.BUFFER RIGHT  is   {conf.INFO_RIGHT}")
        part()
        ##################################################################

        if self._just_game_rows < conf.MIN_HEIGHT or self.just_game_cols < conf.MIN_WIDTH:
            print(
                Fore.RED + Style.BRIGHT +
                'Error: Not enough TERMINAL SIZE. Resize window to a larger size'
            )
            sys.exit()

        self._screen = Canvas(self._just_game_rows, self.just_game_cols,
                              self._info_box_height)

        self._input_stream = InputHelper()

        #############################################################################

        self._score = 0
        self._lives_left = conf.TOT_LIVES
        self._overall_start_time = clock()
        self.curr_level = 3

        self.game_ufo=None

        # self._available_powerups=[ExpandPaddle, ShrinkPaddle, FastBall, ThruBall,BallMultiplier,PaddleGrab, PaddleShoot]
        self._available_powerups = [PaddleShoot]

        self.recent_bomb_time=clock()

        self.bricks_list = []
        self.curr_bullets_list = []
        self.init_new_level()
        self.curr_bombs_list=[]

        self.did_any_ball_hit_the_paddle = False

        ######################################################################

    def init_new_level(self):
        '''IMPLEMENT FUNCTION TO GENERATE NEW BRICK COORDINATES HERE'''
        self.level_start_time = clock()
        self.init_new_life()

        if self.curr_level==3:
            self.game_ufo=UFOClass(self.game_paddle.left_c+self.game_paddle.len_c//2)

        # The first display of the canvas
        BricksClass.tot_breakable_bricks = 0
        self.generate_brick_coordinates()
        self.paint_objs()
        self._screen.print_board()

        # The first painting on the canvas
        #print(f"{Style.BRIGHT}")

    def next_level(self):
        if self.curr_level == conf.TOT_LEVELS:
            self._score += conf.SCORE_LIFE_BONUS * self._lives_left
            self.game_over_screen(
                "Congrats! You broke all the breakable bricks OVER ALL LEVELS")
        else:
            self.curr_level += 1
            logging.info(f"slf curr level is {self.curr_level}")
            self.init_new_level()

    def init_new_life(self):
        '''Initializes values for the current life'''
        self.curr_powerups_list = []  # All powerups have to be removed

        # Reinit the powerup random list
        self.curr_powerup_idx = 0
        ThruBall.cnt = 0
        PaddleGrab.cnt = 0
        PaddleShoot.cnt = 0
        self.curr_bombs_list=[]
        # Making the game paddle
        self._game_paddle = PaddleClass(self.just_game_cols // 2)

        # A new game ball
        random_offset = random.randint(0, self._game_paddle.len_c - 1)
        offset_from_centre = (random_offset -
                              self._game_paddle.len_c // 2) // 2
        original_ball = BallClass(self._game_paddle.left_c + random_offset, 1,
                                  True, 1, offset_from_centre,
                                  offset_from_centre)
        self.balls_list = [original_ball]
        self.curr_bullets_list = []
        self.did_any_ball_hit_the_paddle = False

        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

    def paint_objs(self):
        '''Paints all the objects into CANVAS for the current iteration'''
        self._screen.clear_canvas()
        self._screen.add_entity(self._game_paddle.left_c, self._game_paddle.left_r, \
            self._game_paddle.len_c, self._game_paddle.len_r, self._game_paddle.ascii_repr,"")

        for this_ball in self.balls_list:
            assert (this_ball.isVisible == True)
            if this_ball.isVisible:
                self._screen.add_entity(this_ball.left_c, this_ball.left_r, \
                    this_ball.len_c, this_ball.len_r, this_ball.ascii_repr,conf.BG_COLOR)

        for brick in self.bricks_list:
            self._screen.add_brick(brick)

        for send_powerup in self.curr_powerups_list:
            if send_powerup.status == "in_air":
                self._screen.add_entity(send_powerup.left_c, send_powerup.left_r, send_powerup.len_c,\
                    send_powerup.len_r,send_powerup.ascii_repr, "")

        for send_bullet in self.curr_bullets_list:
            # if send_powerup.status == "in_air":
            self._screen.add_entity(send_bullet.left_c, send_bullet.left_r, send_bullet.len_c,\
                send_bullet.len_r,send_bullet.ascii_repr, "")

        if self.game_ufo is not None:
            self._screen.add_entity(self.game_ufo.left_c, self.game_ufo.left_r, self.game_ufo.len_c,\
                self.game_ufo.len_r,self.game_ufo.ascii_repr, "")

        for send_bomb in self.curr_bombs_list:
            if send_bomb.status == "in_air":
                self._screen.add_entity(send_bomb.left_c, send_bomb.left_r, send_bomb.len_c,\
                    send_bomb.len_r,send_bomb.ascii_repr, "")

        


    def get_time_left(self):
        '''Get time left'''
        time_elapsed = clock() - self._overall_start_time
        time_left = conf.TOT_TIME - time_elapsed
        return [round(time_elapsed, 1), round(time_left, 1)]

    def print_game_details(self):
        '''Printing of game stats'''
        # score, lives_left, time_left, current number of powerups activated
        string_up = Back.RED
        for i in range(0, self._info_box_height):
            string_up += "\033[F"
        print(string_up)

        # cnt = 0
        # for i in self.curr_powerups_list:
        #     if i.status == "active":
        #         cnt += 1
        # assert(cnt==PowerupsClass.tot_active_powerups)

        thru_ball_there = True if ThruBall.cnt > 0 else False
        paddle_grab_there = True if PaddleGrab.cnt > 0 else False

        # logging.info(f"Compare between {PaddleGrab.cnt} and {self._game_paddle.is_magnet}")
        # assert(PaddleGrab.cnt==self._game_paddle.is_magnet)
        #assert(BricksClass.tot_breakable_bricks==len(self.bricks_list))

        speeds_list = []
        for i in self.balls_list:
            speeds_list.append(f"{i.vel_r}:{i.vel_c}")
        time_stats = self.get_time_left()
        str_print = str(speeds_list)
        lim = min(15, len(str_print))
        str_print = str_print[:lim]
        print(f"Score now is {str(self._score).ljust(10)}", end='')
        print(f"Lives left  is {str(self._lives_left).ljust(4)}")
        # print(f"Balls Horizontal vel(INERTIA): {str_print}")
        print(f" Current level is :{self.curr_level}")
        print(
            f"Time elapsed:{str(time_stats[0]).ljust(4)} | Time left:{time_stats[1]}"
        )
        time_before_bricks_descend = conf.TIME_BEFORE_BRICKS_DESCEND - (
            clock() - self.level_start_time)
        print(f"Time before bricks descend is {time_before_bricks_descend}")
        # print(f"No of active powerups is {str(PowerupsClass.tot_active_powerups).ljust(3)}|", end='')
        #print(f"Paddle length is {str(self._game_paddle.len_c).ljust(4)}")
        print(f"No of breakable bricks:{BricksClass.tot_breakable_bricks}  ", end='')
        print(f"Shoot t left:{self.get_max_shooting_time_left()}")
        # print(f"ThruBall:{thru_ball_there} | PaddleGrab:{paddle_grab_there}")s
        print(Back.BLACK)

    def generate_brick_coordinates(self):
        '''Designing layout of bricks'''

        self.bricks_list = []

        if self.curr_level!=3:

            # rows go from 0 to tot_r-1 , start from 10, go till end-2
            # cols go from 0 to tot_c-1 , go from 5 to end-5
            first_code = 0
            for i in range(12, self._just_game_rows - 5):
                first_idx = (first_code - i)
                seq_in_row = 0
                for j in range(11, self.just_game_cols - 10, 3):
                    seq_in_row += 1
                    #logging.info(f"Coordinates are {i}:{j}")
                    color_code = ((first_idx + seq_in_row) % 6 + 6) % 6 + 1
                    #color_code=5
                    # if color_code == 4:
                    #     color_code = 2
                    # elif color_code == 2:
                    #     color_code = 4

                    if color_code == 1:
                        color_code = 4
                    elif color_code == 4:
                        color_code = 1
                    elif color_code == 2:
                        color_code = 6
                    elif color_code == 6:
                        color_code = 2

                    # if color_code==6:
                    #     color_code=2
                    #logging.critical(f"{seq_in_row-i}:{color_code}")
                    decided_class = NormalBrick
                    logging.info(f"Color code is {color_code}")
                    if color_code == 4:
                        decided_class = UnbreakableBrick
                    elif color_code == 5:
                        decided_class = ExplosiveBrick
                    elif color_code == 6:
                        decided_class = RainbowBrick
                        test_list = [1, 2, 3]
                        color_code = random.choice(test_list)
                    self.bricks_list.append(
                        decided_class(i, j, seq_in_row, (seq_in_row - i),
                                    color_code))
                #logging.critical("\n")
        else:

            self.bricks_list=[]
            # rows go from 0 to tot_r-1 , start from 10, go till end-2
            # cols go from 0 to tot_c-1 , go from 5 to end-5
            first_code = 0
            for i in range(6, self._just_game_rows - 12):
                first_idx = (first_code - i)
                seq_in_row = 0
                for j in range(11, self.just_game_cols - 10, 3):
                    seq_in_row += 1
                    #logging.info(f"Coordinates are {i}:{j}")
                    color_code = ((first_idx + seq_in_row) % 6 + 6) % 6 + 1
                    #color_code=5
                    # if color_code == 4:
                    #     color_code = 2
                    # elif color_code == 2:
                    #     color_code = 4

                    if color_code == 1:
                        color_code = 4
                    elif color_code == 4:
                        color_code = 1
                    elif color_code == 2:
                        color_code = 6
                    elif color_code == 6:
                        color_code = 2
                    if color_code==4:
                    # if color_code==6:
                    #     color_code=2
                    #logging.critical(f"{seq_in_row-i}:{color_code}")
                        decided_class = NormalBrick
                        logging.info(f"Color code is {color_code}")
                        if color_code == 4:
                            decided_class = UnbreakableBrick
                        elif color_code == 5:
                            decided_class = ExplosiveBrick
                        elif color_code == 6:
                            decided_class = RainbowBrick
                            test_list = [1, 2, 3]
                            color_code = random.choice(test_list)
                        self.bricks_list.append(
                            decided_class(i, j, seq_in_row, (seq_in_row - i),
                                        color_code))
                #logging.critical("\n")







    def produce_bullet(self):
        col_val = self.game_paddle.left_c + self.game_paddle.len_c // 2
        # col, row, vertical velocity
        new_bullet = BulletClass(col_val, 0, 1)
        self.curr_bullets_list.append(new_bullet)

    def handle_input(self):
        '''Handles paddle movement, Moves balls alongwith paddle if stuck, releases any stuck ball if 's' is pressed '''
        ret_val = False
        if self._input_stream.is_pending():
            inp = self._input_stream.get_pending_char()
            logging.info(f"\n[PRESSED {inp}]\n")
            paddle_new_details = None
            if inp == 'a':
                paddle_new_details = self._game_paddle.change_x(
                    -1, self.just_game_cols)
                # DEAL WITH CASE WHEN BALL IS STUCK ALSO
                ret_val = False
            elif inp == 'd':
                paddle_new_details = self._game_paddle.change_x(
                    1, self.just_game_cols)
                # DEAL WITH CASE WHEN BALL IS STUCK ALSO
                ret_val = False
            elif inp == 's':
                for this_ball in self.balls_list:
                    if this_ball.is_stuck == True:
                        this_ball.release()
                        ret_val = False
            elif inp == 'v':
                '''Bullet produced'''
                #check if powerup activated
                if self.game_paddle.is_armed>0:
                    self.produce_bullet()

            elif inp == 'b':
                logging.info("attempt to move to next level automatically")
                ret_val = True


            #################################################################################
            if paddle_new_details is not None:
                #############################
                for ball_obj in self.balls_list:
                    if ball_obj.is_stuck == True:
                        ball_obj.follow_paddle(paddle_new_details[0] +
                                               paddle_new_details[1] // 2)
                ###############################
                if self.game_ufo is not None:
                    self.game_ufo.chase_paddle(paddle_new_details[0] +
                                               paddle_new_details[1] // 2,  self.just_game_cols)
                ############################

            termios.tcflush(
                sys.stdin, termios.TCIOFLUSH
            )  # to prevent character accumulation in buffer coz  input rate might be faster than frame rate
        return ret_val

    def did_ball_collide_with_wall(self, prob_c, prob_r):
        '''Checks if ball collided with the ball'''
        '''Also, being used for bullet'''
        '''Also, being used for bullet'''
        '''Also, being used for bullet'''
        '''Also, being used for bullet'''
        #logging.critical(f"BALL WALL insvestigation is {prob_r}:{prob_c}")
        if prob_c < 0 or prob_c >= self.just_game_cols:
            return True
        if prob_r < -1 or prob_r >= self._just_game_rows:
            return True
        return False

    def game_over_screen(self, msg):
        '''Prints GAME OVER SCREEN'''
        logging.info(f"Inside game over with message {msg}")
        print(self.CLEAR_ANSI)
        print(self.RESET_CURSOR_ANSI)
        print(f"{Fore.GREEN}{Back.YELLOW}{Style.BRIGHT}")
        # print("Green Text - Yellow Background - Bright")
        # print("HELLO")
        print("GAME OVER".center(os.get_terminal_size().columns))
        print(f"{msg}".center(os.get_terminal_size().columns))
        print(f"Your score is {self._score}".center(
            os.get_terminal_size().columns))
        # time.sleep(10)
        sys.exit()
        #pass

    def did_ball_collide_with_paddle(self, prob_c, prob_r, ball_obj):
        '''Checks if the ball collided with the paddle, 
        Regulates speed
        and
        handles the sticky paddle case
        '''
        dc = prob_c - self._game_paddle.left_c
        if self._game_paddle.left_r == prob_r and (
                dc >= 0 and dc < self._game_paddle.len_c):
            speed_inc_dist = prob_c - (self._game_paddle.left_c +
                                       self._game_paddle.len_c // 2)
            logging.debug(f"speed inc is {speed_inc_dist}")
            ball_obj.impact_velocity(speed_inc_dist // 2)

            logging.info(f"Is paddle magnetic : {self._game_paddle.is_magnet}")
            if self._game_paddle.is_magnet > 0:
                ball_obj.capture()
                ball_obj.offset_from_center = prob_c - (
                    self._game_paddle.left_c + self._game_paddle.len_c // 2)

            ########################
            # collision => ball collided with paddle, move bricks appropriately
            self.did_any_ball_hit_the_paddle = True
            ########################
            return True
        return False

    def did_ball_collide_with_ufo(self, prob_c, prob_r):
        '''Checks if the ball collided with the ufo, 
        Regulates speed
        and
        handles the sticky paddle case
        '''

        if self.game_ufo is None:
            return False

        dc = prob_c - self.game_ufo.left_c

        ufo_height=self.game_ufo.len_r
        for offset in range(0, ufo_height):
            if self.game_ufo.left_r+offset == prob_r and (
                    dc >= 0 and dc < self.game_ufo.len_c):            
                return True
        return False

    def did_ball_collide_with_this_brick(self, prob_c, prob_r, brick_obj):
        '''Returns True if ball collided with THIS brick,false otherwise'''
        dc = prob_c - brick_obj.left_c
        if (brick_obj.left_r == prob_r and (dc >= 0 and dc < brick_obj.len_c)):
            return True
        return False

    @staticmethod
    def random_yes_or_no():
        rand_float = random.uniform(0, 1)
        logging.info(f"rand float is {rand_float}")
        if rand_float > 0.3:
            return True
        logging.info("Randomness says NO")
        return False

    def try_powerup_generation(self, prob_r, prob_c):

        if self.random_yes_or_no() is False:
            return

            ##########################
        self.curr_powerup_idx = (self.curr_powerup_idx + 1) % (len(
            self._available_powerups))

        # self.curr_powerup_idx = random.randint(0,len(self._available_powerups)-1)

        chosen_powerup_cls = self._available_powerups[self.curr_powerup_idx]

        new_powerup = chosen_powerup_cls(prob_r, prob_c)
        self.curr_powerups_list.append(new_powerup)
        logging.info("Powerup appended")

    @staticmethod
    def is_there(a, b, unlucky_arr):
        for i in unlucky_arr:
            if i[0] == a and i[1] == b:
                return True
        return False

    def hit_brick(self, brick_obj, is_forced, is_origin_brick=True):
        # Hit brick
        #logging.critical(f"Inside HIT brick function for {brick_obj.__dict__}")
        #assert (brick_obj.isVisible == True)
        if brick_obj.isVisible and brick_obj.damage(is_forced):
            # brick broken => take score of breaking this brick
            # if brick is still unbroken and is now broken, then
            self._score += brick_obj.score_bounty
            self._screen.finish_brick(brick_obj)
            self.bricks_list.remove(brick_obj)

            if is_origin_brick:
                # generate powerup with probability only if the brick is the first one to be broken
                self.try_powerup_generation(brick_obj.left_r, brick_obj.left_c)

            unlucky_neighbors = brick_obj.get_unlucky_friends()

            # A sad_brick is surely due to explosion

            chosen_ones = []
            for sad_brick in self.bricks_list:
                # if sad_brick.left_r==15 and sad_brick.seq_id==11 and brick_obj.left_r==16 and brick_obj.left_c==10:
                #     #logging.info("voila")
                #     pass
                if self.is_there(sad_brick.left_r, sad_brick.seq_id,
                                 unlucky_neighbors):
                    #logging.info(f"Sad brick credentials are {sad_brick.__dict__}\n")

                    # this brick will be a part of DFS NOW
                    chosen_ones.append(sad_brick)
                else:
                    #logging.info(f"UNSad brick credentials are {sad_brick.__dict__}\n")
                    pass

            for i in chosen_ones:
                self.hit_brick(i, True, False)

    def did_ball_collide_with_bricks(self, prob_c, prob_r, ball_obj):
        '''Returns true if collided with a brick and false otherwise, 
        The true/false helps determine whether to flip ball's velocity or not.
        '''
        # invariant= only active bricks present in bricks_list
        bricks_checklist = self.bricks_list.copy()
        for a_brick in bricks_checklist:
            # # proceed only if brick is still visible

            if self.did_ball_collide_with_this_brick(prob_c, prob_r, a_brick):
                self.hit_brick(a_brick, (ball_obj.is_boss_cnt > 0))
                return True
        return False

    def move_ball_horizontally(self, ball_obj):

        # getter implemented in ball class, left_c and left_r are private variables
        prob_c = ball_obj.get_horizontal_prediction()
        prob_r = ball_obj.left_r  # ball is not moving horizontally in this case

        if ball_obj.left_c == prob_c:
            return  # ball did not move => no need to check

        ########### Collision with wall ##########################
        if self.did_ball_collide_with_wall(prob_c, prob_r):
            #logging.debug("Collision with wall")
            # Collision while moving horizontally => can be the left, right walls only and not the top wall
            ball_obj.flip_horizontal_velocity()
        elif (self.did_ball_collide_with_bricks(prob_c, prob_r, ball_obj)):
            #logging.debug("Collision with BRICK")
            ball_obj.flip_horizontal_velocity()
        elif (self.did_ball_collide_with_ufo(prob_c, prob_r)):
            logging.debug("Horizontal Collision with UFO")
            ball_obj.flip_horizontal_velocity()
        else:
            ball_obj.move_horizontally()

        ###  Collision with paddle ########################
        # (TECHNICALLY impossible as collision with paddle can happen only vertically)

    def claim_life(self):
        self._lives_left -= 1
        sleep(0.7)
        if self._lives_left == 0:
            self.game_over_screen("All lives are over")
        self.init_new_life()
        termios.tcflush(
            sys.stdin, termios.TCIOFLUSH
        )  # to prevent character accumulation in buffer coz  input rate might be faster than frame rate

    def move_ball_vertically(self, ball_obj):

        # getter implemented in ball class, left_c and left_r are private variables
        prob_c = ball_obj.left_c
        prob_r = ball_obj.get_vertical_prediction()

        if ball_obj.left_r == prob_r:
            return  # ball did not move => no need to check

        ########### Collision with wall ##########################
        if self.did_ball_collide_with_wall(prob_c, prob_r):
            logging.debug("Vertical Collision with wall")
            ball_obj.flip_vertical_velocity()
        elif (self.did_ball_collide_with_bricks(prob_c, prob_r, ball_obj)):
            logging.debug("Vertical Collision with BRICK")
            ball_obj.flip_vertical_velocity()
        elif (self.did_ball_collide_with_paddle(prob_c, prob_r, ball_obj)):
            logging.debug("Vertical Collision with PADDLE")
            # Even if the ball stuck due to magnet, reverse velocity will be helpful for the next time the ball gets released
            ball_obj.flip_vertical_velocity()
        elif (self.did_ball_collide_with_ufo(prob_c, prob_r)):
            logging.debug("Vertical Collision with UFO")
            ball_obj.flip_vertical_velocity()
        else:
            if prob_r < 0:
                ball_obj.flip_vertical_velocity()
                #################RESTORE THIS################################
                # '''sys.exit()'''
                # ball_obj.isActive = False
                # self.balls_list.remove(ball_obj)
                # if len(self.balls_list) == 0:
                #     self._lives_left -= 1
                #     sleep(0.7)
                #     if self._lives_left == 0:
                #         self.game_over_screen("All lives are over")
                #     self.init_new_life()
                #     termios.tcflush(
                #         sys.stdin, termios.TCIOFLUSH
                #     )  # to prevent character accumulation in buffer coz  input rate might be faster than frame rate
                #################RESTORE THIS  ENDS################################

                logging.error(
                    "\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nBALL TOUCHED GROUND\n$$$$$$$$$$$$$$$$$$"
                )
            else:
                ball_obj.move_vertically()


    def did_bullet_collide_with_bricks(self, prob_c, prob_r, bullet_obj):
        '''Returns true if collided with a brick and false otherwise, 
        The true/false helps determine whether to vanish bullet or not
        '''
        # invariant= only active bricks present in bricks_list
        bricks_checklist = self.bricks_list.copy()
        for a_brick in bricks_checklist:
            # # proceed only if brick is still visible

            '''Using the ball function for brick also'''
            if self.did_ball_collide_with_this_brick(prob_c, prob_r, a_brick):
                # False as not forced
                self.hit_brick(a_brick, False)
                return True
        return False

    def move_bullet_vertically(self, bullet_obj):
    
        # getter implemented in bullet class, left_c and left_r are private variables
        prob_c = bullet_obj.left_c
        prob_r = bullet_obj.get_vertical_prediction() 

        ########### Collision with wall ##########################
        '''I am using the function I made for ball here only'''
        if self.did_ball_collide_with_wall(prob_c, prob_r):
            logging.debug("BULLET Vertical Collision with wall")
            bullet_obj.isActive = False
            self.curr_bullets_list.remove(bullet_obj)
            #############################################
        elif (self.did_bullet_collide_with_bricks(prob_c, prob_r, bullet_obj)):
            logging.debug("BULLET Vertical Collision with BRICK")
            bullet_obj.isActive = False
            self.curr_bullets_list.remove(bullet_obj)
            #################################################       
        else:
            bullet_obj.move_vertically()



    def did_powerup_collide_with_paddle(self, curr_powerup):
        # just_game_rows, just_game_cols
        dc = curr_powerup.left_c - self._game_paddle.left_c
        '''This works bcoz powerups have size 1 x 1, reimplement if you change powerup size'''
        if self._game_paddle.left_r == curr_powerup.left_r and (
                dc >= 0 and dc < self._game_paddle.len_c):
            return True
        return False

    def did_bomb_collide_with_paddle(self, curr_bomb):
        # just_game_rows, just_game_cols
        dc = curr_bomb.left_c - self._game_paddle.left_c
        '''This works bcoz bombs have size 1 x 1, reimplement if you change BOMB size'''
        if self._game_paddle.left_r == curr_bomb.left_r and (
                dc >= 0 and dc < self._game_paddle.len_c):
            return True
        return False


    def get_max_shooting_time_left(self):
        curr_max=0
        for powerup in self.curr_powerups_list:
            if powerup.status == "active":
                if isinstance(powerup,PaddleShoot):
                    curr_max=max(curr_max,conf.POWERUP_DURATION-(clock() - powerup.activate_time))
        return curr_max
                    

    def check_powerups_expiry(self):
        eliminate_list = []
        for powerup in self.curr_powerups_list:
            if powerup.status == "active":
                if clock() - powerup.activate_time > conf.POWERUP_DURATION:
                    powerup.eliminate()
                    powerup.deactivate_powerup(self)
                    eliminate_list.append(powerup)
        for i in eliminate_list:
            self.curr_powerups_list.remove(i)

    @property
    def game_paddle(self):
        return self._game_paddle

    def move_powerups(self):
        eliminate_list = []

        # this list contains both types of powerups, in_air and activated
        for curr_powerup in self.curr_powerups_list:
            if curr_powerup.status == "in_air":
                curr_powerup.move()

                # if powerup touched the paddle
                if curr_powerup.left_r == 0:

                    # valid contact between paddle and powerup=> activate powerup
                    if self.did_powerup_collide_with_paddle(curr_powerup):
                        curr_powerup.activate_powerup(
                            self)  # sending the game obj to powerups
                        self._score += conf.SCORE_POWERUP_PICKED
                    else:
                        # powerup touched floor but not did not hit paddle
                        curr_powerup.eliminate()
                        eliminate_list.append(curr_powerup)
        for i in eliminate_list:
            self.curr_powerups_list.remove(i)


    def move_bombs(self):
        eliminate_list = []
        should_eliminate=True
        # this list contains both types of bombs, in_air and activated
        for curr_bomb in self.curr_bombs_list:
            if curr_bomb.status == "in_air":
                curr_bomb.move()

                # if bomb touched the paddle
                if curr_bomb.left_r == 0:

                    # valid contact between paddle and bomb=> activate bomb
                    if self.did_bomb_collide_with_paddle(curr_bomb):
                        '''CLAIM HIS LIFE'''
                        logging.info("Bomb collided with paddle")
                        self.claim_life() # will empty all the lists and hence, eliminating from emty ist would be bad
                        should_eliminate=False    
                    
                    curr_bomb.eliminate()
                    eliminate_list.append(curr_bomb)

        if should_eliminate:
            for i in eliminate_list:
                logging.info(f"Bomb list is {self.curr_bombs_list}")
                logging.info(f"Bomb TO remove is {self.curr_bombs_list}")
                self.curr_bombs_list.remove(i)

    def descend_bricks(self):
        ########COMMENT THIS##########
        return
        ##############################
        logging.info("GOing to descend all bricks")

        for this_brick in self.bricks_list:
            assert (this_brick.isVisible)
            if this_brick.isVisible:
                # move it down
                this_brick.move_brick(-1)
                if this_brick.left_r == 1:
                    self.game_over_screen(
                        "Brick touched PADDLE LEVEL. You lost")

    def update_rainbow_bricks(self):
        dup_bricks_list = self.bricks_list.copy()
        for this_brick in dup_bricks_list:
            if isinstance(this_brick, RainbowBrick):
                new_power = ((this_brick.power_factor + 1) % 3) + 1
                this_brick.update_power_factor(new_power)

    def start_game(self):
        logging.info("#### ## Inside play function of GAME class ## ######")
        #print("+++++++++++++++++++++++++++++++++++++++++++++++")
        #self.generate_brick_coordinates()
        time_unit_duration = 0.1

        # The first painting on the canvas
        self.paint_objs()
        #print(f"{Style.BRIGHT}")

        # The first display of the canvas
        self._screen.print_board()

        self.did_any_ball_hit_the_paddle = False

        global_cnt = 0

        while True:
            paddle_last_tended = clock()
            global_cnt += 1
            # logging.error(f"Paddle len theoretical is {self._game_paddle.len_c} and actual is {self._game_paddle.ascii_repr.shape}")
            assert (self._game_paddle.len_c ==
                    self._game_paddle.ascii_repr.shape[1])

            #######################################################################################
            ##########--DESCENT OF BRICKS -- ##########################################
            if self.did_any_ball_hit_the_paddle and conf.TIME_BEFORE_BRICKS_DESCEND < clock(
            ) - self.level_start_time:
                self.descend_bricks()
            self.did_any_ball_hit_the_paddle = False

            # bricks_length_initial = len(self.bricks_list)
            while clock() - paddle_last_tended < time_unit_duration:
                #logging.info(f"Inside obstacle loop, dis is {clock() - paddle_last_tended}")
                dup_list = self.balls_list.copy()
                mandatory_show = False
                for this_ball in dup_list:
                    if ((this_ball.vel_c)!=0) and \
                        clock()-this_ball.ball_last_tended_h > time_unit_duration/abs(this_ball.vel_c):
                        '''update balls position horizontally (if unstuck only)'''
                        self.move_ball_horizontally(this_ball)

                        # self.paint_objs()
                        # self._screen.print_board()
                        # print screen
                        this_ball.ball_last_tended_h = clock()
                        if this_ball.left_r == 0:
                            mandatory_show = True

                # if mandatory_show:
                #     self.paint_objs()
                #     self._screen.print_board()

                for this_ball in dup_list:
                    if ((this_ball.vel_r)!=0) and \
                        clock()-this_ball.ball_last_tended_v > time_unit_duration/abs(this_ball.vel_r):
                        '''update balls position vertically (if unstuck only)'''
                        self.move_ball_vertically(this_ball)
                        this_ball.ball_last_tended_v = clock()

                bullets_dup_list=self.curr_bullets_list.copy()
                for this_bullet in bullets_dup_list:
                    if ((this_bullet.vel_r)!=0) and \
                        clock()-this_bullet.bullet_last_tended_v > time_unit_duration/abs(this_bullet.vel_r):
                        '''update bullets position vertically'''
                        self.move_bullet_vertically(this_bullet)
                        this_bullet.bullet_last_tended_v = clock()

    

            self.move_powerups()
            self.move_bombs()

            if self.curr_level==3:
                if clock()-self.recent_bomb_time>conf.TIME_BETWEEN_BOMBS:
                    self.recent_bomb_time=clock()
                    new_bomb=BombClass(self.game_ufo.left_r, self.game_ufo.left_c+self.game_ufo.len_c//2)
                    self.curr_bombs_list.append(new_bomb)

            dup_list = self.balls_list.copy()
            # for this_ball in dup_list:
            #     self.move_ball_vertically(this_ball)

            if global_cnt % 10 == 0:
                self.update_rainbow_bricks()

            self.check_powerups_expiry()
            self.paint_objs()
            self._screen.print_board()
            self.print_game_details()

            if self.handle_input():  # found a keystroke
                logging.info("moving to next level automated")
                self.next_level()
            elif BricksClass.tot_breakable_bricks == 0:

                if self.curr_level<3:
                    logging.info("moving to next level")
                    self.next_level()
                    #break
                else:
                    pass

            if self.get_time_left()[1] < 0:
                self.game_over_screen("You LOST ON TIME !!!")