import sys
import logging
from logging import FileHandler, StreamHandler, Formatter


class Logger:
    """Class for logging messages to stdout and to log files. Contains different types of Logger
    as class variables that will all point to the specified log_dir."""
    def __init__(self, log_dir):
        """
        Constructs a logger to log to the specified directory.
        :param log_dir: Directory to send log files to.
        """
        self.log_dir = log_dir
        self.standard_logger = self.get_logger('standard')
        self.referee_logger = self.get_logger('referee', True)

    def get_logger(self, name, is_ref=False):
        """
        Constructs a logger with the given name.
        :param name: The name of the logger. Always assigned as 'deepothello.(name)' in the logger itself.
        :param is_ref: Whether to save logs and output in format compatible with CSCI 312 referee.
        """
        fmt = "%(asctime)s [%(levelname)s]: %(message)s in %(pathname)s:%(lineno)d"
        if is_ref:
            fmt = f'C {fmt}'

        file = f'{self.log_dir}/deepothello_{name}.log'
        log_level = logging.DEBUG

        logger = logging.getLogger(f'deepothello.{name}')
        logger.setLevel(log_level)

        file_handler = FileHandler(file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(Formatter(fmt))

        stream_handler = StreamHandler(sys.stdout)
        stream_handler.setLevel(log_level)
        stream_handler.setFormatter(Formatter(fmt))

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        return logger
