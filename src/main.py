import pyfiglet
import random
import numpy as np
from othello.game_logic import GameBoard, BitBoard, Move
from othello import color
from src.core.logger import logger
from src.ai.mcts import MCTS


def greeting():
    """
    :return: ASCII art for "DeepOthello" with speed font
    """
    return pyfiglet.figlet_format('DeepOthello', font='speed')


def greet():
    for line in greeting().splitlines():
        logger.info(line)


greet()


def play_once():
    board = GameBoard(BitBoard(1), BitBoard(-1))
    legal = board.legal_moves(-board.current_player)
    for l in legal:
        board.apply_move(l)
        board.print()
        board = GameBoard(BitBoard(1), BitBoard(-1))


def play_mcts_single(iterations=350):
    board = GameBoard(BitBoard(1), BitBoard(-1))
    mcts = MCTS(board, iter_max=iterations, verbose=True)
    search = mcts.search()
    print(search)


def test_moves():
    bb1 = BitBoard(-1, np.uint64(1177713353440496642))
    bb2 = BitBoard(1, np.uint64(4611686018427387904))
    board = GameBoard(bb1, bb2)
    legal = board.legal_moves(board.current_player)
    print(legal)


def play_mcts_full():
    board = GameBoard(BitBoard(1), BitBoard(-1))
    while not board.is_game_complete():
        legal = board.legal_moves(board.current_player)
        if len(legal) == 0:
            board.apply_pass()
            continue

        mcts = MCTS(board, iter_max=250, verbose=True)
        search = mcts.search()

        if search is None:
            board.apply_pass()
            continue

        logger.info(f'{board.current_player} plays {search}')
        board.apply_move(search)
        board.print()


def play_mcts_against_weak_mcts(strong_iters=500, weak_iters=100, strong_color=1):
    board = GameBoard(BitBoard(strong_color), BitBoard(-strong_color))
    while not board.is_game_complete():
        legal = board.legal_moves(board.current_player)
        if len(legal) == 0:
            board.apply_pass()
            continue

        if board.current_player == strong_color:
            mcts = MCTS(board, iter_max=strong_iters, verbose=True)
            search = mcts.search()
            logger.info(f'(strong) {board.current_player} plays {search}')

            if search is None:
                board.apply_pass()
                logger.info('(strong) {board.current_player} passed')
                continue

            board.apply_move(search)
            board.print()
        else:
            # Weak MCTS
            mcts = MCTS(board, iter_max=weak_iters, verbose=True)
            search = mcts.search()
            logger.info(f'(weak) {board.current_player} plays {search}')

            if search is None:
                board.apply_pass()
                logger.info('(weak) {board.current_player} passed')
                continue

            board.apply_move(search)
            board.print()

    logger.info(
        f'Score: {board.player_board.bitcount()} {board.player_board.color} (strong) | {board.opp_board.color} (weak) {board.opp_board.bitcount()}')


def play_mcts_vs_random(iters=350, agent_color=1):
    board = GameBoard(BitBoard(agent_color), BitBoard(-agent_color))
    while not board.is_game_complete():
        legal = board.legal_moves(board.current_player)
        if len(legal) == 0:
            board.apply_pass()
            continue

        if board.current_player == agent_color:
            mcts = MCTS(board, iter_max=iters, verbose=True)
            search = mcts.search()
            logger.info(f'{board.current_player} plays {search}')

            if search is None:
                board.apply_pass()
                logger.info(f'{board.current_player} passed')
                continue

            board.apply_move(search)
            board.print()
        else:
            # Random
            if len(legal) == 0:
                board.apply_pass()
                logger.info(f'{board.current_player} passed')
                continue

            r_move = random.choice(legal)
            logger.info(f'{board.current_player} plays {r_move}')
            board.apply_move(r_move)
            board.print()

    logger.info(f'Score: {board.player_board.bitcount()} {board.player_board.color} (agent) | {board.opp_board.color} '
                f'(agent) {board.opp_board.bitcount()}')


def play_mcts_interactive(display_legal=True, iterations=250, mcts_verbose=False, assistance=False,
                          assistance_iters=100):
    logger.info('Specify color to play as... [1 for white, -1 for black]')
    color = int(input())
    board = GameBoard(BitBoard(color), BitBoard(-color))

    while not board.is_game_complete():
        legal = board.legal_moves(board.current_player)
        if len(legal) == 0:
            board.apply_pass()
            continue

        # Agent plays MCTS
        if board.current_player == -board.player_board.color:
            mcts = MCTS(board, iterations, mcts_verbose)
            logger.info('Agent searching...')
            search = mcts.search()
            logger.info(f'{board.current_player} plays {search}')

            if search is None:
                board.apply_pass()
                logger.info('Black passed')
                continue

            board.apply_move(search)
        else:
            if display_legal:
                logger.info(f'Legal moves: {legal}')
            if assistance:
                mcts_player_assistance(assistance_iters, board)

            board.print()
            # Interactive
            logger.info('Specify move... [e.g. a1, b2], or have agent help you with "help"')
            valid = False
            while not valid:
                move = input()
                if move == 'help':
                    mcts_player_assistance(assistance_iters, board)
                    continue
                try:
                    interactive_move = Move(board.current_player, move)
                    if interactive_move.pos not in [x.pos for x in legal]:
                        logger.info('Invalid move, please try again... [e.g. a1, b2]')
                        continue
                    valid = True
                except ValueError:
                    if move == 'help':
                        mcts_player_assistance(assistance_iters, board)
                    logger.info('Invalid move, please try again... [e.g. a1, b2]')
                    continue

            board.apply_move(interactive_move)
            logger.info(f'{board.current_player} plays {interactive_move}')
            board.print()


def mcts_player_assistance(assistance_iters, board):
    logger.info('Player assistance processing...')
    mcts = MCTS(board, assistance_iters, False)
    search = mcts.search()
    logger.info(f'Agent recommends: {search}')


if __name__ == '__main__':
    play_mcts_against_weak_mcts(500, 100, 1)
