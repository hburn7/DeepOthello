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

    board = GameBoard(BitBoard(color.WHITE), BitBoard(color.BLACK))
    board.print()

    logger.info('hello')


if __name__ == '__main__':
    main()
