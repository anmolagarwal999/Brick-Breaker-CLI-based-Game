import os
import sys
import atexit
import termios
from select import select

# Read theoretical stuff here: https://blog.nelhage.com/2009/12/a-brief-introduction-to-termios-termios3-and-stty/
class InputHelper:
    def __init__(self):
       
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
        atexit.register(self.restore_original_settings)

   
    def get_pending_char(self):     
        return sys.stdin.read(1)

    def is_pending(self):
        ''' Returns True if keyboard was hit, False otherwise. '''
        dr, dw, de = select([sys.stdin], [], [], 0)
        return dr != []

    def restore_original_settings(self):          
        # prototype: termios.tcsetattr(fd, when, attributes)
        # 'when' decides : The when argument determines when the attributes are changed:
        # TCSANOW to change immediately,
        # TCSADRAIN to change after transmitting all queued output,
        # or TCSAFLUSH to change after transmitting all queued output and discarding all queued input.
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)


