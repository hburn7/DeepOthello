import unittest
from core import parse_args
from core.config import Config

class TestConfig(unittest.TestCase):
    def test_config_log_dir(self):
        target = 'test_logs'
        arg = [f'-l {target}']
        parsed = parse_args(arg)
        cfg = Config(log_dir=parsed.log_dir)
        self.assertEqual(target, cfg.log_dir)


if __name__ == '__main__':
    unittest.main()
