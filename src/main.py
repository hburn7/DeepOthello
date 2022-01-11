import sys
import pyfiglet
from othello.game_logic import GameBoard, BitBoard
from othello import color
from core import config, logger
from core.config import Config

def greeting():
    """
    :return: ASCII art for "DeepOthello" with speed font
    """
    return pyfiglet.figlet_format('DeepOthello', font='speed')

def main():
    # Greeting log
    for line in greeting().splitlines():
        logger.info(line)


if __name__ == '__main__':
    main()
