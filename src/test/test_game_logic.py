import unittest
import numpy as np
import othello.game_logic as game_logic

from othello.game_logic import Move, BitBoard, GameBoard
from othello import color

VALID_POSITIONS = [x for x in range(64)]


class TestMove(unittest.TestCase):
    def test_default(self):
        move = Move(color.BLACK)
        self.assertTrue(move.is_pass, f'Expected default behavior to be pass. Received {move}')


class TestBitBoard(unittest.TestCase):
    def test_init(self):
        bb_black = BitBoard(color.BLACK)
        bb_white = BitBoard(color.WHITE)

        self.assertTrue(bb_black.bits == BitBoard.BLACK_BITS)
        self.assertTrue(bb_white.bits == BitBoard.WHITE_BITS)

    def test_set_bit(self):
        for p in VALID_POSITIONS:
            copy = BitBoard(color.BLACK)
            copy.set_bit(p)
            reference = BitBoard.BLACK_BITS | np.uint64(1 << p)
            self.assertTrue(copy.bits == reference)

        bad = [-1, 65]
        for p in bad:
            copy = BitBoard(color.BLACK)
            self.assertRaises(ValueError, copy.set_bit, p)

    def test_get_bit_state(self):
        for p in VALID_POSITIONS:
            copy = BitBoard(color.BLACK)
            copy.set_bit(p)
            self.assertTrue(copy.get_bit_state(p))

    def test_disable_bit(self):
        for p in VALID_POSITIONS:
            copy = BitBoard(color.BLACK)
            copy.disable_bit(p)
            self.assertFalse(copy.get_bit_state(p), f'Expected bit to be disabled. Received {copy.get_bit_state(p)} instead. '
                                                    f'Pos: {p} | Bits: {copy.binary_repr()}')

    def test_bitcount(self):
        # Initial count
        copy = BitBoard(color.BLACK)
        self.assertTrue(copy.bitcount() == 2, f'Expected bitcount to equal 2. Received {copy.bitcount()}')

        # All positions occupied by one color would never occur in a real game.
        for p in VALID_POSITIONS:
            copy.set_bit(p)

        self.assertTrue(copy.bitcount() == 64)

        # Disable all
        for p in VALID_POSITIONS:
            copy.disable_bit(p)

        self.assertTrue(copy.bitcount() == 0)

    def test_get_bitboard(self):
        black = BitBoard(color.BLACK)
        white = BitBoard(color.WHITE)

        # Test black retrieval
        board = GameBoard(black, white)
        result = board._get_bitboard(color.BLACK)
        self.assertTrue(black.bits == result.bits)

        # Test white retrieval
        board = GameBoard(white, black)
        result = board._get_bitboard(color.WHITE)
        self.assertTrue(white.bits == result.bits)


if __name__ == '__main__':
    unittest.main()
