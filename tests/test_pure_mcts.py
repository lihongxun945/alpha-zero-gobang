# -*- coding: utf-8 -*-
import sys

sys.path.append(r"..")
import unittest
from alpha_zero.board import Board
from alpha_zero.pure_mcts import PureMCTS

'''
给PureMCTS写一个测试用例，要用 unittest
'''

manuals = [
  # - - - - - -
  # - - - - - -
  # o o o o - -
  # - x x x - -
  # - - x - - -
  # - - - - - -
  #
  [6, [12, 19, 13, 20, 14, 21, 15, 26], 1, [16]],
  # - - - - - -
  # - - - - - -
  # o o o o - -
  # - x x x - -
  # - - - - - -
  # - - - - - -
  #
  [6, [12, 19, 13, 20, 14, 21, 15], -1, [16]],
  # - - - - - -
  # - - - - - -
  # o o o - - -
  # - x x x - -
  # - - o - - -
  # - - - - - -
  [6, [12, 19, 13, 20, 14, 21, 26], -1, [22]],
  # - - - - - -
  # - - - - - -
  # - o o o - -
  # - x x x - -
  # - - - - - -
  # - - - - - -
  [6, [13, 19, 14, 20, 15, 21], 1, [16]],
  # - - - - - -
  # o - x - - -
  # o - x - - -
  # o - x - - -
  # x - - o - -
  # - - - - - -
  [6, [6, 14, 12, 20, 18, 24, 27, 8], 1, [2, 26]],
]


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
    for size, moves, color, actions in manuals:
      board = Board(size)  # Initialize a 5x5 board
      mcts = PureMCTS(board, 5000)  # Initialize a MCTS with 100 simulations
      for move in moves:
        board.move(move)
      m = mcts.move(None, False)
      print('check actions: ', m, 'in', actions)
      self.assertTrue(m in actions)


if __name__ == '__main__':
  unittest.main()
