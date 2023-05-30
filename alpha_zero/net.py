# -*- coding: utf-8 -*-
'''
帮我用tensorflow写一个Net类，实现方法参考Alpha Zero的论文，这个类中会构造一个model模型，这个模型需要接收的输入维度是 n * n * 17，有两个输出层，其中一个输出落子的概率分布，是一个n*n的一位向量，每一个值表示当前位置的落子概率。另一个输出获胜的角色，实现以下方法：
- __init__: 初始化方法，需要传入棋盘的大小，默认为15, 在这个方法中构造网络模型
- predict: 预测方法，传入一个棋盘状态 n*n*17，返回两个值，第一个值是落子概率分布，第二个值是获胜的角色
- train: 用训练数据集进行训练
- save: 保存模型checkpoint
注意其中的n是棋盘的大小，输入维度是17, 17个平面，其中8个平面表示当前玩家的棋子分布，8个平面表示对手玩家的棋子分布，最后一个平面表示当前玩家的颜色，1表示黑棋，-1表示白棋
网络模型就用tensorflow内置的Resnet50
'''

import tensorflow as tf
from tensorflow.keras import Model
from tensorflow.keras.layers import Input, Conv2D, BatchNormalization, Activation, Add, Flatten, Dense
from tensorflow.keras.applications.resnet50 import ResNet50


class Net:
  def __init__(self, board_size=15):
    self.board_size = board_size
    self.model = self.build_model()

  def build_model(self):
    base_model = ResNet50(weights=None, include_top=False, input_shape=(self.board_size, self.board_size, 17))

    x = base_model.output
    x = Conv2D(filters=2, kernel_size=(1, 1))(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)

    # Policy Head
    policy_head = Conv2D(filters=2, kernel_size=(1, 1))(x)
    policy_head = BatchNormalization()(policy_head)
    policy_head = Activation('relu')(policy_head)
    policy_head = Flatten()(policy_head)
    policy_head = Dense(self.board_size * self.board_size, activation='softmax', name='policy')(policy_head)

    # Value Head
    value_head = Conv2D(filters=1, kernel_size=(1, 1))(x)
    value_head = BatchNormalization()(value_head)
    value_head = Activation('relu')(value_head)
    value_head = Flatten()(value_head)
    value_head = Dense(256, activation='relu')(value_head)
    value_head = Dense(1, activation='tanh', name='value')(value_head)

    model = Model(inputs=base_model.input, outputs=[policy_head, value_head])
    model.compile(loss={'policy': 'categorical_crossentropy', 'value': 'mean_squared_error'},
                  optimizer='adam', metrics=['accuracy'])

    return model

  def predict(self, board_state):
    board_state = board_state.reshape(-1, self.board_size, self.board_size, 17)
    policy, value = self.model.predict(board_state)
    return policy[0], value[0][0]

  def train(self, x_train, y_train, batch_size=256, epochs=10):
    self.model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs)

  def save(self, path):
    self.model.save_weights(path)
