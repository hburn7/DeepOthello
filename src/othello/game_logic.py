import numpy as np
from othello import color

BLACK_BITS = np.uint64(0x0000000810000000)
WHITE_BITS = np.uint64(0x0000001008000000)

class BitBoard:
    def __init__(self, c, bits=np.uint64(0)):
        self.color = c

        if bits != np.uint64(0):
            self.bits = bits
        else:  # Initialize default
            if self.color == color.BLACK:
                self.bits = BLACK_BITS
            else:
                self.bits = WHITE_BITS