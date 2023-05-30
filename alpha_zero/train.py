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

checkpoint_file = os.path.join('checkpoint', 'best_checkpoit.h5')
data_file = os.path.join('checkpoint', 'train_data.pkl')

class Train:
  def __init__(self, board, ai, net, iterations=100, iteration_epochs=100, data_limit=2000, load_checkpoint=False):
    self.board = board
    self.ai = ai
    self.net = net
    self.iterations = iterations
    self.iteration_epochs = iteration_epochs
    self.data_limit = data_limit
    self.load_checkpoint = load_checkpoint

  def start(self):
    if self.load_checkpoint:
      self.net.load(checkpoint_file)
      with open(data_file, 'rb') as f:
        train_data = pickle.load(f)
    else:
      train_data = []

    for iteration in range(self.iterations):
      print(f"Starting iteration {iteration + 1}/{self.iterations}...")
      iteration_data = self._run_iteration()
      train_data.extend(iteration_data)

      # If the training data exceeds the limit, remove the oldest data.
      if len(train_data) > self.data_limit:
        del train_data[:len(train_data) - self.data_limit]

      print("Training...")
      X, y_v, y_p = zip(*train_data)
      self.net.train(np.array(X), np.array(y_v), np.array(y_p))

      print("Saving checkpoint...")
      self.net.save(checkpoint_file)
      with open(data_file, 'wb') as f:
        pickle.dump(train_data, f)

      print(f"Finished iteration {iteration + 1}/{self.iterations}.")

  def _run_iteration(self):
    iteration_data = []

    for epoch in range(self.iteration_epochs):
      print(f"Starting epoch {epoch + 1}/{self.iteration_epochs}...")
      board = self.board.copy()

      self.ai.set_board(board)

      epoch_data = []
      while not board.is_game_over():
        action = self.ai.move()
        x, y = board.get_data(action)
        epoch_data.append((x, y))
        board.move(action)
        print('move:', action)
        board.display()

      winner = board.get_winner()
      for data in epoch_data:
        iteration_data.append([data[0], winner, data[1][1]])
      print(f"Finished epoch {epoch + 1}/{self.iteration_epochs}.")

    return iteration_data
