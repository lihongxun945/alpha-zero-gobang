# -*- coding: utf-8 -*-
from alpha_zero.pure_mcts import PureMCTS
from alpha_zero.mcts import MCTS
from alpha_zero.net import Net

class MCTSPlayer:
  def __init__(self, board, simulation_num=400, net=None):
    if (net is None):
      net = Net(board.size)
      net.load('checkpoint/best_checkpoint.h5')
    self.mcts = MCTS(board=board, net=net, simulation_num=simulation_num, self_play=False)

  def move(self):
    return self.mcts.move(temp=0)
'''
帮我用python3写一个类HumanPlayer，作用是让人类玩家下棋，实现以下方法：
1. __init__: 初始化方法，需要传入board
2. move: 从控制台读取玩家的输入，返回玩家的落子位置，输入的是棋盘的横纵坐标，用空格或者逗号分隔，返回的是一个整数表示落子位置.注意要用 get_valid_moves 验证玩家落子是否合法
board 中有一个方法 get_size 可以返回棋盘的大小
'''

# 以下是Chatgpt4.0 写的代码
class HumanPlayer:
  def __init__(self, board):
    self.board = board

  def move(self, player=1):
    valid_moves = self.board.get_valid_moves()
    while True:
      user_input = input("Please enter your move (x,y): ")
      user_input = user_input.replace(',', ' ').split()
      if len(user_input) != 2:
        print("Invalid input. Please enter two numbers separated by a space or comma.")
        continue
      x, y = int(user_input[0]), int(user_input[1])
      position = x * self.board.get_size() + y
      if position in valid_moves:
        return position
      else:
        print("Invalid move. Please enter a valid move.")


'''
帮我用python3写一个类PureMCTSPlayer, 使用上面写的PureMCTS实现一个简单的AI，实现以下方法：
1. __init__: 初始化方法，需要传入board
2. move: 调用PureMCTS返回玩家的落子位置，返回的是一个整数表示落子位置
'''
class PureMCTSPlayer:
  def __init__(self, board, simulation_num=1000):
    self.mcts = PureMCTS(board, simulation_num)

  def move(self):
    return self.mcts.move(None, True)
