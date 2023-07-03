# -*- coding: utf-8 -*-
import sys

sys.path.append(r"..")
import unittest
from alpha_zero.board import Board
from alpha_zero.mcts import MCTS
from alpha_zero.net import Net

# 这里可以自己做一些专门的测试，帮助发现问题
class CustomTest(unittest.TestCase):

  def test_mcts(self):
    # 创建一个模拟的 net
    board_size = 6
    win_count = 4
    net = Net(board_size)

    # - - - - - -
    # - - - O O O
    # X X - - - -
    # - - - - - -
    # - - - - - -
    # 创建一个 Board 对象
    board = Board(size=board_size, win_count=win_count)
    for i in [9, 12, 10, 13, 11]:
      board.move(i)
    print(board.get_data())

    # 创建 MCTS 对象
    mcts = MCTS(board=board, net=net, simulation_num=100)

    action = mcts.move(temp=0)
    print(action)

    # 验证 action 在正确的范围内
    self.assertTrue(action == 8)

if __name__ == '__main__':
  unittest.main()
