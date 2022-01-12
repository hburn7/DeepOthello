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
        if not isinstance(bits, np.uint64):
            raise ValueError(f"Expected bits to be of type np.uint64, received {bits} instead.")

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

    def get_bitboard(self, c):
        """
        Returns a bitboard based on the color
        :param c: Color of the bitboard we want to retrieve
        """
        return self.player_board if c == self.p_color else self.opp_board

    def set_bitboard(self, b: BitBoard):
        """
        Automatically updates the appropriate bitboard in the GameBoard to the new
        object provided. This is done via color.
        """
        if b.color == color.BLACK or b.color == color.WHITE:
            if self.p_color == b.color:
                self.player_board = b
            else:
                self.opp_board = b
        else:
            raise Exception(f"Expected bitboard with color BLACK or WHITE. Received '{b}' instead.")

    def draw(self):
        logger.info('    A B C D E F G H')
        logger.info('    * * * * * * * *')

        black = self.get_bitboard(color.BLACK)
        white = self.get_bitboard(color.WHITE)

        line = ''
        for i in range(63, -1, -1):
            if i % 8 == 7:
                line += f'{int(-(i / 8) + 9)} * '

            if black.get_bit_state(i):
                line += 'B '
            elif white.get_bit_state(i):
                line += 'W '
            else:
                line += '- '

            if i % 8 == 0:
                logger.info(line)
                line = ''

    def generate_move_mask(self, p_gen=True) -> np.uint64:
        """
        Generates moves for the initial player by default.
        :param p_gen: Determines whether to generate moves for the player or the opponent. Generate
        moves for the current player by default, set to False to generate for opponent.
        :return: A uint64 bitmask containing 1s where the player can move.
        """
        player_bits = self.player_board.bits
        opponent_bits = self.opp_board.bits

        if not p_gen:
            player_bits = self.opp_board.bits
            opponent_bits = self.player_board.bits

        empty_mask = ~player_bits & ~opponent_bits
        move_mask = np.uint64(0)

        for i in range(self.DIR_COUNT):
            # Finds opponent disks that are adjacent to player disks in current direction
            hold_mask = player_bits

            if self.DIR_INCREMENTS[i] > 0:
                hold_mask = (hold_mask << np.uint64(self.DIR_INCREMENTS[i])) & self.DIR_MASKS[i]
            else:
                hold_mask = (hold_mask >> -np.uint64(self.DIR_INCREMENTS[i])) & self.DIR_MASKS[i]

            hold_mask = hold_mask & opponent_bits

            for j in range(6):
                if not (j < 6) & (hold_mask != 0):
                    break

                if self.DIR_INCREMENTS[i] > 0:
                    hold_mask = (hold_mask << np.uint64(self.DIR_INCREMENTS[i])) & self.DIR_MASKS[i]
                else:
                    hold_mask = (hold_mask >> -np.uint64(self.DIR_INCREMENTS[i])) & self.DIR_MASKS[i]

                dir_move_mask = hold_mask & empty_mask
                move_mask |= dir_move_mask
                hold_mask &= (~dir_move_mask & opponent_bits)

        return move_mask

    def count(self):
        """
        Counts the number of set bits across both bitboards.
        """
        return self.player_board.bitcount() + self.opp_board.bitcount()



