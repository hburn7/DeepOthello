import logging
import math
import numpy as np

from src.core import config
from src.core.logger import logger

from enum import Enum

WHITE = 1
BLACK = -1

BLACK_BITS = np.uint64(0x0000000810000000)
WHITE_BITS = np.uint64(0x0000001008000000)
DIR_COUNT = 8
UNIVERSE = np.uint64(0xffffffffffffffff)

DIR_INCREMENTS = np.array([8, 9, 1, -7, -8, -9, -1, 7], dtype=np.uint64)
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


def opposite(c):
    if c == BLACK:
        return WHITE

    return BLACK


class Move:
    def __init__(self, c, pos=-1, is_pass=True):
        self.color = c
        self.pos = pos
        self.is_pass = is_pass

    def __repr__(self):
        return f'Move([{self.pos_to_str()}] c={self.color} (pos={self.pos}, is_pass={self.is_pass})'

    def pos_to_str(self):
        # This is wrong
        i = self.pos + 1
        letters = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
        letter_idx = int(math.floor(i / 8))
        remainder = i % 8
        return f'{letters[letter_idx]} {remainder}'


class BitBoard:
    def __init__(self, c, bits: np.uint64 = 0):
        self.color = c

        if bits != np.uint64(0):
            self.bits = bits
        else:  # Initialize default
            if self.color == -1:  # Black
                self.bits = BLACK_BITS
            else:
                self.bits = WHITE_BITS

        logger.info(self.bits)

    def __repr__(self):
        return f'BitBoard(color={self.color} ({self.color}, bits={self.bits} ({np.binary_repr(self.bits, 64)}))'

    def set_bit(self, pos) -> None:
        """
        Sets the bit at the desired position to 1.
        :param pos: Bit position to set. Range 0 to 63 inclusive. Throws ValueError if pos is outside that bound.
        """
        if pos < 0 or pos > 63:
            raise ValueError(f'Expected pos between 0 and 63 inclusive. Received {pos}')

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

    def apply_move(self, m: Move):
        self.set_bit(1 << m.pos)


class GameBoard:
    def __init__(self, player_board: BitBoard, opp_board: BitBoard):
        self.p_color = player_board.color
        self.o_color = opp_board.color
        self.player_board = player_board
        self.opp_board = opp_board
        print(self)

    def __repr__(self):
        return f'GameBoard(player_board={self.player_board}, opp_board={self.opp_board})'

    def legal_moves(self, b: BitBoard, o: BitBoard):
        """Returns a list of all possible moves for the given bitboard"""
        r = []
        move_mask = self.__generate_move_mask(b.bits, o.bits)
        for i in range(64):
            mask = np.uint64(1 << i)
            if (mask & move_mask) != 0:
                r.append(Move(b.color, i, False))

        return r

    def _get_bitboard(self, c):
        """
        Returns a bitboard based on the color
        :param c: Color of the bitboard we want to retrieve
        """
        return self.player_board if c == self.p_color else self.opp_board

    def print(self):
        logger.info('    A B C D E F G H')
        logger.info('    * * * * * * * *')

        black = self._get_bitboard(BLACK)
        white = self._get_bitboard(WHITE)

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

    def __apply_move(self, b: BitBoard, m: Move):
        b.apply_move(m)

        self.__set_for_color(b)

    def __is_game_complete(self):
        p_bits = self.player_board.bits
        o_bits = self.opp_board.bits

        p_legal = self.__generate_move_mask(p_bits, o_bits)
        o_legal = self.__generate_move_mask(o_bits, p_bits)

        return (p_legal == 0 and o_legal == 0) or (p_bits | o_bits) == UNIVERSE

    def __generate_move_mask(self, p_bits: np.uint64, o_bits: np.uint64) -> np.uint64:
        empty_mask = ~p_bits & ~o_bits
        move_mask = np.uint64(0)

        for i in range(DIR_COUNT):
            hold_mask = p_bits

            # Finds opponent disks that are adjacent to player disks
            # in the current direction
            hold_mask = self.__update_hold_mask(hold_mask, i)
            hold_mask = hold_mask & o_bits

            j = 0
            while (j < 6) & (hold_mask != 0):
                hold_mask = self.__update_hold_mask(hold_mask, i)

                dir_move_mask = hold_mask & empty_mask
                move_mask |= dir_move_mask
                hold_mask &= (~dir_move_mask & o_bits)

                j += 1

        return move_mask

    def __line_cap(self, b: BitBoard, m: Move):
        opp = self._get_bitboard(opposite(b.color))

        self_bits = b.bits
        o_bits = opp.bits

        mask = np.uint64(1 << m.pos)
        f_fin = 0
        possibility = 0

        for i in range(DIR_COUNT):
            to_change = search = 0
            self.__update_hold_mask(mask, i)

            possibility = o_bits & search

            while possibility != 0:
                to_change |= possibility
                self.__update_hold_mask(mask, i)

                if (self_bits & search) != 0:
                    f_fin |= to_change
                    break

                possibility = o_bits & search

        self_bits |= f_fin
        o_bits = (~f_fin) & o_bits

        b.bits = self_bits
        opp.bits = o_bits

        self.__set_for_color(b)
        self.__set_for_color(opp)

    def __get_opposite_board(self, b: BitBoard):
        if b.color == self.p_color:
            return self.opp_board

        return self.player_board

    def __update_hold_mask(self, hold_mask, i):
        if DIR_INCREMENTS[i] > 0:
            hold_mask = np.uint64(hold_mask << DIR_INCREMENTS[i]) & DIR_MASKS[i]
        else:
            hold_mask = np.uint64(hold_mask >> -DIR_INCREMENTS[i]) & DIR_MASKS[i]
        return hold_mask

    def count_pieces(self, c):
        return int(self._get_bitboard(c).bits.count('1'))

    def __set_for_color(self, b: BitBoard):
        """Updates bitboard based on color"""
        if b.color == self.player_board.color:
            self.player_board = b
        else:
            self.opp_board = b
