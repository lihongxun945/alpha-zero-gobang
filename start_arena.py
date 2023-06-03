# -*- coding: utf-8 -*-
from alpha_zero.arena import Arena
from alpha_zero.human_player import HumanPlayer
from alpha_zero.board import Board
from alpha_zero.mcts import MCTS
from alpha_zero.net import Net

board_size=9
silumation_num=400

board = Board(size=board_size)

class MCTSPlayer:
  def __init__(self):
    net = Net(board_size)
    net.load('checkpoint/best_checkpoint.h5')
    self.mcts = MCTS(board=board, net=net, simulation_num=silumation_num, self_play=False)

  def move(self):
    return self.mcts.move(temp=0)

ai1 = MCTSPlayer()
ai2 = HumanPlayer(board)

arena = Arena(board, ai1, ai2)
arena.start()
