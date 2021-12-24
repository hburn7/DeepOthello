import sys
from core import parse_args, config

def main():
    args = sys.argv[1:]
    print(parse_args(args))
    print(config)


if __name__ == '__main__':
    main()
