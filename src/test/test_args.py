import unittest
from core import parse_args
from core.config import Config


class TestArgs(unittest.TestCase):
    def test_program_args(self):
        args = ['-ref', '-t 600', '-c 1', '-i', '-g', '-l test_logs']
        parsed = parse_args(args)
        cfg = Config(referee_compatibility=parsed.referee_compatible, ai_game_time=parsed.ai_game_time,
                     ai_color=parsed.ai_color,
                     interactive=parsed.interactive, gui=parsed.gui, log_dir=parsed.log_dir)
        self.assertTrue(cfg.ref_compatibility)
        self.assertTrue(cfg.ai_game_time == 600)
        self.assertTrue(cfg.ai_color == 1)
        self.assertTrue(cfg.interactive)
        self.assertTrue(cfg.gui)
        self.assertTrue(cfg.log_dir == 'test_logs')

    def test_invalid_color(self):
        bad_args = ['-c 0', '-c -2', '-c 2']

        for a in bad_args:
            try:
                parsed = parse_args(a)
                _ = Config(ai_color=parsed.ai_color)
            except:
                continue

            self.assertTrue(False, f'Expected exception.')


if __name__ == '__main__':
    unittest.main()
