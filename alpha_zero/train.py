# -*- coding: utf-8 -*-
'''
帮我用写一个Train类，用来执行AI训练，基本原理是调用 ai 进行多次对局，并把对局结果保存到文件中，然后用这些数据训练Net，实现如下方法：
- __init__： 初始化方法，传入这几个参数，board 是Board实例，ai 是要执行对局的AI，net 是神经网络, iterations 是要执行多少轮训练，iteration_epochs 是每一轮训练中执行多少次对局，load_checkpoint 是否要加载之前的checkpoint
- start: 启动训练，执行 self.iterations 轮训练，每一轮执行 self.iteration_epochs 次对局，每一轮结束后，保存训练数据，用数据训练神经网络，然后保存checkpoint
其中的ai和PureMCTS接口是一样的，有一个 train 方法进行训练
'''

import pickle
import numpy as np
import os
from tqdm import tqdm
from random import shuffle
from alpha_zero.players import MCTSPlayer
from alpha_zero.arena import Arena
from copy import deepcopy
from datetime import datetime

accept_threshold = 0.6
pitting_count = 20
learning_rate_threshold = 20

class Train:
  def __init__(self, board, ai, net, prev_net, iterations=100, iteration_epochs=100, train_data_limit=200000, load_checkpoint=False, temp_threshold=20):
    self.board = board
    self.ai = ai
    self.net = net
    self.prev_net = prev_net
    self.iteration = 0
    self.iterations = iterations
    self.iteration_epochs = iteration_epochs
    self.data_limit = train_data_limit
    self.load_checkpoint = load_checkpoint
    self.temp_threshold = temp_threshold
    self.train_data_history = []
    self.pitting_history = []
    self.init_file_path()
  
  def init_file_path(self):
    self.checkpoint_dir = f'checkpoint_{self.board.size}'
    self.checkpoint_file = os.path.join(self.checkpoint_dir, 'best_checkpoint.h5')
    self.tmp_checkpoint_file = os.path.join(self.checkpoint_dir, 'tmp_checkpoint.h5')
    self.data_file = os.path.join(self.checkpoint_dir, 'train_data.pkl')
    self.meta_file = os.path.join(self.checkpoint_dir, 'meta.pkl')

  def start(self):
    if self.load_checkpoint:
      self.load_all_data()
    for i in range(self.iterations):
      self.iteration += 1
      # 动态学习速率
      lr = 0.001 if self.iteration <= learning_rate_threshold else 0.0002
      self.net.set_lr(lr)
      print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Starting iteration {self.iteration}/{self.iterations}...")
      print('current lr:', self.net.get_lr())
      iteration_data = self._run_iteration()

      # make new train data
      train_data = deepcopy(self.train_data_history)

      train_data.extend(iteration_data)
      print('train_data length:', len(train_data))

      # If the training data exceeds the limit, remove the oldest data.
      if len(train_data) > self.data_limit:
        del train_data[:len(train_data) - self.data_limit]
        print('train_data length after remove out of limit:', len(train_data))

      print("Training...")

      # shuffle the data before training
      shuffled_train_data = deepcopy(train_data)
      shuffle(shuffled_train_data)

      X, y_v, y_p = zip(*shuffled_train_data)

      self.net.save(self.tmp_checkpoint_file)
      self.prev_net.load(self.tmp_checkpoint_file)

      # do the training
      self.net.train(np.array(X), np.array(y_v), np.array(y_p))

      print("Pitting against previous version...")
      prev_ai = MCTSPlayer(board=self.board, net=self.prev_net, simulation_num=self.ai.simulation_num)
      current_ai = MCTSPlayer(board=self.board, net=self.net, simulation_num=self.ai.simulation_num)

      area = Arena(board=self.board, ai1=current_ai, ai2=prev_ai, random_opening=True)
      wins, fails, draws = area.start(match_count=pitting_count, verbose=False)

      win_percent = round(wins/(wins+fails), 2)
      print(f"Pit result, new ai Wins: {wins}, Fails: {fails}, Draws: {draws}")
      self.pitting_history.append(win_percent)
      print("pitting history:", self.pitting_history)

      if win_percent >= accept_threshold:
        print("Accept!!! Saving checkpoint...")
        self.net.save(self.checkpoint_file)

      else:
        print("Discarding checkpoint...")
        self.net.load(self.tmp_checkpoint_file)
      # 即使没有赢，应该也是存下来比较好
      self.train_data_history = train_data
      with open(self.data_file, 'wb+') as f:
        pickle.dump(self.train_data_history, f)

      # 保存元数据
      self.save_meta()

  def _run_iteration(self):
    self.ai.reset()
    iteration_data = []

    black_wins = 0
    white_wins = 0
    draws = 0
    for epoch in tqdm(range(self.iteration_epochs), desc="Self Play"):
      board = self.board.copy()
      size = board.size

      epoch_steps = 0

      self.ai.set_board(board)

      epoch_data = []
      while not board.is_game_over():
        temp = int(epoch_steps <= self.temp_threshold)
        probs = self.ai.getActionProbs(temp=temp)
        # print(np.array(probs).reshape(size, size))
        if temp == 0:
          max_indices = np.argwhere(probs == np.amax(probs)).flatten()
          action = np.random.choice(max_indices)
        else:
          action = np.random.choice(len(probs), p=probs)
        x = board.get_simple_data()
        y = [0, probs]
        epoch_data.extend(board.enhance_data(x, y))
        # print('move:', action // size, action % size)
        board.move(action)
        epoch_steps += 1

      winner = board.get_winner()
      if winner == 1:
          black_wins += 1
      elif winner == -1:
          white_wins += 1
      else:
          draws += 1
      print('#epoch', epoch, ', step ', epoch_steps, 'winner', winner)
      board.display()
      print('history:', [[[h[0]//board.size, h[0]%board.size], h[1]] for h in board.history])
      for data in epoch_data:
        iteration_data.append([data[0], winner, data[1][1]])
    print('summary: black wins', black_wins, 'white wins', white_wins, 'draws', draws)
    self.ai.displayPerformance()

    return iteration_data

  def load_all_data(self):
    if not self.load_checkpoint:
      return None
    # 创建文件夹
    if not os.path.exists(self.checkpoint_dir):
      print("create checkpoint directory: {}".format(self.checkpoint_dir))
      os.mkdir(self.checkpoint_dir)
    print('loading checkpoint from', self.checkpoint_file)
    self.net.load(self.checkpoint_file)
    print('checkpoint loaded success')
    with open(self.data_file, 'rb') as f:
      print('loading train_data from', self.data_file)
      self.train_data_history = pickle.load(f)
    print('train_data loaded success, total length :', len(self.train_data_history))
    print('loading meta from ', self.meta_file)
    with open(self.meta_file, 'rb') as f:
      history_data = pickle.load(f)
      self.iteration = history_data["iteration"]
      self.pitting_history = history_data["pitting_history"]
      print('meta loaded success, iteration:', self.iteration, 'pitting_history:', self.pitting_history)

  def save_meta(self):
    with open(self.meta_file, 'wb+') as f:
      history_data = {
        "iteration": self.iteration,
        "pitting_history": self.pitting_history
      }
      pickle.dump(history_data, f)
