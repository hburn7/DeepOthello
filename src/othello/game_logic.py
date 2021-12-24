import numpy as np
from core import config, logger
from othello import color


class Move:
    def __init__(self, c, pos=-1, is_pass=True):
        self.color = c
        self.pos = pos
        self.is_pass = is_pass


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

    def __repr__(self):
        return f'BitBoard(color={self.color} ({color.as_str(self.color)}, bits={self.bits} ({np.binary_repr(self.bits)}))'

    def set_bit(self, pos) -> None:
        """
        Sets the bit at the desired position to 1.
        :param pos: Bit position to set. Range 0 to 63 inclusive. Throws ValueError if pos is outside that bound.
        """
        if pos < 0 or pos > 63:
            raise ValueError(f'Expected pos between 0 and 63 inclusive. Recieved {pos}')

        mask = np.uint64(1 << pos)
        self.bits |= mask

    def get_bit_state(self, p):
        mask = np.uint64(1 << p)
        return (self.bits & mask) != 0

    def disable_bit(self, p):
        mask = np.uint64(1 << p)
        self.bits &= ~mask

    def bitcount(self):
        return self.binary_repr().count('1')

    def binary_repr(self) -> str:
        return np.binary_repr(self.bits, 64)
