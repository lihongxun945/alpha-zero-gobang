# -*- coding: utf-8 -*-
import tensorflow as tf
from alpha_zero.net import Net
from alpha_zero.board import Board
from alpha_zero.mcts import MCTS
from alpha_zero.train import Train

# 训练参数
board_size = 9 # 棋盘大小
win_count = 5 # 多少个棋子连在一起可以赢，可以改成4快速验证算法是否正确
iterations = 1000 #  训练多少轮
iteration_epochs = 200 # 每一轮进行多少次对局
simulation_num = 400 # 蒙特卡洛模拟次数
load_checkpoint = True # 是否加载checkpoint和训练数据
train_data_limit = 1000000 # 训练数据最大长度
temp_threshold = 10 # 选择落子的温度阈值，小于这个数值会更随机，大于这个数值会总是选最优解。Alpha Zero设置的是30

gpu = True # 启用GPU加速

if not gpu:
  print('disable GPU')
  tf.config.set_visible_devices([], 'GPU')
else:
  print('GPUs:', tf.config.list_physical_devices('GPU'))

board = Board(size=board_size, win_count=win_count)
net = Net(board_size)
prev_net = Net(board_size)
net.model.summary()
ai = MCTS(board, net, simulation_num=simulation_num, self_play=True)

train = Train(board, ai=ai, net=net, prev_net=prev_net, iterations=iterations, iteration_epochs=iteration_epochs, load_checkpoint=load_checkpoint, train_data_limit=train_data_limit, temp_threshold=temp_threshold)
train.start()
