import os
import sys
import math
import numpy as np
import colorama
from colorama import Fore, Back, Style
colorama.init(autoreset=False)
import termios
from input_fd import InputHelper
from screen import Screen
import config as conf
import random
from time import monotonic as clock, sleep
from paddle import PaddleClass
from ball_class import BallClass
from bricks_class import BricksClass, UnbreakableBrick, NormalBrick, ExplosiveBrick
from powerups import PowerupsClass, ExpandPaddle, ShrinkPaddle, FastBall, ThruBall, PaddleGrab, BallMultiplier

###############################################################
import logging


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

        self._screen = Screen(self._just_game_rows, self.just_game_cols,
                              self._info_box_height)

        #############################################################################
        self._input_stream = InputHelper()
        self._score = 0
        self._lives_left = conf.TOT_LIVES
        self.frame_count = 0
        self._overall_start_time = clock()

        # self.available_powerups=[ExpandPaddle, ShrinkPaddle, FastBall, ThruBall,BallMultiplier,PaddleGrab]
        self.bricks_list = []
        self.available_powerups = [ShrinkPaddle]
        self.init_new_life()

        ######################################################################

    def init_new_life(self):
        '''Initializes values for the current life'''
        self.curr_powerups_list = []  # All powerups have to be removed

        # Reinit the powerup random list
        self.curr_powerup_idx = 0

        # Making the game paddle
        self.game_paddle = PaddleClass(self.just_game_cols // 2)

        # A new game ball
        original_ball = BallClass(
            self.game_paddle.left_c + self.game_paddle.len_c // 2, 1, True, 1,
            0)
        self.balls_list = [original_ball]
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

    def paint_objs(self):
        '''Paints all the objects into CANVAS for the current iteration'''
        self._screen.clear_foreground()
        self._screen.add_entity(self.game_paddle.left_c, self.game_paddle.left_r, \
            self.game_paddle.len_c, self.game_paddle.len_r, self.game_paddle.ascii_repr,"")

        for this_ball in self.balls_list:
            if this_ball.isVisible:
                self._screen.add_entity(this_ball.left_c, this_ball.left_r, \
                    this_ball.len_c, this_ball.len_r, this_ball.ascii_repr,conf.BG_COLOR)

        for brick in self.bricks_list:
            self._screen.add_brick(brick)

        for send_powerup in self.curr_powerups_list:
            if send_powerup.status == "in_air":
                self._screen.add_entity(send_powerup.left_c, send_powerup.left_r, send_powerup.len_c,\
                    send_powerup.len_r,send_powerup.ascii_repr, "")

    def get_time_left(self):
        '''Get time left'''
        time_now = clock()
        time_elapsed = time_now - self._overall_start_time
        time_left = conf.TOT_TIME - time_elapsed
        return round(time_left, 1)

    def print_game_details(self):
        '''Printing of game stats'''
        # score, lives_left, time_left, current number of powerups activated
        string_up = Back.RED
        for i in range(0, self._info_box_height):
            string_up += "\033[F"
        print(string_up)

        cnt = 0
        thru_ball_there = False
        for i in self.curr_powerups_list:
            if i.status == "active":
                cnt += 1
                if isinstance(i, ThruBall) == True:
                    thru_ball_there = True
        speeds_list = []
        for i in self.balls_list:
            speeds_list.append(i.vel_c)

        print(f"Score now is {str(self._score).ljust(10)}", end='')
        print(f"Lives left  is {self._lives_left}")
        print(f"Balls Horizontal speed (INERTIA) are {speeds_list}")
        print(f"Time left  is {self.get_time_left()}")
        # print(f"Score now is {str(self._score).ljust(10)}",end='')
        print(f"Number of powerups there is {str(cnt).ljust(10)}", end='')
        print(f"Paddle length is {self.game_paddle.len_c}")
        print(f"Thru ball is : {thru_ball_there}")
        print(Back.BLACK)

    def generate_brick_coordinates(self):
        '''Designing layout of bricks'''
        # h=20, #w=60

        # rows go from 0 to tot_r-1 , start from 10, go till end-2
        # cols go from 0 to tot_c-1 , go from 5 to end-5
        first_code = 0
        for i in range(15, self._just_game_rows - 2):
            first_idx = (first_code - i)
            seq_in_row = 0
            for j in range(5, self.just_game_cols - 5, 3):
                seq_in_row += 1
                #logging.info(f"Coordinates are {i}:{j}")
                color_code = ((first_idx + seq_in_row) % 5 + 5) % 5 + 1
                logging.critical(f"{seq_in_row-i}:{color_code}")
                decided_class = NormalBrick
                if color_code == 4:
                    decided_class = UnbreakableBrick
                elif color_code == 5:
                    decided_class = ExplosiveBrick
                self.bricks_list.append(
                    decided_class(i, j, seq_in_row, (seq_in_row - i),
                                  color_code))
            logging.critical("\n")

    def handle_input(self):
        '''Handles paddle movement, Moves balls alongwith paddle if stuck, releases any stuck ball if 's' is pressed '''
        ret_val = False
        if self._input_stream.is_pending():
            inp = self._input_stream.get_pending_char()
            logging.info(f"\n[PRESSED {inp}]\n")
            paddle_new_details = None
            if inp == 'a':
                paddle_new_details = self.game_paddle.change_x(
                    -1, self.just_game_cols)
                # DEAL WITH CASE WHEN BALL IS STUCK ALSO
                ret_val = True
            elif inp == 'd':
                paddle_new_details = self.game_paddle.change_x(
                    1, self.just_game_cols)
                # DEAL WITH CASE WHEN BALL IS STUCK ALSO
                ret_val = True
            elif inp == 's':
                for this_ball in self.balls_list:
                    if this_ball.is_stuck == True:
                        this_ball.release()
                        ret_val = True

            if paddle_new_details is not None:
                for ball_obj in self.balls_list:
                    if ball_obj.is_stuck == True:
                        ball_obj.follow_paddle(paddle_new_details[0] +
                                               paddle_new_details[1] // 2)

            termios.tcflush(
                sys.stdin, termios.TCIOFLUSH
            )  # to prevent character accumulation in buffer coz  input rate might be faster than frame rate
        return ret_val

    def did_ball_collide_with_wall(self, prob_c, prob_r):
        '''Checks if ball collided with the ball'''
        logging.critical(f"BALL WALL insvestigation is {prob_r}:{prob_c}")
        if prob_c < 0 or prob_c >= self.just_game_cols:
            return True
        if prob_r < 0 or prob_r >= self._just_game_rows:
            return True
        return False

    def game_over_screen(self, msg):
        '''Prints GAME OVER SCREEN'''
        print(self.CLEAR_ANSI)
        print(self.RESET_CURSOR_ANSI)
        print(f"{Fore.GREEN}{Back.YELLOW}{Style.BRIGHT}")
        # print("Green Text - Yellow Background - Bright")
        # print("HELLO")
        print("GAME OVER".center(os.get_terminal_size().columns))
        print(f"{msg}".center(os.get_terminal_size().columns))
        print(f"Your score is {self._score}".center(
            os.get_terminal_size().columns))
        sys.exit()
        pass

    def did_ball_collide_with_paddle(self, prob_c, prob_r, ball_obj):
        '''Checks if the ball collided with the paddle'''
        dc = prob_c - self.game_paddle.left_c
        if self.game_paddle.left_r == prob_r and (dc >= 0 and
                                                  dc < self.game_paddle.len_c):
            speed_inc_dist = prob_c - (self.game_paddle.left_c +
                                       self.game_paddle.len_c // 2)
            logging.debug(f"speed inc is {speed_inc_dist}")
            ball_obj.impact_velocity(speed_inc_dist // 2)

            if self.game_paddle.is_magnet == True:
                ball_obj.is_stuck = True
                ball_obj.offset_from_center = prob_c - (
                    self.game_paddle.left_c + self.game_paddle.len_c // 2)
            return True
        return False

    # def destroy_this_brick(self, brick_obj):

    #     if brick_obj.isVisible==False:
    #         return
    #     brick_obj.isVisible=False
    #     self._score+=brick_obj.score_bounty
    #     self._screen.finish_brick(brick_obj)
    #     unlucky_friends=brick_obj.get_unlucky_friends()
    #     logging.info(f"unlucky coordinates for power {brick_obj.power_factor} are {unlucky_friends}")
    #     for a_brick in self.bricks_list:
    #         logging.error(f"{[a_brick.left_r,a_brick.seq_id]}")
    #         if [a_brick.left_r,a_brick.seq_id] in unlucky_friends and a_brick.power_factor!=4:
    #             logging.info("FOund")
    #             self.destroy_this_brick(a_brick)

    def did_ball_collide_with_this_brick(self, prob_c, prob_r, brick_obj):
        '''Returns True if ball collided with THIS brick,false otherwise'''
        dc = prob_c - brick_obj.left_c
        if (brick_obj.left_r == prob_r and (dc >= 0 and dc < brick_obj.len_c)):
            return True
        return False

    def try_powerup_generation(self, prob_r, prob_c):
        self.curr_powerup_idx = (self.curr_powerup_idx + 1) % (len(
            self.available_powerups))

        chosen_powerup = self.available_powerups[self.curr_powerup_idx]
        if chosen_powerup == ThruBall:
            eliminate_powerup = None
            for already_there_powerup in self.curr_powerups_list:
                if isinstance(
                        already_there_powerup,
                        ThruBall) and already_there_powerup.status == "active":
                    eliminate_powerup = already_there_powerup
            if eliminate_powerup is not None:
                eliminate_powerup.status = "inactive"
                self.curr_powerups_list.remove(eliminate_powerup)

        # Create a new powerup and append it to the array
        new_powerup = chosen_powerup(prob_r, prob_c)
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
        logging.critical(f"Inside HIT brick function for {brick_obj.__dict__}")
        #assert (brick_obj.isVisible == True)
        if brick_obj.isVisible and brick_obj.damage(is_forced):
            # brick broken => take score of breaking this brick
            self._score += brick_obj.score_bounty
            self._screen.finish_brick(brick_obj)
            self.bricks_list.remove(brick_obj)

            if is_origin_brick:
                self.try_powerup_generation(brick_obj.left_r, brick_obj.left_c)

            unlucky_neighbors = brick_obj.get_unlucky_friends()

            # A sad_brick is surely due to explosion
            # Confirm with TA if unbreakable brick should break if next to explosive break

            chosen_ones = []
            for sad_brick in self.bricks_list:
                # if sad_brick.left_r==15 and sad_brick.seq_id==11 and brick_obj.left_r==16 and brick_obj.left_c==10:
                #     #logging.info("voila")
                #     pass
                if self.is_there(sad_brick.left_r, sad_brick.seq_id,
                                 unlucky_neighbors):
                    #logging.info(f"Sad brick credentials are {sad_brick.__dict__}\n")
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
            # if self.bricks_list[i].isVisible==False:
            #     continue
            if self.did_ball_collide_with_this_brick(prob_c, prob_r, a_brick):
                self.hit_brick(a_brick, ball_obj.is_boss)
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
            ball_obj.flip_horizontal_velocity()
        elif (self.did_ball_collide_with_bricks(prob_c, prob_r, ball_obj)):
            #logging.debug("Collision with BRICK")
            ball_obj.flip_horizontal_velocity()
        else:
            ball_obj.move_horizontally()

        ###  Collision with paddle ########################
        # (TECHNICALLY impossible as collision with paddle can happen only vertically)

    def move_ball_vertically(self, ball_obj):

        # getter implemented in ball class, left_c and left_r are private variables
        prob_c = ball_obj.left_c
        prob_r = ball_obj.get_vertical_prediction()

        if ball_obj.left_r == prob_r:
            return  # ball did not move => no need to check

        ########### Collision with wall ##########################
        if self.did_ball_collide_with_wall(prob_c, prob_r):
            #logging.debug("Collision with wall")
            ball_obj.flip_vertical_velocity()
        elif (self.did_ball_collide_with_bricks(prob_c, prob_r, ball_obj)):
            #logging.debug("Collision with BRICK")
            ball_obj.flip_vertical_velocity()
        elif (self.did_ball_collide_with_paddle(prob_c, prob_r, ball_obj)):
            # change vertical woth velocity
            ball_obj.flip_vertical_velocity()
        else:
            if prob_r == 0:
                '''sys.exit()'''
                ball_obj.isActive = False
                self.balls_list.remove(ball_obj)
                if len(self.balls_list) == 0:
                    self._lives_left -= 1
                    if self._lives_left == 0:
                        self.game_over_screen("All lives are over")
                    self.init_new_life()
                    termios.tcflush(
                        sys.stdin, termios.TCIOFLUSH
                    )  # to prevent character accumulation in buffer coz  input rate might be faster than frame rate
                logging.error(
                    "\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nBALL TOUCHED GROUND\n$$$$$$$$$$$$$$$$$$"
                )
            else:
                ball_obj.move_vertically()

    def did_powerup_collide_with_paddle(self, curr_powerup):
        # just_game_rows, just_game_cols
        dc = curr_powerup.left_c - self.game_paddle.left_c
        if self.game_paddle.left_r == curr_powerup.left_r and (
                dc >= 0 and dc < self.game_paddle.len_c):
            return True
        return False

    def check_powerups_expiry(self):
        eliminate_list = []
        for powerup in self.curr_powerups_list:
            if powerup.status == "active":
                if clock() - powerup.activate_time > conf.POWERUP_DURATION:
                    powerup.status = "inactive"
                    powerup.deactivate_powerup(self)
                    eliminate_list.append(powerup)
        for i in eliminate_list:
            self.curr_powerups_list.remove(i)

    def move_powerups(self):

        # move only if unstuck

        eliminate_list = []

        # this list contains both types of powerups, in_air and activated
        for curr_powerup in self.curr_powerups_list:
            if curr_powerup.status == "in_air":
                curr_powerup.left_r += curr_powerup.vel_r
                if curr_powerup.left_r == 0:
                    if self.did_powerup_collide_with_paddle(curr_powerup):
                        curr_powerup.status = "active"
                        curr_powerup.activate_powerup(
                            self)  # sending the game obj to powerups
                        self._score += conf.SCORE_POWERUP_PICKED
                    else:
                        curr_powerup.status = "inactive"
                        eliminate_list.append(curr_powerup)
        for i in eliminate_list:
            self.curr_powerups_list.remove(i)

    def play(self):
        logging.info("#### ## Inside play function of GAME class ## ######")
        print("+++++++++++++++++++++++++++++++++++++++++++++++")
        self.generate_brick_coordinates()
        time_unit_duration = 0.1

        # The first painting on the canvas
        self.paint_objs()
        #print(f"{Style.BRIGHT}")

        # The first display of the canvas
        self._screen.print_board()

        while True:
            paddle_last_tended = clock()
            # logging.error(f"Paddle len theoretical is {self.game_paddle.len_c} and actual is {self.game_paddle.ascii_repr.shape}")
            assert (
                self.game_paddle.len_c == self.game_paddle.ascii_repr.shape[1])

            while clock() - paddle_last_tended < time_unit_duration:
                #logging.info(f"Inside obstacle loop, dis is {clock() - paddle_last_tended}")
                dup_list = self.balls_list.copy()
                for this_ball in dup_list:
                    if ((this_ball.get_ball_speed_magnitude())!=0) and \
                        clock()-this_ball.ball_last_tended > time_unit_duration/(this_ball.get_ball_speed_magnitude()):
                        '''update balls position horizontally (if unstuck only)'''
                        self.move_ball_horizontally(this_ball)

                        # self.paint_objs()
                        # self._screen.print_board()
                        # print screen
                        this_ball.ball_last_tended = clock()
                    else:
                        #sys.exit()
                        pass
            #sys.exit()
            #logging.info("Outside obstacle loop")
            if self.handle_input():  # found a keystroke
                pass

            self.move_powerups()

            dup_list = self.balls_list.copy()
            for this_ball in dup_list:
                self.move_ball_vertically(this_ball)

            self.check_powerups_expiry()
            self.paint_objs()
            self._screen.print_board()
            self.print_game_details()

            if self.get_time_left() < 0:
                self.game_over_screen("You LOST ON TIME !!!")
