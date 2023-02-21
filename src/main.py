import sys
import pyfiglet
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
    board.print()

    legal = board.legal_moves(board.player_board, board.opp_board)
    print(legal)


if __name__ == '__main__':
    main()
