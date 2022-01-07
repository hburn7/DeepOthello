import argparse
import sys
from .config import Config
from othello import color


def parse_args(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='DeepOthello, created by Harry Burnett & Eric Dunbar. '
                                                 'Specify configuration options if desired.')
    parser.add_argument('-ref', '--referee_compatible', action='store_true',
                        help='Toggles logging in a way that is '
                             'compatible with the CSCI 312 referee. If you aren\'t '
                             'sure what this means, it can be left alone.')
    parser.add_argument('-t', '--ai_game_time', metavar='N', type=int, default=600,
                        help='Total time in seconds that is allotted to the AI '
                             'for the entire game. The higher this value, the longer '
                             'it will think about the move it makes.',
                        choices=[x for x in range(1, 86400)])  # 1 second to 24hrs
    parser.add_argument('-c', '--ai_color', metavar='N_COLOR', type=int, default=color.BLACK, choices=[-1, 1],
                        help='The color the AI should play as. -1 for Black and 1 for White. '
                             'If interactive, the human player will be assigned the opposite color.')
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='Toggles playing the game interactively. '
                             'The human player would play against the AI with this setting enabled. '
                             'Default behavior is AI vs. AI.')
    parser.add_argument('-g', '--gui', action='store_true',
                        help='Toggles playing through the GUI. (Currently not implemented)')
    parser.add_argument('-l', '--log_dir', default='logs',
                        help='Alters log directory to specified directory. Input should be '
                             'an absolute path or relative path to the project\'s root directory.')
    return parser.parse_args(args)

def init_config():
    args = sys.argv[1:]
    parsed = parse_args(args)
    return config.Config(referee_compatibility=parsed.referee_compatible, ai_game_time=parsed.ai_game_time, ai_color=parsed.ai_color,
                  interactive=parsed.interactive, gui=parsed.gui, log_dir=parsed.log_dir)

cfg = init_config()
logger = cfg.active_logger
