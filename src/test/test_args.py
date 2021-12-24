import unittest
from core import parse_args

class TestArgs(unittest.TestCase):
    def test_program_args(self):
        args = ['-ref', '-t 600', '-c 1', '-i', '-g', '-l test_logs']
        parser = parse_args(args)
        print(parser)

if __name__ == '__main__':
    unittest.main()
