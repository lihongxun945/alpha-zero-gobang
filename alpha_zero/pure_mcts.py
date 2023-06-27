# -*- coding: utf-8 -*-
'''
帮我用python3写一个类PureMCTS, 实现蒙特卡洛搜索算法的五子棋AI，实现以下方法：
1. __init__: 初始化方法，需要传入simulation_num 表示模拟次数，board是棋盘
2. move: 传入当前玩家的颜色，返回落子位置，返回的是一个整数表示落子位置。 如果没有传入颜色，则默认用board.get_current_player_color()获取当前玩家颜色
'''

import numpy as np
import random
import math
from collections import defaultdict


class Node:
  def __init__(self, parent=None):
    self.parent = parent
    self.children = dict()  # {move: Node}
    self.visit_count = 1
    self.q_value = 0.0

  def is_leaf(self):
    return len(self.children) == 0

  def is_root(self):
    return self.parent is None

  def get_value(self):
    return self.q_value / self.visit_count

  def expand(self, action_priors):
    for action, _ in action_priors:
      if action not in self.children:
        self.children[action] = Node(parent=self)

  def select(self):
    return max(self.children.items(),
               key=lambda node: node[1].get_value() + math.sqrt(math.log(self.N) / node[1].visit_count))

  def update(self, reward):
    self.visit_count += 1
    self.q_value += reward

  def update_recursive(self, reward):
    self.update(reward)
    if not self.is_root():
      self.parent.update_recursive(-reward)

  def display(self):
    for action, node in self.children.items():
      print(f"Action: {action}, Value: {node.q_value}, Visit Count: {node.visit_count}")

  def display_tree(self, depth=0, action=-1):
    print('  ' * depth + f'Node: {action} Visit count: {self.visit_count}')
    for action, node in self.children.items():
      node.display_tree(depth + 1, action)

  def get_visit_count(self):
    return self.visit_count


class PureMCTS:
  def __init__(self, board, simulation_num=1000):
    self.root = Node()
    self.board = board
    self.simulation_num = simulation_num

  def _simulate(self, color=None):
    board_copy = self.board.copy()
    node = self.root
    if color is None:
      color = board_copy.get_current_player_color()

    while board_copy.get_winner() == 0:
      valid_moves = board_copy.get_valid_moves()
      if len(valid_moves) == 0:
        break
      if node.is_leaf():
        node.expand([(move, 1.0) for move in valid_moves])
      move, node = node.select()
      board_copy.move(move, color)
      color = -color

    winner = board_copy.get_winner()
    node.update_recursive(-winner if color == 1 else winner)
    return winner

  def move(self, color=None, verbose=False):
    self.root = Node()  # reset the root node
    if color is None:
      color = self.board.get_current_player_color()

    black_wins = 0
    white_wins = 0
    draws = 0
    for _ in range(self.simulation_num):
      winner = self._simulate(color)
      if winner == 1:
        black_wins += 1
      elif winner == -1:
        white_wins += 1
      else:
        draws += 1
    if verbose:
      print('results:', 'black wins', black_wins, 'white wins', white_wins, 'draws', draws)
      print('root:', self.root.get_visit_count())
      self.root.display()
      self.board.display()
    move = max(self.root.children.items(), key=lambda node: node[1].get_visit_count())
    return move[0]

  def set_board(self, board):
    self.board = board
