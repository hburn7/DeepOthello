import json
import multiprocessing

import pyfiglet
import random
import numpy as np

from multiprocessing import Pool

from src.othello.game_logic import GameBoard, BitBoard, Move
from src.core.logger import logger
from src.ai.mcts import MCTS
from src.ai.state_save import StateSave, StateSaveDecoder, SavedMoveData


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


def play_mcts_full(iters=1500):
    board = GameBoard(BitBoard(-1), BitBoard(1))
    while not board.is_game_complete():
        legal = board.legal_moves(board.current_player)
        if len(legal) == 0:
            board.apply_pass()
            continue

        mcts = MCTS(board, iter_max=iters, verbose=True)
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
                f'(random) {board.opp_board.bitcount()}')


def play_mcts_interactive(display_legal=True, iterations=1200, mcts_verbose=False, assistance=False,
                          assistance_iters=650):
    logger.info('Specify color to play as... [1 for white, -1 for black]')
    color = int(input())

    # player_board = human, opp = agent
    board = GameBoard(BitBoard(color), BitBoard(-color))

    while not board.is_game_complete():
        legal = board.legal_moves(board.current_player)
        if len(legal) == 0:
            board.apply_pass()
            logger.info(f'{board.current_player} passed (forced)')
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

    logger.info(f'Score: {board.player_board.bitcount()} (human [{board.player_board.color}]) | '
                f'(agent [{board.opp_board.color}) {board.opp_board.bitcount()}')


def mcts_save_data(iters=1600) -> []:
    """Save data from MCTS games to file. Alternates random play between players each game
    to maximize saved data."""
    logger.info(f'Starting MCTS save_data session with {iters} iterations')
    random_player = 1

    decoder = StateSaveDecoder()
    logger.info('Loading previously stored data...')
    game_data = decoder.data if decoder.data is not None else []
    logger.info(f'Loaded {len(game_data)} states')

    while True:
        board = GameBoard(BitBoard(-1), BitBoard(1))

        logger.info('Starting new game...')
        move_count = 1
        try:
            while not board.is_game_complete():
                legal = board.legal_moves(board.current_player)
                if len(legal) == 0:
                    board.apply_pass()
                    continue

                if board.current_player == random_player:
                    r_move = random.choice(legal)
                    logger.info(f'{board.current_player} plays {r_move} (random)')
                    board.apply_move(r_move)
                    continue

                current = decoder.find_best_move(board.player_board.bits, board.opp_board.bits, board.current_player)
                if isinstance(current, SavedMoveData):
                    logger.info(f'Found save for move {move_count}, skipping...')
                    board.apply_move(Move(board.current_player, current.pos))
                    move_count += 1
                    continue

                mcts = MCTS(board, iter_max=iters, verbose=False)
                search_nodes = mcts.search(return_nodes=True)

                # player must be black and opp must be white
                saves = []
                for node in search_nodes:
                    saves.append(SavedMoveData(node.move.pos, node.move.pos_to_str(), node.wins, node.visits,
                                               node.wins / node.visits))

                state_save = StateSave(board.player_board.bits, board.opp_board.bits, board.current_player, saves)
                game_data.append(state_save.to_json())

                best = search_nodes[0].move

                logger.info(f'{board.current_player} plays {best}')
                board.apply_move(best)
                move_count += 1

            random_player = -random_player

            # If we are starting a new game, end here. We complete 1 game per color in this function.
            if random_player == 1:
                logger.info('Exiting save_data session')
                return game_data
        except:
            logger.exception('Aborting...')
            return game_data



def _save_data_json(game_data):
    with open('data.json', 'w') as f:
        json.dump(game_data, f, indent=4)


def save_data_multiprocessing(iters=1600):
    n_processes = multiprocessing.cpu_count()
    pool = Pool(processes=n_processes)

    results = []
    for i in range(n_processes):
        results.append(pool.apply_async(mcts_save_data, args=(iters,)))

    pool.close()
    pool.join()

    final_data = []

    for r in results:
        game_data = r.get()
        logger.info(f'Found {len(game_data)} states to save')
        for d in game_data:
            if d not in final_data:
                final_data.append(d)


    logger.info(f'Final data size: {len(final_data)} states')
    _save_data_json(final_data)
    logger.info('Saved data to file')


def mcts_player_assistance(assistance_iters, board):
    logger.info('Player assistance processing...')
    mcts = MCTS(board, assistance_iters, False)
    search = mcts.search()
    logger.info(f'Agent recommends: {search}')


def gather_data():
    """Call this function as main when gathering new game data."""
    i = 1
    while True:
        logger.info(f'Data generation loop {i}')
        save_data_multiprocessing()

        i += 1


if __name__ == '__main__':
    play_mcts_against_weak_mcts(strong_iters=1200, weak_iters=800, strong_color=-1)