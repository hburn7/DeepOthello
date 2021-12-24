from pathlib import Path

from core.logger import Logger
from othello import color

class Config:
    def __init__(self, referee_compatibility: bool = False, ai_game_time: int = 600, ai_color: int = color.BLACK,
                 interactive=False, gui=False, log_dir='./logs'):
        """
        Settings for program behavior. All configuration options
        are handled through program arguments.
        :param referee_compatibility: Whether to have all output be in a format compatible with the CSCI_312 referee
        :param ai_game_time: How long the AI has to play a full game, in seconds
        :param ai_color: The color for the AI
        :param interactive: Whether to play the game interactively. Human Vs. AI.
        :param gui: Whether to launch a graphical interface for gameplay (not implemented yet)
        :param log_dir: Directory location for all log files to be saved in
        """
        self.ref_compatibility = referee_compatibility
        self.ai_game_time = ai_game_time
        self.ai_color = ai_color
        self.interactive = interactive
        self.gui = gui
        self.log_dir = log_dir.strip()

        _logger = Logger(self.log_dir)
        self.active_logger = _logger.referee_logger if self.ref_compatibility else _logger.standard_logger

        self._init_log_dir()
        self.active_logger.debug(f'Initialized {self}')

    def __repr__(self):
        return f'Config(referee_compatibility={self.ref_compatibility}, ai_game_time={self.ai_game_time}, ' \
               f'ai_color={self.ai_color} ({color.as_str(self.ai_color)}), interactive={self.interactive}, gui={self.gui}, ' \
               f'log_dir={self.log_dir})'

    def _init_log_dir(self):
        p = Path(f'./{self.log_dir}')
        if not p.exists():
            p.mkdir()

