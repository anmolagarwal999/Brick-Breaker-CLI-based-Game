import os
import numpy as np
import colorama
from colorama import Fore, Back, Style
colorama.init(autoreset=False)
import random
import time
import sys
from time import monotonic as clock, sleep
import config as conf
from bricks_class import BricksClass,UnbreakableBrick, NormalBrick, ExplosiveBrick

###############################################################
import logging


def part():
    logging.debug("############################")


logging.basicConfig(filename='test.log',
                    level=logging.DEBUG,
                    filemode='w',
                    format='%(levelname)s:%(message)s')
##############################################################


class Canvas:
    '''
    CANVAS FOR THE GAME WINDOW
    '''
    # https://stackoverflow.com/a/56335
    RESET_CURSOR_ANSI = "\033[0;0H" # https://forums.macrumors.com/threads/clear-screen-function.1292111/post-14014870

    def __init__(self, just_game_height, just_game_width, info_box_height):
        logging.info("Inside SCREEN class's INIT()")
        logging.debug(f"info box height is {info_box_height}")

        ###########################################################################]
        self._just_game_height=just_game_height
        self._info_box_height=info_box_height
        self._tot_screen_rows = just_game_height+info_box_height
        self._tot_screen_cols = just_game_width
        part()
        logging.debug(f"Setting screens tot_rows as {self._tot_screen_rows}")
        logging.debug(f"Setting screens tot_cols as {self._tot_screen_cols}")
        # logging.debug(f"conf . BGCOLOR IS  as {conf.BG_COLOR}")
        ##################################################################################################

        self._bg_layer = []

        # Initializing game window with Original BG COLOR
        for i in range(0,self._just_game_height):
            #https://stackoverflow.com/a/3881504/6427607
            arr=[conf.BG_COLOR]*self._tot_screen_cols
            #logging.info(f"\n\narr is {arr}\n\n")
            self._bg_layer.append(arr)

        # initializing score board layer
        # for i in range(0,self._info_box_height):
        #     arr=[conf.DETAILS_BG_COLOR]*self._tot_screen_cols
        #     logging.info(f"\n\narr is {arr}\n\n")
        #     self._bg_layer.append(arr)
        for i in range(0,self._info_box_height):
            if i==0:
                arr=[Back.GREEN]*self._tot_screen_cols
            elif i==self._info_box_height-1:
                arr=[conf.BG_COLOR]*self._tot_screen_cols
            else:
                arr=[conf.DETAILS_BG_COLOR]*self._tot_screen_cols
            #logging.info(f"\n\narr is {arr}\n\n")
            self._bg_layer.append(arr)

        # conversion to an array
        self._bg_layer=np.array(self._bg_layer)

        # logging.debug(f"self.backboard SHAPE IS is  {self._bg_layer.shape}")
        # logging.debug(f"self.backboard is  {self._bg_layer}")
        # part()

        #############################################################################################################
        self._fore_board = np.full((self._tot_screen_rows, self._tot_screen_cols), ' ')
        #############################################################################

        # logging.debug(
        #     f"Finally is self.backboard is  \n{self._bg_layer}\n\n")
        # logging.debug(
        #     f"Finally is self.foreboard (SHAPE: {self._fore_board.shape} is  \n{self._fore_board}\n\n"
        # )

    def clear_foreground(self):
        '''Clearing the front part of the canvas'''
        for i in range(0, self._tot_screen_rows):
            for j in range(self._tot_screen_cols):
                self._fore_board[i][j] = ' '


        #################################################################################
        self._bg_layer = []

        # Initializing game window with Original BG COLOR
        for i in range(0,self._just_game_height):
            #https://stackoverflow.com/a/3881504/6427607
            arr=[conf.BG_COLOR]*self._tot_screen_cols
            #logging.info(f"\n\narr is {arr}\n\n")
            self._bg_layer.append(arr)

        # initializing score board layer
        # for i in range(0,self._info_box_height):
        #     arr=[conf.DETAILS_BG_COLOR]*self._tot_screen_cols
        #     logging.info(f"\n\narr is {arr}\n\n")
        #     self._bg_layer.append(arr)
        for i in range(0,self._info_box_height):
            if i==0:
                arr=[Back.GREEN]*self._tot_screen_cols
            elif i==self._info_box_height-1:
                arr=[conf.BG_COLOR]*self._tot_screen_cols
            else:
                arr=[conf.DETAILS_BG_COLOR]*self._tot_screen_cols
            #logging.info(f"\n\narr is {arr}\n\n")
            self._bg_layer.append(arr)

        # conversion to an array
        self._bg_layer=np.array(self._bg_layer)


    def add_powerup(self, game_powerup):
        if game_powerup.status=="in_air":
            start_col_num = game_powerup.left_c
            start_row_num = game_powerup.left_r
            end_col_num = game_powerup.left_c + game_powerup.len_c
            end_row_num = game_powerup.left_r + game_powerup.len_r
            self._fore_board[start_row_num:end_row_num, start_col_num:
                            end_col_num] = game_powerup.ascii_repr[:]
            self._bg_layer[start_row_num:end_row_num, start_col_num:
                            end_col_num] = conf.BG_COLOR


    def add_entity(self, left_c, left_r, len_c, len_r, ascii_form, bg_string):

        # https://stackoverflow.com/a/26506237/6427607

        #logging.info("Inside add entity func")
        #logging.info(f"entity recived is {game_entity.__dict__}")

        #start_col_num = game_entity.left_x
        start_col_num = left_c
        start_row_num = left_r
        end_col_num = left_c + len_c
        end_row_num = left_r + len_r

        #logging.info(f"Start col num is {start_col_num}\nend_col_num is {end_col_num}")
        #logging.info(f"Start row num is {start_row_num}\nend_row_num is {end_row_num}")

        self._fore_board[start_row_num:end_row_num, start_col_num:
                         end_col_num] = ascii_form[:]
        self._bg_layer[start_row_num:end_row_num, start_col_num:
                         end_col_num] = bg_string

    def finish_brick(self, game_brick):
        logging.error(f"Inside finish brick for {game_brick.__dict__}")
        start_col_num = game_brick.left_c
        start_row_num = game_brick.left_r
        end_col_num = game_brick.left_c + game_brick.len_c
        end_row_num = game_brick.left_r + game_brick.len_r
        self._fore_board[start_row_num:end_row_num, start_col_num:
                         end_col_num] = ''
        #logging.info(f"end col num is {end_col_num}")
        self._bg_layer[start_row_num:end_row_num, start_col_num:
                         end_col_num] = conf.BG_COLOR
        # self.print_board(True)
        part()


    def add_brick(self, game_brick):
        if game_brick.isVisible == False:
            sys.exit("A brick isVisible as False has been sent to add_brick()")
            return
        color_code=game_brick.power_factor
        if game_brick.ascii_repr[0][1]=='5':
            color_code=5
        # color_code=int(game_brick.ascii_repr[0][1])
        start_col_num = game_brick.left_c
        start_row_num = game_brick.left_r
        end_col_num = game_brick.left_c + game_brick.len_c
        end_row_num = game_brick.left_r + game_brick.len_r
        self._fore_board[start_row_num:end_row_num, start_col_num:
                         end_col_num] = game_brick.ascii_repr[:]
        self._bg_layer[start_row_num:end_row_num, start_col_num:
                         end_col_num] = conf.BRICKS_BGCOLORS[
                             color_code]


    def print_board(self, should_wait=False):
        '''
        Display canvas on console
        '''
        
        #logging.info("Using the SETTING CURSON ON TOP ANSI SEQUENCE")
        print(self.RESET_CURSOR_ANSI)
        for i in range(self._just_game_height):
            curr_i=i
            curr_i=self._just_game_height-i-1
            for j in range(self._tot_screen_cols):
                curr_j=j
                print(self._bg_layer[curr_i][curr_j] + self._fore_board[curr_i][curr_j], end='')
            print('')

        for i in range(self._just_game_height,self._tot_screen_rows):
            curr_i=i
            for j in range(self._tot_screen_cols):
                curr_j=j
                print(self._bg_layer[curr_i][curr_j] + self._fore_board[curr_i][curr_j], end='')
            print('')
        



