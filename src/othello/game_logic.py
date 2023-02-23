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
DIRECTION_COUNT = 8
UNIVERSE = np.uint64(0xffffffffffffffff)

DIR_INCREMENTS = np.array([8, 9, 1, -7, -8, -9, -1, 7], dtype=int)
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
    def __init__(self, c, pos):
        self.color = c

        if type(pos) == int:
            self.pos = pos
        else:
            try:
                self.pos = self.str_to_pos(pos)
            except ValueError as e:
                logger.warn(f'Could not parse {pos} to pos: {e}')
                self.pos = -1

    def __repr__(self):
        return f'Move([{self.pos_to_str()}] c={self.color} (pos={self.pos})'

    def pos_to_str(self):
        chars = 'abcdefgh'

        row = 7 - int(self.pos / 8)
        col = 7 - (self.pos % 8)

        if row < 0:
            row = -row
        if col < 0:
            col = -col

        c = chars[col]
        return f'{c}{row + 1}'

    def str_to_pos(self, s):
        """Converts a string to a position, e.g. h4, e2"""
        chars = 'abcdefgh'
        x = 7 - chars.index(s[0])
        y = 8 - int(s[1])

        pos = (y * 8) + x

        if pos < 0 or pos > 63:
            raise ValueError(f'Position {pos} is out of bounds.')

        return pos


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

    def __repr__(self):
        return f'BitBoard(color={self.color} ({self.color}, bits={self.bits} ({np.binary_repr(self.bits, 64)}))'

    def set_bit(self, pos) -> None:
        """
        Sets the bit at the desired position to 1.
        :param pos: Bit position to set. Range 0 to 63 inclusive. Throws ValueError if pos is outside that bound.
        """
        if pos < 0 or pos > 63:
            raise ValueError(f'Expected pos between 0 and 63 inclusive. Received {pos}')

        mask = np.uint64(np.uint64(1) << np.uint64(pos))
        self.bits |= mask

    def get_bit_state(self, p):
        mask = np.uint64(1) << np.uint64(p)
        return (self.bits & mask) != 0

    def disable_bit(self, p):
        mask = np.uint64(np.uint64(1) << np.uint64(p))
        self.bits &= ~mask

    def bitcount(self):
        return self.binary_repr().count('1')

    def binary_repr(self) -> str:
        return np.binary_repr(self.bits, 64)

    def apply_move(self, m: Move):
        self.set_bit(m.pos)


class GameBoard:
    def __init__(self, player_board: BitBoard, opp_board: BitBoard):
        self.p_color = player_board.color
        self.o_color = opp_board.color
        self.player_board = player_board
        self.opp_board = opp_board
        self.current_player = -1  # Black moves first

    def __repr__(self):
        return f'GameBoard(player_board={self.player_board}, opp_board={self.opp_board})'

    def legal_moves(self, c):
        """Returns a list of all possible moves for the given bitboard"""
        r = []
        bb = self._get_bitboard(c)
        op_bb = self._get_bitboard(-c)
        move_mask = self._generate_move_mask(bb, op_bb)
        for i in range(64):
            mask = np.uint64(1 << i)
            if (mask & move_mask) != 0:
                r.append(Move(bb.color, i))

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

    def apply_move(self, m: Move):
        bb = self._get_bitboard(m.color)
        bb.apply_move(m)

        self._set_for_color(bb)
        self._line_cap(m)
        self.current_player = -self.current_player

    def is_game_complete(self):
        p_bits = self.player_board.bits
        o_bits = self.opp_board.bits

        p_legal = self._generate_move_mask(self.player_board, self.opp_board)
        o_legal = self._generate_move_mask(self.opp_board, self.player_board)

        return (p_legal == 0 and o_legal == 0) or (p_bits | o_bits) == UNIVERSE

    def _generate_move_mask(self, p, o):
        current_board = p.bits
        opponent_board = o.bits

        # Initialize an empty bitboard to store the legal moves
        legal_moves_board = np.uint64(0)

        # Loop over all squares on the board
        for square in range(64):
            # If the square is already occupied, it's not a legal move
            if ((current_board >> np.uint64(square)) & np.uint64(1)) or ((opponent_board >> np.uint64(square)) & np.uint64(1)):
                continue

            # Check each direction for a potential capture
            for direction in [-9, -8, -7, -1, 1, 7, 8, 9]:
                # Initialize variables to keep track of the current position and potential captures
                pos = square + direction
                num_captures = 0
                captures_board = np.uint64(0)

                # Move along the current direction until a capture is found or the edge of the board is reached
                while (pos >= 0) and (pos < 64) and ((pos % 8 != 0) or (direction not in [-9, -1, 7])) and (
                        (pos % 8 != 7) or (direction not in [-7, 1, 9])):
                    # If the square is empty, it's not a capture
                    if not ((current_board >> np.uint64(pos)) & np.uint64(1)) and not ((opponent_board >> np.uint64(pos)) & np.uint64(1)):
                        break

                    # If the square is occupied by the opponent, add it to the captures
                    if (opponent_board >> np.uint64(pos)) & np.uint64(1):
                        num_captures += 1
                        captures_board |= np.uint64(1) << np.uint64(pos)

                    # If the square is occupied by the current player, a capture has been found
                    if (current_board >> np.uint64(pos)) & np.uint64(1):
                        if num_captures > 0:
                            legal_moves_board |= np.uint64(1) << np.uint64(square)
                        break

                    # Move to the next square along the current direction
                    pos += direction

        return legal_moves_board

    def _line_cap(self, move: Move):
        pos = np.uint64(move.pos)
        bitboard = self._get_bitboard(move.color)
        opp_board = self._get_bitboard(opposite(move.color))

        for direction in range(DIRECTION_COUNT):
            direction_mask = DIR_MASKS[direction]
            increment = DIR_INCREMENTS[direction]
            flipped = False

            # check the first piece in the given direction
            pos_to_check = np.uint64(pos + increment)
            if (pos_to_check > 63) or (pos_to_check < 0):
                continue
            if (direction_mask & (np.uint64(1) << pos_to_check)) == 0:
                continue
            if not opp_board.get_bit_state(pos_to_check):
                continue

            # continue capturing in the direction until an empty space, same color, or edge is reached
            pos_to_flip = [pos_to_check]
            pos_to_check += increment
            pos_to_check = np.uint64(pos_to_check)
            while (pos_to_check > 0) and (pos_to_check < 63) and (direction_mask & (np.uint64(1) << pos_to_check)):
                if opp_board.get_bit_state(pos_to_check):
                    pos_to_flip.append(pos_to_check)
                elif bitboard.get_bit_state(pos_to_check):
                    for p in pos_to_flip:
                        opp_board.disable_bit(p)
                        bitboard.set_bit(p)
                    flipped = True
                    break
                else:
                    break

                pos_to_check += increment

            if flipped:
                self._set_for_color(bitboard)
                self._set_for_color(opp_board)

    def _get_opposite_board(self, b: BitBoard):
        if b.color == self.p_color:
            return self.opp_board

        return self.player_board

    def _update_hold_mask(self, hold_mask, i):
        if DIR_INCREMENTS[i] > 0:
            hold_mask = np.uint64(hold_mask << DIR_INCREMENTS[i]) & DIR_MASKS[i]
        else:
            hold_mask = np.uint64(hold_mask >> -DIR_INCREMENTS[i]) & DIR_MASKS[i]
        return hold_mask

    def count_pieces(self, c):
        return int(self._get_bitboard(c).bits.count('1'))

    def _set_for_color(self, b: BitBoard):
        """Updates bitboard based on color"""
        if b.color == self.player_board.color:
            self.player_board = b
        else:
            self.opp_board = b
