import unittest
import os
from pathlib import Path
from core.logger import Logger
from core.config import Config

class TestLogger(unittest.TestCase):
    def test_referee_logger(self):
        cfg = Config(referee_compatibility=True, log_dir='./test_logs')
        logger = Logger(cfg.log_dir)

        ref_path = Path(f'{logger.log_dir}/deepothello_referee.log')

        self.assertTrue(os.path.exists(logger.log_dir), f'Expected path \'{logger.log_dir}\' to exist.')
        self.assertTrue(cfg.ref_compatibility, f'Expected cfg.ref_compatibility==True but received {cfg.ref_compatibility}')

        msg = 'Hello world!'
        logger.referee_logger.debug(msg=msg)

        self.assertTrue(ref_path.exists(), f'Expected referee log file \'deepothello_referee.log\' but was not found.')
        self.assertTrue(ref_path.is_file())

        with ref_path.open(mode='r') as f:
            for line in f:
                pass

            self.assertTrue(line.startswith('C'), f'Expected \'C {line}\' -- received \'{line}\' instead.')

if __name__ == '__main__':
    unittest.main()
