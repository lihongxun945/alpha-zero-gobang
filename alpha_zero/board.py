# -*- coding: utf-8 -*-
import copy
import numpy as np

'''
帮我用python3写一个五子棋的Board类，实现以下功能：
1. __init__: 初始化方法用来初始化棋盘，可以指定棋盘大小，默认为15，可以指定先手颜色，默认为黑子先手
2. move: 落子，指定位置，落子颜色。如果不指定落子颜色，则默认为当前轮到的颜色
3. undo: 悔棋，可以指悔棋七步数，如果不指定，默认为1
4. get_winner: 判断当前棋局胜负，返回 1 表示黑子胜，-1 表示白子胜，0 表示还未分出胜负
5. display: 打印当前棋盘
6. get_valid_moves: 获取当前棋局下一步可以走的所有位置
7. get_current_player_color: 获取当前轮到哪一方落子，返回 1 表示黑子，-1 表示白子
8. get_board_string: 获取当前棋盘的字符串表示，把棋盘上所有棋子拼成一个字符串来表示

注意，所有位置都用一个整数表示，从0开始，从左到右，从上到下依次编号, 所有棋子都是用一个整数表示，1表示黑子，-1表示白子，0表示空位
'''

'''
为了用Net模型，需要改造一下Board类，增加一个get_data方法，这个方法会返回一个训练数据 [x, y]
其中 x 是 n*n*17 的张量，其中8个平面表示当前棋盘上黑子最近8次落子后的状态，8个平面表示当前棋盘上白子的最近8次落子后的状态，最后一个平面表示当前轮到哪一方落子，如果是黑方落子，则这个平面全部为1，否则为-1
其中 y 是一个二维向量 [v, pi]，v 表示当前棋盘的胜负情况，1表示黑方胜，-1表示白方胜，0表示未分出胜负，pi 是一个n*n的向量，表示黑方落子的概率，其中非法位置的概率为0
'''


# 以下是Chatgpt4.0 写的代码, 并做了少量修改

class Board:
  def __init__(self, size=15, first_player=1):
    self.size = size
    self.board = [[0 for _ in range(size)] for _ in range(size)]
    self.history = []
    self.current_player = first_player

  def move(self, position, color=None):
    if color is None:
      color = self.current_player
    x, y = position // self.size, position % self.size
    self.board[x][y] = color
    self.history.append((position, color))
    self.current_player *= -1

  def undo(self, steps=1):
    for _ in range(steps):
      if self.history:
        position, color = self.history.pop()
        x, y = position // self.size, position % self.size
        self.board[x][y] = 0
        self.current_player = color

  def get_winner(self):
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for i in range(self.size):
      for j in range(self.size):
        if self.board[i][j] == 0:
          continue
        else:
          if self.is_current_position_winning(i * self.size + j, directions=directions):
            return self.board[i][j]
    return 0  # No winner yet

  def is_current_position_winning(self, position, directions=[(1, 0), (0, 1), (1, 1), (1, -1), (0, -1), (-1, 0), (-1, 1), (-1, -1)]):
    i, j = position // self.size, position % self.size
    for dx, dy in directions:
      for k in range(1, 5):
        if i + k * dx < 0 or j + k * dy < 0 or i + k * dx >= self.size or j + k * dy >= self.size:
          break
        if self.board[i][j] != self.board[i + k * dx][j + k * dy]:
          break
      else:
        return True
    return False

  def display(self):
    print("  ", end="")
    for y in range(self.size):
      print("{:2d}".format(y), end=" ")
    print()
    for i in range(self.size):
      print("{:2d}".format(i), end=" ")
      for j in range(self.size):
        piece = self.board[i][j]
        if piece == 0:
          print(" . ", end="")
        elif piece == 1:
          print(" O ", end="")
        else:
          print(" X ", end="")
      print()

  # 返回所有合法的位置，不合法的不返回，这里是没有考虑五子棋的知识的
  def get_valid_moves_all(self):
    return [i for i in range(self.size * self.size) if self.board[i // self.size][i % self.size] == 0]

  # 返回所有合法的位置，增加了五子棋的一些知识
  # 1. 如果存在能连成五个子的位置，那么只返回这些位置
  # 2. 返回周围2步之内至少有一个子的位置，以及中间的空位
  def get_valid_moves(self):
    winning_moves = set()

    # 先检查是否存在能连成五子的棋子
    for row in range(self.size):
      for col in range(self.size):
        if self.board[row][col] == 0:
          # 尝试下一个黑子，看看能不能连成五子
          for player in [-1, 1]:
            self.board[row][col] = player # 不要调用self.move ，因为这里颜色不对，可能会导致混乱
            if self.is_current_position_winning(row*self.size+col):
              winning_moves.add(row*self.size + col)
            self.board[row][col] = 0
    if winning_moves:
      return list(winning_moves)

    valid_moves = set()
    # 只检测周围2步范围内有至少一个棋子的位置
    for row in range(self.size):
      for col in range(self.size):
        if self.board[row][col] == 0:
          has_adjacent_piece = False
          for dr in [-2, -1, 0, 1, 2]:
            if has_adjacent_piece:
              break
            for dc in [-2, -1, 0, 1, 2]:
              if (0 <= row+dr < self.size) and (0 <= col+dc < self.size) and (self.board[row+dr][col+dc] != 0):
                has_adjacent_piece = True
                break
          if not has_adjacent_piece:
            continue
          else:
            valid_moves.add(row*self.size + col)
    # 如果中间没人走，也要包括中间，避免总是被对手引导到棋盘边缘
    _range = [-1, 0, 1] if self.size > 3 else [0]
    for x in _range:
      for y in _range:
          i = int(self.size / 2) + x
          j = int(self.size / 2) + y
          if self.board[i][j] == 0:
            valid_moves.add(i*self.size + j)
    return list(valid_moves)

  def get_valid_moves_mask(self):
    mask = np.zeros(self.size * self.size, dtype=np.int8)
    valid_moves = self.get_valid_moves()
    for move in valid_moves:
      mask[move] = 1
    return mask

  def get_current_player_color(self):
    return self.current_player

  def get_board_string(self):
    return ''.join(str(self.board[i // self.size][i % self.size]) for i in range(self.size * self.size))

  def get_size(self):
    return self.size

  def copy(self):
    new_board = Board(self.size, self.current_player)
    new_board.board = copy.deepcopy(self.board)
    new_board.history = copy.deepcopy(self.history)
    return new_board

  def position_to_coordinate(self, position):
    """
    将整数位置转换为二维坐标
    """
    row = position // self.size
    col = position % self.size
    return row, col

  def coordinate_to_position(self, coordinate):
    """
    将整数位置转换为二维坐标
    """
    return coordinate[0] * self.size + coordinate[1]

  # def get_data(self, next_action = None):
  #   x = np.zeros((17, self.size, self.size), dtype=np.int8)
  #   # 填充棋盘状态
  #   history_len = len(self.history)
  #   for i in range(16):
  #     if i < history_len:
  #       # 获取历史状态
  #       state = np.zeros((self.size, self.size), dtype=np.int8)
  #       # 从history中获取每一次的落子，然后把它转换成棋盘状态
  #       for j in range(history_len - i):
  #         position, color = self.history[j]
  #         row, col = self.position_to_coordinate(position)
  #         state[row, col] = color

  #       # 将每一次落子后的棋盘状态标记到x的前16个平面上
  #       x[15 - i, :, :] = state

  #   # 最后一个平面表示当前轮到哪一方落子
  #   x[-1, :, :] = self.current_player  # 全部的值都是当前角色

  #   if next_action is None:
  #     return x

  #   v = self.get_winner()  # 胜负情况

  #   # 创建一个全零向量表示落子概率
  #   pi = np.zeros(self.size * self.size)
  #   pi[next_action] = 1

  #   y = [v, pi]

  #   return x, y

  '''
  AlphaZero 的神经网络输入表示由 17 个二值特征平面组成。这些特征平面表示了棋盘上的情况以及当前的游戏状态，包括当前玩家的棋子位置、对手的棋子位置以及其他游戏相关信息。具体来说，这 17 层可以被细分为：
  前 8 层表示的是当前玩家在最近 8 步的棋子分布。每个平面中，如果在该步该玩家在某一格中有棋子，则该格的值为 1，否则为 0。
  接下来的 8 层表示的是对手在最近 8 步的棋子分布。处理方式与前 8 层类似。
  最后一层是一个标量特征平面，表示当前玩家的颜色（1表示黑棋，-1表示白棋）。
  这 17 层的平面堆叠在一起，为神经网络提供了关于当前游戏状态的全面信息。神经网络通过这些输入来预测每一步的最佳动作和最终游戏结果。
  '''
  def get_data(self, next_action=None):
    x = np.zeros((17, self.size, self.size), dtype=np.int8)
    # 填充棋盘状态
    history_len = len(self.history)
    black_moves = [position for position, color in self.history if color == 1]
    white_moves = [position for position, color in self.history if color == -1]
    black_len = len(black_moves)
    white_len = len(white_moves)

    # The recent 8 steps of black pieces
    for i in range(8):
      if i < black_len:
        state = np.zeros((self.size, self.size), dtype=np.int8)
        for j in range(black_len - i):
          position = black_moves[j]
          row, col = self.position_to_coordinate(position)
          state[row, col] = 1
        x[7 - i, :, :] = state

    # The recent 8 steps of white pieces
    for i in range(8):
      if i < white_len:
        state = np.zeros((self.size, self.size), dtype=np.int8)
        for j in range(white_len - i):
          position = white_moves[j]
          row, col = self.position_to_coordinate(position)
          state[row, col] = -1
        x[15 - i, :, :] = state

    # 最后一个平面表示当前轮到哪一方落子
    x[-1, :, :] = self.current_player  # 全部的值都是当前角色

    if next_action is None:
      return x

    v = self.get_winner()  # 胜负情况

    # 创建一个全零向量表示落子概率
    pi = np.zeros(self.size * self.size)
    pi[next_action] = 1

    y = [v, pi]

    return x, y

  def is_game_over(self):
    return self.get_winner() !=0 or len(self.get_valid_moves()) == 0

  # 数据增强，进行水平和垂直翻转
  def enhance_data(self, x, y):
    # 原始数据
    data_original = (x, y)
    # 水平翻转数据
    x_flip_horizontal = np.flip(x, 2)
    y_flip_horizontal = [y[0], np.flip(y[1].reshape(self.size, self.size), 1).flatten()]
    data_flip_horizontal = (x_flip_horizontal, y_flip_horizontal)
    # 垂直翻转数据
    x_flip_vertical = np.flip(x, 1)
    y_flip_vertical = [y[0], np.flip(y[1].reshape(self.size, self.size), 0).flatten()]
    data_flip_vertical = (x_flip_vertical, y_flip_vertical)

    return data_original, data_flip_horizontal, data_flip_vertical
