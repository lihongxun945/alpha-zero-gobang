# -*- coding: utf-8 -*-
from alpha_zero.pure_mcts import PureMCTS

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
