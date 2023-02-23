from src.othello.game_logic import GameBoard, Move
from src.core.logger import logger
from copy import deepcopy
import numpy as np
import random

class MCTSNode:
    def __init__(self, board: GameBoard, parent=None, move=None):
        self.board = board
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.wins = 0
        self.untried_moves = board.legal_moves(board.current_player)

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def is_terminal_node(self):
        return self.board.is_game_complete()

    def uct_select_child(self):
        s = sorted(self.children, key=lambda c: c.wins / c.visits + np.sqrt(2 * np.log(self.visits) / c.visits))[-1]
        return s

    def add_child(self, m, board):
        n = MCTSNode(board, parent=self, move=m)
        self.untried_moves.remove(m)
        self.children.append(n)
        return n

    def update(self, result):
        self.visits += 1
        self.wins += result

    def rollout(self):
        board_copy: GameBoard = deepcopy(self.board)
        while not board_copy.is_game_complete():
            legal_moves_cur = board_copy.legal_moves(board_copy.current_player)
            if len(legal_moves_cur) != 0:
                # Cur can play
                board_copy.apply_move(random.choice(legal_moves_cur))
            else:
                board_copy.apply_pass()

        cur_count = board_copy._get_bitboard(board_copy.current_player).bitcount()
        opp_count = board_copy._get_bitboard(-board_copy.current_player).bitcount()
        if cur_count > opp_count:
            return board_copy.current_player
        elif cur_count == opp_count:
            return 0

        return -board_copy.current_player

    def __repr__(self):
        return f"Move: {self.move} | Wins: {self.wins} | Visits: {self.visits}"


class MCTS:
    def __init__(self, board: GameBoard, iter_max=100, verbose=False):
        self.root = MCTSNode(board)
        self.iter_max = iter_max
        self.verbose = verbose

    def search(self) -> Move:
        for i in range(self.iter_max):
            node = self.tree_policy(self.root)
            result = node.rollout()
            self.backup(node, result)

        if self.verbose:
            for c in sorted(self.root.children, key=lambda c: c.visits):
                logger.info(c)

        s = sorted(self.root.children, key=lambda c: c.visits)[-1]
        return s.move

    def tree_policy(self, node: MCTSNode):
        while not node.is_terminal_node():
            if not node.is_fully_expanded():
                return self.expand(node)
            else:
                if len(node.children) == 0:
                    result = node.rollout()
                    self.backup(node, result)
                    return node
                else:
                    node = node.uct_select_child()
        return node

    def expand(self, node: MCTSNode):
        m = random.choice(node.untried_moves)
        board_copy: GameBoard = deepcopy(node.board)
        board_copy.apply_move(m)
        return node.add_child(m, board_copy)

    def backup(self, node: MCTSNode, result):
        while node is not None:
            node.update(result)
            node = node.parent