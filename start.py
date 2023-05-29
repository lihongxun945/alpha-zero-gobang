# -*- coding: utf-8 -*-
from alpha_zero.arena import Arena
from alpha_zero.human_player import HumanPlayer
from alpha_zero.board import Board
from alpha_zero.pure_mcts_player import PureMCTSPlayer

board = Board(size=6, first_player=1)

ai1 = PureMCTSPlayer(board, simulation_num=5000)
ai2 = HumanPlayer(board)

arena = Arena(board, ai1, ai2)
arena.start()