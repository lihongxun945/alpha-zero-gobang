# -*- coding: utf-8 -*-
'''
把Node类改一下，需要结合神经网络的增加两个参数 P和Q，分别是神经网络预测的当前概率和得分，改动点：
1. 增加 P 和 Q 两个属性
2. 并且在select函数的公式中加上p和v进行计算，公式请参阅alpha zero的论文，公式大约是这样的：self.c_puct * self.P * sqrt(total_count)/(1 + self.N) + self.Q
3. 在update的时候需要同时更新Q，Q计算公式 (self.N * self.Q + value)/(self.N + 1)
把PureMCTS 改一下，结合 神经网络进行搜索，具体的改动点是：
1. __init__ 方法中增加一个 net 参数
2. _simulate 函数中不用模拟到游戏结束，如果碰到叶节点，直接调用 self.net.predict 方法获取拓展的子节点
'''

import numpy as np

c_puct = 1

class Node:
  def __init__(self, parent, P=0, Q=0):
    self.N = 1  # visit count
    self.Q = Q  # mean action value
    self.P = P  # prior probability

    self.parent = parent
    self.children = {}

  def is_leaf(self):
    return self.children == {}

  def is_root(self):
    return self.parent is None

  def select(self, total_count):
    return max(self.children.items(),
               key=lambda act_node: act_node[1].Q + c_puct * act_node[1].P * (np.sqrt(total_count) / (1 + act_node[1].N)))

  def expand(self, action_priors, v):
    for action in range(0, len(action_priors)):
      prob = action_priors[action]
      if action not in self.children:
        self.children[action] = Node(self, P=prob, Q=v)

  def update(self, value):
    self.N += 1
    self.Q = (self.N * self.Q + value) / (self.N + 1)

  def update_recursive(self, value):
    if not self.is_root():
      self.parent.update_recursive(-value)
    self.update(value)

class MCTS:
  def __init__(self, board, net, simulation_num=1600):
    self.root = Node(None)
    self.board = board
    self.net = net
    self.simulation_num = simulation_num
    self.c_puct = c_puct

  def _simulate(self):
    node = self.root
    board_copy = self.board.copy()

    while True:
      if node.is_leaf():
        if board_copy.is_game_over():
          break
        train_data = board_copy.get_data()
        train_data = np.expand_dims(train_data, axis=0)  # 转换为四维张量，因为模型需要 batch 维度
        action_probs, v = self.net.predict(train_data)
        node.expand(action_probs[0], v[0][0])
      action, node = node.select(self.c_puct)
      board_copy.move(action)

    return board_copy.get_winner()

  def _backpropagate(self, leaf_value):
    self.root.update_recursive(-leaf_value)

  def move(self, color=None):
    for _ in range(self.simulation_num):
      leaf_value = self._simulate()
      self._backpropagate(leaf_value)

    return max(self.root.children.items(), key=lambda act_node: act_node[1].N)[0]

  def update_with_move(self, last_move):
    if last_move in self.root.children:
      self.root = self.root.children[last_move]
      self.root.parent = None
    else:
      self.root = Node(None)

  def set_board(self, board):
    self.board = board

  def __str__(self):
    return "AI player, using pure Monte Carlo Tree Search algorithm"

