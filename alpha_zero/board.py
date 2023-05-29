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
                for dx, dy in directions:
                    try:
                        for k in range(1, 5):
                            if i+k*dx < 0 or j+k*dy < 0 or i+k*dx >= self.size or j+k*dy >= self.size:
                                break
                            if self.board[i][j] != self.board[i + k * dx][j + k * dy]:
                                break
                        else:
                            return self.board[i][j]
                    except IndexError:
                        continue
        return 0  # No winner yet

    def _count_same_color(self, x, y, dx, dy):
        count = 0
        color = self.board[x][y]
        while 0 <= x < self.size and 0 <= y < self.size and self.board[x][y] == color:
            count += 1
            x, y = x + dx, y + dy
        return count

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
                    print(" ○ ", end="")
                else:
                    print(" × ", end="")
            print()

    def get_valid_moves(self):
        return [i for i in range(self.size * self.size) if self.board[i // self.size][i % self.size] == 0]

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

    def get_data(self):
        x = np.zeros((self.size, self.size, 17), dtype=np.int8)

        # 填充棋盘状态
        history_len = len(self.history)
        for i in range(16):
            if i < history_len:
                # 获取历史状态
                state = np.zeros((self.size, self.size), dtype=np.int8)
                # 从history中获取每一次的落子，然后把它转换成棋盘状态
                for j in range(history_len - i):
                    position, color = self.history[j]
                    row, col = self.position_to_coordinate(position)
                    state[row, col] = color

                # 将每一次落子后的棋盘状态标记到x的前16个平面上
                x[:, :, 15 - i] = state

        # 最后一个平面表示当前轮到哪一方落子
        x[:, :, -1] = self.current_color  # 全部的值都是当前角色

        v = self.get_winner()  # 胜负情况

        # 创建一个全零向量表示落子概率
        pi = np.zeros(self.size * self.size)
        if len(self.history) > 0:
            # 最后一步落子位置的概率设为1，其他设为0
            last_move = self.history[-1][0]
            pi[last_move] = 1
        
        y = [v, pi]

        return x, y

