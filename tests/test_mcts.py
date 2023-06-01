# -*- coding: utf-8 -*-
'''
帮我给下面这段代码写一个单元测试，{粘贴的MCTS代码}
'''

import sys

sys.path.append(r"..")
import unittest
from alpha_zero.board import Board
from alpha_zero.mcts import MCTS
from alpha_zero.net import Net

class TestMCTS(unittest.TestCase):

  def test_move(self):
    # 创建一个模拟的 net
    board_size = 5
    net = Net(board_size)

    # 创建一个 Board 对象
    board = Board(board_size)

    # 创建 MCTS 对象
    mcts = MCTS(board=board, net=net, simulation_num=100)

    # 进行一个 move 操作
    action = mcts.move()

    # 验证 action 在正确的范围内
    self.assertTrue(0 <= action < 25)

if __name__ == '__main__':
  unittest.main()
