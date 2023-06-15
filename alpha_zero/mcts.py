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
import time

c_puct = 1
enable_cache = True
show_search_debug_info = False

class Node:
  def __init__(self, parent=None, P=0, Q=0, action=None):
    self.N = 1  # visit count
    self.Q = Q  # mean action value
    self.P = P  # prior probability
    self.action = action # 移动位置

    self.parent = parent
    self.children = dict()

  def is_leaf(self):
    return len(self.children) == 0

  def is_root(self):
    return self.parent is None

  def select(self, total_count):
    action, node = max(self.children.items(),
               key=lambda act_node: act_node[1].Q + c_puct * act_node[1].P * (np.sqrt(total_count) / (1 + act_node[1].N)))
    return action, node

  def expand(self, action_priors, v=0):
    for action in range(0, len(action_priors)):
      prob = action_priors[action]
      if action not in self.children:
        if prob > 0:
          self.children[action] = Node(parent=self, P=prob, Q=v, action=action)

  def update(self, value):
    if show_search_debug_info:
      if self.action:
        print('update node:', self.action//11, self.action%11, value)
      else:
        print('update root node:', value)
    self.N += 1
    self.Q = (self.N * self.Q + value) / (self.N + 1)

  def update_recursive(self, value):
    if not self.is_root():
      self.parent.update_recursive(-value)
    self.update(value)

class MCTS:
  def __init__(self, board, net, simulation_num=1000, self_play=False):
    self.root = Node(None)
    self.board = board
    self.net = net
    self.simulation_num = simulation_num
    self.c_puct = c_puct
    self.self_play = self_play

    # performance
    self.reset()

  def reset(self):
    self.performance_start_time = time.time()
    self.performance_predict_time = 0
    self.performance_predict_count = 0
    self.predict_cache = {}
    self.predict_cache_hit = 0

  def displayPerformance(self):
    print('MCTS performance: total time: %s, predict time: %f, predict count: %d, average predict time: %f, predict cache hit percent: %f' % (time.time() - self.performance_start_time, self.performance_predict_time, self.performance_predict_count, self.performance_predict_time / self.performance_predict_count, self.predict_cache_hit / (self.performance_predict_count + self.predict_cache_hit)))

  def _simulate(self, color):
    node = self.root
    board_copy = self.board.copy()

    if color is None:
      color = board_copy.get_current_player_color()

    if show_search_debug_info:
      print('simulating...')
    while not node.is_leaf():
      action, node = node.select(self.root.N)
      # print('select', action, node)
      board_copy.move(action, color)
      if show_search_debug_info:
        print('simulate move', action//self.board.size, action%self.board.size)
      color = -color

    if show_search_debug_info:
      board_copy.display()
      print('current player is', board_copy.get_current_player_color())

    if board_copy.is_game_over():
      winner = board_copy.get_winner()
      value = 1 if winner == board_copy.get_current_player_color() else -1
      if show_search_debug_info:
        print('game over update', winner, -value)
      node.update_recursive(-value)
      return winner
    else:
      train_data = board_copy.get_simple_data()
      train_data = np.expand_dims(train_data, axis=0)  # 转换为四维张量，因为模型需要 batch 维度
      board_string = board_copy.get_board_string()
      predict = None
      if enable_cache and board_string in self.predict_cache:
        predict = self.predict_cache[board_string]
        self.predict_cache_hit += 1
      else:
        predict_start_time = time.time()
        predict = self.net.predict(train_data)
        self.performance_predict_time += time.time() - predict_start_time
        self.performance_predict_count += 1
        self.predict_cache[board_string] = predict
      action_probs, v = predict
      if show_search_debug_info:
        print('predict probs', np.array([int(i*1000) for i in action_probs]).reshape(self.board.size, self.board.size))
        print('predict value', v)
      # 顶层节点使用 dirichlet 噪声
      if self.self_play and node.parent == self.root:
        action_probs = 0.75*action_probs + 0.25 * np.random.dirichlet(0.03*np.ones(len(action_probs)))
      action_probs = action_probs * board_copy.get_valid_moves_mask()
      sum = np.sum(action_probs)
      if sum > 0:
        action_probs = action_probs / sum
      else:
        print('all valid moves have 0 probability, use workaround')
        action_probs = action_probs + board_copy.get_valid_moves_mask()
        action_probs = action_probs / np.sum(action_probs)
      v = v[0]
      # print('expand', action_probs[0], v[0][0])
      node.expand(action_probs, color*v) # Q是当前玩家的胜率，所以要乘以玩家角色
      if show_search_debug_info:
        print('update:', -v*color)
      # node.update_recursive(-v*color) # 这样更新会导致预测的胜率总是不准确，无法训练出有效的AI，应该还是返回0比较好
      node.update_recursive(0)
      return 0

  def move(self, color=None, verbose=False, temp=1):
    self.root = Node()  # reset the root node
    if color is None:
      color = self.board.get_current_player_color()

    for _ in range(self.simulation_num):
      self._simulate(color)

    # 选最优解
    if temp < 0.1:
      action = max(self.root.children.items(), key=lambda act_node: act_node[1].N)[0]
      return action

    action_probs = np.zeros(self.board.size * self.board.size)
    for action, node in self.root.children.items():
      action_probs[action] = node.N ** (1 / temp)
    action_probs /= np.sum(action_probs)
    return np.random.choice(np.arange(len(action_probs)), p=action_probs)

  def set_board(self, board):
    self.board = board

  def __str__(self):
    return "AI player, using pure Monte Carlo Tree Search algorithm"

