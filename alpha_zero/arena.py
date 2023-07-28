# -*- coding: utf-8 -*-
'''
帮我用python3写一个Arena类，作用是让两个AI对战，实现以下方法：
1. __init__: 初始化方法，需要传入1个board和2个AI实例，以及棋盘的大小，默认为15，参数在前面的AI先手
2. start: 开始对战，直到棋局结束，返回胜利的AI的颜色，每个AI落子之后，都调用一下board的display方法，打印当前棋盘
其中AI实例有一个方法move，返回AI的落子位置
'''

'''
帮我把这个方法改一下，可以指定ai1和ai2的对局次数，轮流执先手。并且可以指定每次是否从五子棋常见的26个开局中随机选取开局。
board 有一个 move(position) 方法可以用来走棋，有size可以获取棋盘大小，可以用这两个方法来实现开局
'''
import random

class Arena:
  def __init__(self, board, ai1, ai2, random_opening=True):
    self.board = board
    self.ai1 = ai1
    self.ai2 = ai2
    self.random_opening = random_opening

  def get_random_opening(self):
    center = self.board.size // 2
    openings = [(center, center)]
    seconds = [[0, 1], [1, 0], [0, -1], [-1, 0], [1, 1], [-1, -1], [1, -1], [-1, 1]]
    second = seconds.pop(random.randint(0, len(seconds)-1))
    openings.append((second[0]+center, second[1]+center))
    thirds = [
      [-2, -2], [-2, -1], [-2, 0], [-2, 1], [-2, 2],
      [-1, -2], [-1, 2],
      [0, -2], [0, 2],
      [1, -2], [1, 2],
      [2, -2], [2, -1], [2, 0], [2, 1], [2, 2],
    ]
    thirds.extend(seconds)
    third = thirds.pop(random.randint(0, len(thirds)-1))
    openings.append((third[0]+center, third[1]+center))
    # openings.append((third_d[0]+center, third_d[1]+center))
    return openings
  
  def print(self, *args):
    if self.verbose:
      print(*args)

  def start(self, match_count=20, verbose=True):
    self.verbose = verbose
    ai1 = self.ai1
    ai2 = self.ai2
    ai1_wins = 0
    ai2_wins = 0
    draws = 0
    opening = self.get_random_opening()
    for _ in range(match_count):
      board = self.board
      if self.random_opening:
        if _%2==0:
            opening = self.get_random_opening()
            print('random opening', opening)
        for move in opening:
          board.move(board.coordinate_to_position(move))

      if verbose:
        board.display()
      while not board.is_game_over():
        if board.get_current_player_color() == 1:
          move = ai1.move()
          board.move(move)
          self.print("AI 1 moved to position", board.position_to_coordinate(move))
        else:
          move = ai2.move()
          board.move(move)
          self.print("AI 2 moved to position", board.position_to_coordinate(move))
        if verbose:
          board.display()

      board.display()
      winner_color = board.get_winner()
      print('winner is: ', winner_color)
      print('history:', [[[h[0]//board.size, h[0]%board.size], h[1]] for h in board.history])
      if winner_color == 1:
        if self.ai1 == ai1:
          ai1_wins += 1
          print("AI 1 wins!")
        else:
          ai2_wins += 1
          print("AI 2 wins!")
      elif winner_color == -1:
        if self.ai2 == ai2:
          ai2_wins += 1
          print("AI 2 wins!")
        else:
          ai1_wins += 1
          print("AI 1 wins!")
      else:
          draws += 1
      ai1, ai2 = ai2, ai1
      self.board.reset()
    return ai1_wins, ai2_wins, draws

