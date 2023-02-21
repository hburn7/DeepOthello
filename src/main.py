import sys
import pyfiglet
import random
from othello.game_logic import GameBoard, BitBoard
from othello import color
from core import config
from src.core.logger import logger
from core.config import Config



def greeting():
    """
    :return: ASCII art for "DeepOthello" with speed font
    """
    return pyfiglet.figlet_format('DeepOthello', font='speed')


def greet():
    for line in greeting().splitlines():
        logger.info(line)


def main():
    # Greeting log
    greet()

    bw = BitBoard(color.WHITE)
    bb = BitBoard(color.BLACK)

    board = GameBoard(bw, bb)

    while not board.is_game_complete():
        # Make move for white
        w = board.player_board
        b = board.opp_board

        legal_w = board.legal_moves(w, b)

        # select random move
        mw = random.choice(legal_w)
        board.apply_move(w, mw)

        # print and repeat for black
        board.print()

        if not board.is_game_complete():
            legal_b = board.legal_moves(b, w)

            mb = random.choice(legal_b)
            board.apply_move(b, mb)

            board.print()

    print(f'Score: {board.player_board.bitcount()} W | B {board.opp_board.bitcount()}')

if __name__ == '__main__':
    main()
