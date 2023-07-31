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

c_puct = 2
show_search_debug_info = False
EPS = 1e-8

def rnd(num):
  if num is None:
    return None
  return round(num, 4)

class Node:
  def __init__(self, parent=None, P=0, Q=None, action=None):
    self.N = 0  # visit count
    self.Q = Q  # mean action value
    self.P = P  # prior probability
    self.action = action # 移动位置

    self.parent = parent
    self.children = dict()

  def is_leaf(self):
    return len(self.children) == 0

  def is_root(self):
    return self.parent is None

  def select(self):
    best_u = -float('inf')
    best_node = None
    best_action = None
    for action, node in self.children.items():
      u = None
      if node.Q is None:
        u = c_puct * node.P * np.sqrt(self.N + EPS)
      else:
        u = node.Q + c_puct * node.P * (np.sqrt(self.N) / (1 + node.N))
      if u > best_u:
        best_u = u
        best_node = node
        best_action = action
    return best_action, best_node

  def expand(self, action_priors, v=0):
    for action in range(0, len(action_priors)):
      prob = action_priors[action]
      if action not in self.children:
        if prob > 0:
          self.children[action] = Node(parent=self, P=prob, Q=None, action=action)

  def update(self, value):
    if show_search_debug_info:
      if self.action:
        print('update node:', (self.action//5, self.action%5), value)
      else:
        print('update root node:', value)
    if self.Q is None:
      self.Q = value
      self.N = 1
    else:
      self.Q = (self.N * self.Q + value) / (self.N + 1)
      self.N += 1

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
      action, node = node.select()
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
        print('game over update: winner ', winner, 'value ', -value)
      node.update_recursive(-value*2)
      return winner
    else:
      train_data = board_copy.get_data()
      train_data = np.expand_dims(train_data, axis=0)  # 转换为四维张量，因为模型需要 batch 维度
      board_string = board_copy.get_board_string()
      valid_moves_mask = board_copy.get_valid_moves_mask()
      action_probs = None
      v = None
      if self.self_play and board_string in self.predict_cache:
        action_probs, v = self.predict_cache[board_string]
        self.predict_cache_hit += 1
      else:
        predict_start_time = time.time()
        action_probs, v = self.net.predict(train_data)
        self.performance_predict_time += time.time() - predict_start_time
        self.performance_predict_count += 1
        if self.self_play:
          self.predict_cache[board_string] = (action_probs, v)

      action_probs = action_probs * valid_moves_mask

      # 先normalize，再加噪声
      sum = np.sum(action_probs)
      if sum > 0:
        action_probs = action_probs / sum
      else:
        print('all valid moves have 0 probability, use workaround')
        action_probs = action_probs + board_copy.get_valid_moves_mask()
        action_probs = action_probs / np.sum(action_probs)

      # 噪声在train中添加，不在这里
      # 顶层节点使用 dirichlet 噪声
      # if self.self_play and node == self.root:
      #   # 创建一个与action_probs长度相同的，但只在有效动作位置上具有非零值的向量，用于狄利克雷噪声
      #   dirichlet_noise_mask = np.where(valid_moves_mask > 0, 1, 1e-8)
      #   dirichlet_noise = np.random.dirichlet(0.03 * dirichlet_noise_mask)
      #   action_probs = 0.75*action_probs + 0.25 * dirichlet_noise

      if show_search_debug_info:
        print('predict probs', np.array([int(i*1000) for i in action_probs]).reshape(self.board.size, self.board.size))
        print('predict Q', np.array([(i[0], round(i[1].Q, 2)) for i in self.root.children.items()]))
        print('predict value', v)
      
      v = v[0]
      node.expand(action_probs, color*v) # Q是当前玩家的胜率，所以要乘以玩家角色
      if show_search_debug_info:
        print('mcts expand:', action_probs.reshape(self.board.size, self.board.size), v)
      node.update_recursive(-color*v)
      return 0

  # 返回概率分布
  def getActionProbs(self, color=None, temp=1):
    self.root = Node()  # reset the root node
    if color is None:
      color = self.board.get_current_player_color()

    for _ in range(self.simulation_num):
      self._simulate(color)

    action_probs = np.zeros(self.board.size * self.board.size)
    if show_search_debug_info:
      ns = [(i[0], i[1].N) for i in self.root.children.items()]
      size = self.board.size
      ps = np.zeros(size*size)
      for i in ns:
        ps[i[0]] = i[1]
      print(ps.reshape(size, size))
    if temp == 0:
      max_value = max(node.N for node in self.root.children.values())
      actions_with_max_value = [action for action, node in self.root.children.items() if node.N == max_value]
      action = np.random.choice(actions_with_max_value)
      action_probs[action] = 1
      return action_probs
    for action, node in self.root.children.items():
      action_probs[action] = node.N ** (1 / temp)
    action_probs /= np.sum(action_probs)
    return action_probs

  # 直接选取最优解返回，根据温度决定是否使用概率分布
  def move(self, color=None, temp=1):
    action_probs = self.getActionProbs(color, temp)

    if temp == 0:
      max_indices = np.argwhere(action_probs == np.amax(action_probs)).flatten()
      action = np.random.choice(max_indices)
      return action
    else:
      return np.random.choice(len(action_probs), p=action_probs)

  def set_board(self, board):
    self.board = board

  def __str__(self):
    return "AI player, using pure Monte Carlo Tree Search algorithm"

