import logging
from logging import FileHandler, Formatter

class Logger:
    def __init__(self, log_dir):
        self.log_dir = log_dir

        STD_LOG_FORMAT = "%(asctime)s [%(levelname)s]: %(message)s"
        REF_LOG_FORMAT = "C %(asctime)s [%(levelname)s]: %(message)s"

        REF_LOG_FILE = f'{self.log_dir}/deepothello_referee.log'
        STD_LOG_FILE = f'{self.log_dir}/deepothello_standard.log'

        LOG_LEVEL = logging.DEBUG

        # Referee logger
        self.referee_logger = logging.getLogger('deepothello.referee')
        self.referee_logger.setLevel(LOG_LEVEL)
        _referee_logger_file_handler = FileHandler(REF_LOG_FILE)
        _referee_logger_file_handler.setLevel(LOG_LEVEL)
        _referee_logger_file_handler.setFormatter(Formatter(REF_LOG_FORMAT))
        self.referee_logger.addHandler(_referee_logger_file_handler)

        # Standard logger
        self.standard_logger = logging.getLogger('deepothello.standard')
        self.standard_logger.setLevel(LOG_LEVEL)
        _standard_logger_file_handler = FileHandler(STD_LOG_FILE)
        _standard_logger_file_handler.setLevel(LOG_LEVEL)
        _standard_logger_file_handler.setFormatter(Formatter(STD_LOG_FORMAT))
        self.standard_logger.addHandler(_standard_logger_file_handler)

