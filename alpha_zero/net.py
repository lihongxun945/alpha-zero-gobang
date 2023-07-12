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
import time
from tensorflow.keras.layers import Input, Dense, Conv2D, Flatten, Reshape, BatchNormalization, Add, Activation, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.optimizers import Adam
import numpy as np

lr = 0.001

class Net:
  def __init__(self, size=15):
    self.size = size
    self.build_simple_model()
    self.epochs = 20

  def build_simple_model(self):
    # game params
    num_channels = 512
    action_size = self.size * self.size

    # Neural Net
    input_boards = Input(shape=(self.size, self.size, 2))  # s: batch_size x board_x x board_y

    h_conv1 = Activation('relu')(BatchNormalization(axis=3)(
      Conv2D(num_channels, 3, padding='same')(input_boards)))  # batch_size  x board_x x board_y x num_channels
    h_conv2 = Activation('relu')(BatchNormalization(axis=3)(
      Conv2D(num_channels, 3, padding='same')(h_conv1)))  # batch_size  x board_x x board_y x num_channels
    h_conv3 = Activation('relu')(BatchNormalization(axis=3)(
      Conv2D(num_channels, 3, padding='valid')(h_conv2)))  # batch_size  x (board_x-2) x (board_y-2) x num_channels
    h_conv4 = Activation('relu')(BatchNormalization(axis=3)(
      Conv2D(num_channels, 3, padding='valid')(h_conv3)))  # batch_size  x (board_x-4) x (board_y-4) x num_channels
    h_conv4_flat = Flatten()(h_conv4)
    s_fc1 = Dropout(0.3)(
      Activation('relu')(BatchNormalization(axis=1)(Dense(1024)(h_conv4_flat))))  # batch_size x 1024
    s_fc2 = Dropout(0.3)(
      Activation('relu')(BatchNormalization(axis=1)(Dense(512)(s_fc1))))  # batch_size x 1024
    self.pi = Dense(action_size, activation='softmax', name='policy_head')(s_fc2)  # batch_size x action_size
    self.v = Dense(1, activation='tanh', name='value_head')(s_fc2)  # batch_size x 1

    self.model = Model(inputs=input_boards, outputs=[self.pi, self.v])
    self.model.compile(loss=['categorical_crossentropy', 'mean_squared_error'], optimizer=Adam(lr))

  def build_model(self):
    residual_blocks=19 # 根据AlphzZero论文，这里是19或39个残差块。为了在小棋盘上迅速验证效果，小棋盘时候可以进行适当缩减
    input_shape=(self.size, self.size, 4)
    # Step 1: 256 filters of kernel size 3x3 with stride 1
    inputs = Input(shape=input_shape)
    x = Conv2D(256, 3, padding="same", strides=1)(inputs)
    x = BatchNormalization(axis=-1)(x)
    x = Activation("relu")(x)

    # Step 2: 19 or 39 residual blocks
    for _ in range(residual_blocks):
        residual_input = x
        # Convolution 1
        x = Conv2D(256, 3, padding="same", strides=1)(x)
        x = BatchNormalization(axis=-1)(x)
        x = Activation("relu")(x)
        # Convolution 2
        x = Conv2D(256, 3, padding="same", strides=1)(x)
        x = BatchNormalization(axis=-1)(x)
        # Add skip connection
        x = Add()([x, residual_input])
        x = Activation("relu")(x)

    # Step 3: Policy head
    policy_head = Conv2D(2, 1, padding="same", strides=1)(x)
    policy_head = BatchNormalization(axis=-1)(policy_head)
    policy_head = Activation("relu")(policy_head)
    policy_head = Flatten()(policy_head)
    policy_head = Dense(self.size * self.size, activation="softmax", name="policy_head")(policy_head)

    # Step 4: Value head
    value_head = Conv2D(1, 1, padding="same", strides=1)(x)
    value_head = BatchNormalization(axis=-1)(value_head)
    value_head = Activation("relu")(value_head)
    value_head = Flatten()(value_head)
    value_head = Dense(256, activation="relu")(value_head)
    value_head = Dense(1, activation="tanh", name="value_head")(value_head)

    self.model = Model(inputs=inputs, outputs=[policy_head, value_head])
    self.model.compile(optimizer=Adam(lr), loss=["categorical_crossentropy", "mean_squared_error"])


  def predict(self, state):
    # start = time.time()
    pi, v = self.model(state, training=False)
    #print('model time', time.time()-start)
    #start = time.time()
    #self.model.predict(state, batch_size=17)
    #print('predict time', time.time()-start)
    return pi.numpy()[0], v.numpy()[0]

  def train(self, x, v, pi):
    return self.model.fit(x, {'policy_head': pi, 'value_head': v}, epochs=self.epochs)

  def save(self, filepath):
    self.model.save_weights(filepath)

  def load(self, filepath):
    self.model.load_weights(filepath)

  def set_lr(self, lr):
    self.model.optimizer.lr.assign(lr)

  def get_lr(self):
    return self.model.optimizer.lr.read_value()

  def set_epochs(self, epochs):
    self.epochs = epochs
