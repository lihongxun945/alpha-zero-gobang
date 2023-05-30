# -*- coding: utf-8 -*-
from alpha_zero.net import Net
from alpha_zero.board import Board
from alpha_zero.pure_mcts import PureMCTS
from alpha_zero.train import Train

# 训练参数
board_size = 6 # 棋盘大小
iterations = 100 #  训练多少轮
iteration_epochs = 2 # 每一轮进行多少次对局
simulation_num = 100 # 蒙特卡洛模拟次数
load_checkpoint = False # 是否加载checkpoint和训练数据

board = Board(size=board_size)

ai = PureMCTS(board, simulation_num=100)

net = Net(board_size)

train = Train(board, ai=ai, net=net, iterations=iterations, iteration_epochs=iteration_epochs, load_checkpoint=load_checkpoint)
train.start()
