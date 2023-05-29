# -*- coding: utf-8 -*-
import sys
sys.path.append(r"..")
import unittest
from alpha_zero.board import Board
from alpha_zero.pure_mcts import PureMCTS

'''
给PureMCTS写一个测试用例，要用 unittest
'''

class TestPureMCTS(unittest.TestCase):
    def test_simulation(self):
        board = Board(6)  # Initialize a 5x5 board
        mcts = PureMCTS(board, simulation_num=200)  # Initialize a MCTS with 100 simulations
        board.move(0)
        mcts._simulate()
        # The root should be visited
        self.assertTrue(mcts.root.visit_count > 0)
        # At least one child of the root should be visited
        self.assertTrue(any(node.visit_count > 0 for node in mcts.root.children.values()))
    # 测试action
    def test_actions(self):
        manuals = [
          #- - - - - -
          #- - - - - -
          #o o o o - -
          #- x x x - -
          #- - x - - -
          #- - - - - -
          #
          [[12, 19, 13, 20, 14, 21, 15, 26], 1, 16],
          #- - - - - -
          #- - - - - -
          #o o o o - -
          #- x x x - -
          #- - - - - -
          #- - - - - -
          #
          [[12, 19, 13, 20, 14, 21, 15], -1, 16],
          #- - - - - -
          #- - - - - -
          #o o o - - -
          #- x x x - -
          #- - o - - -
          #- - - - - -
          [[12, 19, 13, 20, 14, 21, 26], -1, 22],
          #- - - - - -
          #- - - - - -
          #- o o o - -
          #- x x x - -
          #- - - - - -
          #- - - - - -
          [[13, 19, 14, 20, 15, 21], 1, 16],
        ]
        for moves, color, action in manuals:
          board = Board(6)  # Initialize a 5x5 board
          mcts = PureMCTS(board, simulation_num=400)  # Initialize a MCTS with 100 simulations
          for move in moves:
            board.move(move)
          self.assertTrue(mcts.move() == action)

if __name__ == '__main__':
    unittest.main()