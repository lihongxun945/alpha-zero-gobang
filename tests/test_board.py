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
        manuals = [
            [5, [0, 5, 1, 6, 2, 7, 3, 8, 4], 1], # 横向五
            [5, [0, 1, 5, 2, 10, 3, 15, 4, 20], 1], # 纵向五
            [5, [0, 1, 6, 2, 12, 3, 18, 4, 24], 1], # 斜线五
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
