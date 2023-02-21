from pathlib import Path

from src.core.logger import logger
from src.othello import color


class Config:
    def __init__(self, ai_game_time: int = 600, ai_color: int = color.BLACK,
                 interactive=False, gui=False):
        """
        Settings for program behavior. All configuration options
        are handled through program arguments.
        :param ai_game_time: How long the AI has to play a full game, in seconds
        :param ai_color: The color for the AI
        :param interactive: Whether to play the game interactively. Human Vs. AI.
        :param gui: Whether to launch a graphical interface for gameplay (not implemented yet)
        :param log_dir: Directory location for all log files to be saved in
        """
        self.ai_game_time = ai_game_time
        self.ai_color = ai_color
        self.interactive = interactive
        self.gui = gui

    def __repr__(self):
        return f'Config(ai_game_time={self.ai_game_time}, ' \
               f'ai_color={self.ai_color} ({color.as_str(self.ai_color)}), interactive={self.interactive}, gui={self.gui}, ' \
               f'log_dir={self.log_dir})'



