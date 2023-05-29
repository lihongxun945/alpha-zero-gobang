# -*- coding: utf-8 -*-
'''
帮我用python3写一个Arena类，作用是让两个AI对战，实现以下方法：
1. __init__: 初始化方法，需要传入1个board和2个AI实例，以及棋盘的大小，默认为15，参数在前面的AI先手
2. start: 开始对战，直到棋局结束，返回胜利的AI的颜色，每个AI落子之后，都调用一下board的display方法，打印当前棋盘
其中AI实例有一个方法move，返回AI的落子位置
'''

class Arena:
    def __init__(self, board, ai1, ai2, size=15):
        self.board = board
        self.ai1 = ai1
        self.ai2 = ai2

    def start(self):
        while self.board.get_winner() == 0:
            if self.board.get_current_player_color() == 1:
                move = self.ai1.move()
                self.board.move(move)
                print("AI 1 moved to position", move)
            else:
                move = self.ai2.move()
                self.board.move(move)
                print("AI 2 moved to position", move)
            self.board.display()
        winner_color = self.board.get_winner()
        if winner_color == 1:
            print("AI 1 wins!")
        else:
            print("AI 2 wins!")
        return winner_color