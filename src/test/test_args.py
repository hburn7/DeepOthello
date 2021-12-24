import unittest
from core import parse_args, cfg

class TestArgs(unittest.TestCase):
    def test_program_args(self):
        args = ['-ref', '-t 600', '-c 1', '-i', '-g', '-l test_logs']
        config = cfg(args)
        self.assertTrue(config.ref_compatibility)
        self.assertTrue(config.ai_game_time == 600)
        self.assertTrue(config.ai_color == 1)
        self.assertTrue(config.interactive)
        self.assertTrue(config.gui)
        self.assertTrue(config.log_dir == 'test_logs')

    def test_invalid_color(self):
        bad_args = ['-c 0', '-c -2', '-c 2']

        for a in bad_args:
            try:
                _ = cfg(a)
            except:
                continue

            self.assertTrue(False, f'Expected exception.')

if __name__ == '__main__':
    unittest.main()
