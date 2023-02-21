import sys
import logging
from pathlib import Path
from logging import FileHandler, StreamHandler, Formatter


def _init_log_dir():
    # Assumes root path [Path('.')] is equal to "DeepOthello/".
    p = Path(f'./logs')
    if not p.exists():
        p.mkdir()


def get_logger(name):
    """
    Constructs a logger with the given name.
    """
    fmt = "%(asctime)s [%(levelname)s]: %(message)s in %(pathname)s:%(lineno)d"

    file = f'logs/deepothello.log'
    log_level = logging.DEBUG

    logger = logging.getLogger(name)
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


_init_log_dir()
logger = get_logger('deepothello')
