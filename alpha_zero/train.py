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
from random import shuffle, random
from alpha_zero.players import MCTSPlayer
from alpha_zero.arena import Arena
from alpha_zero.elo import calculate_elo
from alpha_zero.opening import get_random_opening
from copy import deepcopy
from datetime import datetime
from alpha_zero.utils import construct_weights
import math

accept_threshold = 0.6
pitting_count = 20
backup_checkpoint_interval = 10
random_opening_percent = 0.5 # 开局随机走法的概率，通过随即开局避免总是走同样的开局，避免先手必胜的情况
weight_gamma = 0.9 # 权重衰减因子

class Train:
  def __init__(self, board, ai, net, prev_net, iterations=100, iteration_epochs=100, train_data_limit=200000, load_checkpoint=False, temp_ratio=0.9):
    self.board = board
    self.ai = ai
    self.net = net
    self.prev_net = prev_net
    self.iteration = 0
    self.iterations = iterations
    self.iteration_epochs = iteration_epochs
    self.data_limit = train_data_limit
    self.load_checkpoint = load_checkpoint
    self.temp_ratio = temp_ratio
    self.train_data_history = []
    self.pitting_history = []
    self.elo_history = []
    self.best_elo = 400 # best checkpoint elo
    self.init_file_path()

  def init_file_path(self):
    self.checkpoint_dir = f'checkpoint_{self.board.size}'
    self.checkpoint_file = os.path.join(self.checkpoint_dir, 'best_checkpoint.h5')
    self.tmp_checkpoint_file = os.path.join(self.checkpoint_dir, 'tmp_checkpoint.h5')
    self.data_file = os.path.join(self.checkpoint_dir, 'train_data.pkl')
    self.meta_file = os.path.join(self.checkpoint_dir, 'meta.pkl')

  # 每x轮训练，保存一次checkpoint
  def get_backup_checkpoint_file(self, iteration):
    return os.path.join(self.checkpoint_dir, f'backup_checkpoint_{iteration}.h5')


  def start(self):
    if self.load_checkpoint:
      self.load_all_data()
    for i in range(self.iterations):
      self.iteration += 1
      # 动态学习速率
      # self.net.set_lr(lr)
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

      X, y_v, y_p, weights = zip(*shuffled_train_data)

      self.net.save(self.tmp_checkpoint_file)
      if os.path.exists(self.checkpoint_file):
        print('pre_net load file:', self.checkpoint_file)
        self.prev_net.load(self.checkpoint_file)

      # do the training
      self.net.train(np.array(X), np.array(y_v), np.array(y_p), np.array(weights))

      print("Pitting against previous version...")
      prev_ai = MCTSPlayer(board=self.board, net=self.prev_net, simulation_num=self.ai.simulation_num)
      current_ai = MCTSPlayer(board=self.board, net=self.net, simulation_num=self.ai.simulation_num)

      area = Arena(board=self.board, ai1=current_ai, ai2=prev_ai, random_opening=True)
      wins, fails, draws, results = area.start(match_count=pitting_count, verbose=False)

      win_percent = round(wins/(wins+fails), 2)
      print(f"Pit result, new ai Wins: {wins}, Fails: {fails}, Draws: {draws}, results: {results}")
      self.pitting_history.append(win_percent)
      print("pitting history:", self.pitting_history)

      # calculate elo
      current_elo = 400
      if len(self.elo_history) > 0:
        current_elo = self.elo_history[-1]
      new_elo = calculate_elo(current_elo, self.best_elo, results)
      self.elo_history.append(new_elo)
      print('elo history', self.elo_history)

      if win_percent >= accept_threshold:
        print("Accept!!! Saving checkpoint...")
        self.net.save(self.checkpoint_file)
        self.best_elo = new_elo
        print('update best elo', self.best_elo)

      else:
        print("Discarding checkpoint...")
        # self.net.load(self.tmp_checkpoint_file)
      # 即使没有赢，应该也是存下来比较好
      self.train_data_history = train_data
      with open(self.data_file, 'wb+') as f:
        pickle.dump(self.train_data_history, f)

      # 保存元数据
      self.save_meta()

      if self.iteration % backup_checkpoint_interval == 0:
        self.net.save(self.get_backup_checkpoint_file(self.iteration))

  def _run_iteration(self):
    self.ai.reset()
    iteration_data = []

    black_wins = 0
    white_wins = 0
    draws = 0

    epoch_steps = 0

    for epoch in tqdm(range(self.iteration_epochs), desc="Self Play"):
      epoch_steps = 0
      board = self.board.copy()
      size = board.size

      random_opening = random() < random_opening_percent
      if random_opening:
        openings = get_random_opening(size)
        print('random opening:', openings)
        for move in openings:
          board.move(board.coordinate_to_position(move))
          epoch_steps += 1


      self.ai.set_board(board)

      epoch_data = []
      while not board.is_game_over():
        temp = pow(self.temp_ratio, epoch_steps)
        if temp <= 0.1:
          temp = 0
        probs = self.ai.getActionProbs(temp=1)
        # print(np.array(probs).reshape(size, size))
        # 添加狄利克雷噪声，用于选择节点
        # 创建一个与action_probs长度相同的，但只在有效动作位置上具有非零值的向量，用于狄利克雷噪声
        valid_moves_mask = board.get_valid_moves_mask()
        dirichlet_noise_mask = np.where(valid_moves_mask > 0, 1, 1e-8)
        dirichlet_noise = np.random.dirichlet(0.03 * dirichlet_noise_mask)
        if temp == 0:
          max_indices = np.argwhere(probs == np.amax(probs)).flatten()
          action = np.random.choice(max_indices)
        else:
          # 加噪声
          noised_probs = 0.75*probs+ 0.25 * dirichlet_noise
          action = np.random.choice(len(noised_probs), p=noised_probs)
        # 开局8步以内，只有20%的概率会记录数据，避免开局数据过多影响学习
        # if epoch_steps >= 8 or random() <= 0.2:
        x = board.get_data()
        y = [epoch_steps, probs]
        epoch_data.extend(board.enhance_data(x, y))
        # epoch_data.append((x, y))
        # print('move:', action // size, action % size)
        board.move(action)
        epoch_steps += 1

      if epoch_steps <= 10 and random() > 0.2: # 10步以内获胜的棋，只保留20%，因为这种棋意义不大
        continue
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
      weights = construct_weights(epoch_steps, weight_gamma)
      for i in range(len(epoch_data)):
        data = epoch_data[i]
        x, y = data
        step = y[0]
        weight = weights[step]
        iteration_data.append([x, winner, y[1], weight])
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
      self.elo_history = history_data["elo_history"]
      self.best_elo = history_data["best_elo"]
      print('meta loaded success, iteration:', self.iteration)
      print('pitting_history:', self.pitting_history)
      print('best_elo:', self.best_elo)
      print('elo_history:', self.elo_history)

  def save_meta(self):
    with open(self.meta_file, 'wb+') as f:
      history_data = {
        "iteration": self.iteration,
        "pitting_history": self.pitting_history,
        "elo_history": self.elo_history,
        "best_elo": self.best_elo,
      }
      pickle.dump(history_data, f)
