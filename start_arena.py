# -*- coding: utf-8 -*-
from alpha_zero.arena import Arena
from alpha_zero.players import HumanPlayer, MCTSPlayer
from alpha_zero.board import Board

board_size=11
silumation_num=400

board = Board(size=board_size)

ai1 = MCTSPlayer(board=board, simulation_num=silumation_num)
ai2 = HumanPlayer(board)

arena = Arena(board, ai1, ai2)
arena.start()
