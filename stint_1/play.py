import os
import numpy as np
from colorama import init as cinit

from game import Game

cinit()
#print('\033[2J') # clear screen
print("\033[2J\033[1;1H") # clear screen
print("---------------------------------------------------")
game = Game()
game.play()
