import numpy as np

from othello import color
from core import config, logger


class Move:
    def __init__(self, c, pos=-1, is_pass=True):
        self.color = c
        self.pos = pos
        self.is_pass = is_pass

    def __repr__(self):
        return f'Move(c={self.color} ({color.as_str(self.color)}), pos={self.pos}, is_pass={self.is_pass})'

class BitBoard:
    BLACK_BITS = np.uint64(0x0000000810000000)
    WHITE_BITS = np.uint64(0x0000001008000000)

    def __init__(self, c, bits=np.uint64(0)):
        self.color = c

        if bits != np.uint64(0):
            self.bits = bits
        else:  # Initialize default
            if self.color == color.BLACK:
                self.bits = self.BLACK_BITS
            else:
                self.bits = self.WHITE_BITS

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


class GameBoard:
    DIR_COUNT = 8
    UNIVERSE = np.uint64(0xffffffffffffffff)

    DIR_INCREMENTS = [8, 9, 1, -7, -8, -9, -1, 7]
    DIR_MASKS = np.array([
        0xFFFFFFFFFFFFFF00,  # North
        0xFEFEFEFEFEFEFE00,  # NorthWest
        0xFEFEFEFEFEFEFEFE,  # West
        0x00FEFEFEFEFEFEFE,  # SouthWest
        0x00FFFFFFFFFFFFFF,  # South
        0x007F7F7F7F7F7F7F,  # SouthEast
        0x7F7F7F7F7F7F7F7F,  # East
        0x7F7F7F7F7F7F7F00  # NorthEast
    ], dtype=np.uint64)

    def __init__(self, player_board: BitBoard, opp_board: BitBoard):
        self.p_color = player_board.color
        self.o_color = opp_board.color
        self.player_board = player_board
        self.opp_board = opp_board
        self.move_history = []  # List[Move] (we will use this as a Stack)

    def __repr__(self):
        return f'GameBoard(player_board={self.player_board}, opp_board={self.opp_board})'
