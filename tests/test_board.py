# -*- coding: utf-8 -*-
import sys
sys.path.append(r"..")

import unittest
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
        board = Board(size=5, first_player=1)
        for i in range(5):
            board.move(i, 1)  # 纵向连五
        self.assertEqual(board.get_winner(), 1)
        board.undo(5)
        for i in range(0, 25, 5):  # 横向连五
            board.move(i, 1)
        self.assertEqual(board.get_winner(), 1)
        board.undo(5)
        for i in range(0, 25, 6):  # 对角线连五
            board.move(i, 1)
        self.assertEqual(board.get_winner(), 1)
        board.undo(5)
        # 白子
        for i in [1, 6, 11, 16, 21]:
            board.move(i, -1)  # 纵向连五
        self.assertEqual(board.get_winner(), -1)
        board.undo(5)
        # 中间有一个不是黑子
        board.move(0, 1)
        board.move(1, 1)
        board.move(2, 1)
        board.move(3, -1)
        board.move(4, 1)
        self.assertEqual(board.get_winner(), 0)

    def test_display(self):
        board = Board(size=5, first_player=1)
        board.move(0)
        # 此方法没有返回值，主要看是否会出错
        board.display()

    def test_get_valid_moves(self):
        board = Board(size=5, first_player=1)
        board.move(0)
        board.move(12)
        valid_moves = board.get_valid_moves()
        self.assertTrue(0 not in valid_moves)
        self.assertTrue(1 in valid_moves)
        self.assertTrue(12 not in valid_moves)

    def test_get_board_string(self):
        board = Board(size=5, first_player=1)
        board.move(0)
        self.assertEqual(board.get_board_string()[0], '1')
        self.assertEqual(board.get_board_string()[1], '0')

if __name__ == "__main__":
    unittest.main()
