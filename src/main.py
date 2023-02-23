import pyfiglet
import random
import numpy as np
from othello.game_logic import GameBoard, BitBoard
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


def main():
    bw = BitBoard(color.WHITE)
    bb = BitBoard(color.BLACK)

    board = GameBoard(bw, bb)

    while not board.is_game_complete():
        # Make move for white
        w = board.player_board
        b = board.opp_board

        legal_w = board.legal_moves(1)
        if len(legal_w) == 0:
            # Pass
            logger.info('White passes')
            continue

        # select random move
        mw = random.choice(legal_w)
        board.apply_move(mw)
        logger.info(f'White plays {mw}')

        # print and repeat for black
        board.print()

        if not board.is_game_complete():
            legal_b = board.legal_moves(-1)

            if len(legal_b) == 0:
                logger.info('Black passes')
                continue

            mb = random.choice(legal_b)
            board.apply_move(mb)
            logger.info(f'Black plays {mb}')

            board.print()

    print(f'Score: {board.player_board.bitcount()} W | B {board.opp_board.bitcount()}')


def play_once():
    board = GameBoard(BitBoard(1), BitBoard(-1))
    legal = board.legal_moves(-board.current_player)
    for l in legal:
        board.apply_move(l)
        board.print()
        board = GameBoard(BitBoard(1), BitBoard(-1))


def play_mcts_single():
    board = GameBoard(BitBoard(1), BitBoard(-1))
    mcts = MCTS(board, iter_max=350, verbose=True)
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

        board.apply_move(search)
        board.print()

def play_mcts_vs_random():
    board = GameBoard(BitBoard(-1), BitBoard(1))
    while not board.is_game_complete():
        legal = board.legal_moves(board.current_player)
        if len(legal) == 0:
            board.apply_pass()
            continue

        if board.current_player == -1:
            mcts = MCTS(board, iter_max=250, verbose=True)
            search = mcts.search()

            if search is None:
                board.apply_pass()
                continue

            board.apply_move(search)
            board.print()
        else:
            # Random
            board.apply_move(random.choice(legal))
            board.print()

    logger.info(f'Score: {board.player_board.bitcount()} B (agent) | W (random) {board.opp_board.bitcount()}')



if __name__ == '__main__':
    play_mcts_vs_random()
