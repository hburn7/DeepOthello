import sys
import pyfiglet
from config import Config
from core import config, logger

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
