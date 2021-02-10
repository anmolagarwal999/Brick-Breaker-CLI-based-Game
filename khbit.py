#!/usr/bin/env python
'''
A Python class implementing KBHIT, the standard keyboard-interrupt poller.
Works transparently on Windows and Posix (Linux, Mac OS X).  Doesn't work
with IDLE.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as 
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

'''

import os
import sys
import termios
import atexit
from select import select


class KBHit:
    def __init__(self):
        '''Creates a KBHit object that you can call to do various keyboard things.
        '''

        
        '''I think that aim here is to make input unbuffered so that newline isn't needed to send characters to the program'''
        # Save the terminal settings

        # get input stdin file descriptor
        self.fd = sys.stdin.fileno(
        )  # https://stackoverflow.com/a/32199696/6427607

        # tty=terminal
        # This method returns a list of tty attributes for the given file descriptor.
        # The attributes are iflag, oflag, cflag, lflag, ispeed, ospeed, cc.
        self.new_term = termios.tcgetattr(self.fd)
        self.old_term = termios.tcgetattr(self.fd)

        # New terminal setting unbuffered
        '''
        Read here: https://blog.nelhage.com/2009/12/a-brief-introduction-to-termios-termios3-and-stty/

        ICANON - Perhaps the most important bit in c_lflag is the ICANON bit.
        Enabling it enables “canonical” mode – also known as “line editing” mode.
        When ICANON is set, the terminal buffers a line at a time, and enables line editing.
        Without ICANON, input is made available to programs immediately (this is also known as “cbreak” mode).
        
        
        ECHO in c_lflag controls whether input is immediately re-echoed as output.
        It is independent of ICANON, although they are often turned on and off together.
        When passwd prompts for your password, your terminal is in canonical mode, but ECHO is disabled.
        
        
        '''
        self.new_term[3] = (self.new_term[3] & ~termios.ICANON
                            & ~termios.ECHO)
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

        # Support normal-terminal reset at exit
        atexit.register(self.set_normal_term)

    def set_normal_term(self):
        ''' Resets to normal terminal.  On Windows this is a no-op.
        '''

        
        # prototype: termios.tcsetattr(fd, when, attributes)
        # 'when' decides : The when argument determines when the attributes are changed:
        # TCSANOW to change immediately,
        # TCSADRAIN to change after transmitting all queued output,
        # or TCSAFLUSH to change after transmitting all queued output and discarding all queued input.
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def getch(self):
        ''' Returns a keyboard character after kbhit() has been called.
            Should not be called in the same program as getarrow().
        '''
        return sys.stdin.read(1)

    def kbhit(self):
        ''' Returns True if keyboard character was hit, False otherwise.
        '''
        
        dr, dw, de = select([sys.stdin], [], [], 0)
        return dr != []


####################################################################################
# Test
if __name__ == "__main__":

    kb = KBHit()

    print('Hit any key, or ESC to exit')

    while True:

        if kb.kbhit():
            c = kb.getch()
            c_ord = ord(c)
            print(c)
            print(c_ord)
            if c_ord == 27:  # ESC
                break
            print(c)
            print("---------------")

    kb.set_normal_term()