# -*- coding: utf-8 -*-
import sys

sys.path.append(r"..")

import unittest
import numpy as np
from alpha_zero.board import Board


# 以下是Chatgpt4.0 写的代码, 并做了少量修改
class TestBoard(unittest.TestCase):
  def test_init(self):
    board = Board(size=5, first_player=1)
    self.assertEqual(board.get_board_string(), '0' * 25)
    self.assertEqual(board.get_current_player_color(), 1)
    self.assertEqual(board.get_winner(), 0)

  def test_move_and_undo(self):
    board = Board(size=5, first_player=1)
    board.move(0)
    self.assertEqual(board.get_board_string()[0], '1')
    board.undo()
    self.assertEqual(board.get_board_string()[0], '0')
    board.move(0, color=-1)
    self.assertEqual(board.get_board_string()[0] + board.get_board_string()[1], '-1')
    board.undo()
    self.assertEqual(board.get_board_string()[0], '0')

  def test_get_winner(self):
    manuals = [
      [5, [0, 5, 1, 6, 2, 7, 3, 8, 4], 1],  # 横向五
      [5, [0, 1, 5, 2, 10, 3, 15, 4, 20], 1],  # 纵向五
      [5, [0, 1, 6, 2, 12, 3, 18, 4, 24], 1],  # 斜线五
      [8, [24, 36, 32, 28, 16, 8, 26, 20, 25, 12, 27, 44], -1],
    ]
    for size, actions, winner in manuals:
      board = Board(size, first_player=1)
      for i in actions:
        board.move(i)  # 纵向连五
      board.display()
      self.assertEqual(board.get_winner(), winner)

  def test_display(self):
    board = Board(size=5, first_player=1)
    board.move(0)
    # 此方法没有返回值，主要看是否会出错
    board.display()

  def test_get_valid_moves(self):
    board = Board(size=3, first_player=1)
    board.move(0)
    board.move(8)
    valid_moves = board.get_valid_moves()
    self.assertTrue(np.all(valid_moves == np.array([1, 2, 3, 4, 5, 6, 7])))
    valid_moves_mask = board.get_valid_moves_mask()
    self.assertTrue(np.all(valid_moves_mask == np.array([0, 1, 1, 1, 1, 1, 1, 1, 0])))

    # 测试如果能连五，那么只返回连五的位置
    board = Board(size=5, first_player=1)
    for i in [0, 1, 2, 3]:
      board.move(i, 1)
      board.move(i + 5, -1)
    valid_moves = board.get_valid_moves()
    self.assertTrue(np.all(valid_moves == np.array([4, 9])))
    valid_moves_mask = board.get_valid_moves_mask()
    mask = np.zeros(25)
    mask[4] = 1
    mask[9] = 1
    self.assertTrue(np.all(valid_moves_mask == np.array(mask)))


  def test_get_board_string(self):
    board = Board(size=5, first_player=1)
    board.move(0)
    self.assertEqual(board.get_board_string()[0], '1')
    self.assertEqual(board.get_board_string()[1], '0')

  def test_get_data(self):
    board = Board(size=3)

    # 模拟一系列的棋步
    board.move(0, 1)  # 黑子下在 (0,0)
    board.move(4, -1)  # 白子下在 (1,1)
    board.move(8, 1)  # 黑子下在 (2,2)
    board.move(7, -1)  # 白子下在 (2,1)

    x, y = board.get_data(7)

    # 验证棋盘状态 x
    self.assertEqual(x.shape, (17, 3, 3))  # x 的形状应为 (3, 3, 17)

    # 验证历史棋盘状态
    # 这几个平面应全为 0
    for i in [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]:
      self.assertTrue(np.all(x[i, :, :] == 0))  # 前14个平面应全为 0

    # 验证有棋子的状态
    self.assertTrue(np.all(x[6, :, :] == np.array([[1, 0, 0], [0, 0, 0], [0, 0, 0]])))
    self.assertTrue(np.all(x[7, :, :] == np.array([[1, 0, 0], [0, 0, 0], [0, 0, 1]])))
    self.assertTrue(np.all(x[14, :, :] == np.array([[0, 0, 0], [0, -1, 0], [0, 0, 0]])))
    self.assertTrue(np.all(x[15, :, :] == np.array([[0, 0, 0], [0, -1, 0], [0, -1, 0]])))

    # 验证当前玩家颜色
    self.assertTrue(np.all(x[16, :, :] == 1))  # 最后一个平面应全为 1，因为该黑棋了

    # 验证胜负情况和落子概率
    self.assertEqual(y[0], 0)  # 胜负情况应为 0，因为游戏还没结束
    self.assertTrue(np.all(y[1] == np.array([0, 0, 0, 0, 0, 0, 0, 1, 0])))  # 最后一步的落子概率应为 1，其他位置的概率应为 0

  def test_enhance_data(self):
    board = Board(size=3)
    board.move(0)  # 黑子下在 (0,0)
    board.move(2)  # 黑子下在 (0,0)
    board.move(3)  # 黑子下在 (0,0)
    x, y = board.get_data(6)
    data_original, data_horizontal_flip, data_vertical_flip = board.enhance_data(x, y)
    print('test enhance', data_original, data_horizontal_flip, data_vertical_flip)

    # 分开比较 y 的两个元素
    np.testing.assert_almost_equal(y[0], data_original[1][0])
    np.testing.assert_array_almost_equal(y[1], data_original[1][1])
    
    # 同样地，对水平翻转和垂直翻转后的数据进行比较
    np.testing.assert_almost_equal(y[0], data_horizontal_flip[1][0])
    np.testing.assert_array_almost_equal(np.flip(y[1].reshape(board.size, board.size), axis=1).flatten(), 
                                          data_horizontal_flip[1][1])
    
    np.testing.assert_almost_equal(y[0], data_vertical_flip[1][0])
    np.testing.assert_array_almost_equal(np.flip(y[1].reshape(board.size, board.size), axis=0).flatten(), 
                                          data_vertical_flip[1][1])



if __name__ == "__main__":
  unittest.main()
