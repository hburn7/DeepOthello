import sys
import pyfiglet
from config import Config
from core import parse_args

def greeting():
    """
    :return: ASCII art for "DeepOthello" with speed font
    """
    return pyfiglet.figlet_format('DeepOthello', font='speed')

def main():

    args = sys.argv[1:]
    parsed = parse_args(args)
    cfg = Config(referee_compatibility=parsed.referee_compatible, ai_game_time=parsed.ai_game_time, ai_color=parsed.ai_color,
                  interactive=parsed.interactive, gui=parsed.gui, log_dir=parsed.log_dir)
    logger = cfg.active_logger

    # Greeting log
    for line in greeting().splitlines():
        logger.info(line)





if __name__ == '__main__':
    main()
