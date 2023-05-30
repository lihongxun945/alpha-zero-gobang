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
from tensorflow.keras.layers import Input, Dense, Conv2D, Flatten, Reshape
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.optimizers import Adam

lr = 0.001
epochs = 20

class Net:
  def __init__(self, size=15):
    self.size = size
    self.build_model()

  def build_model(self):
    inp = Input((17, self.size, self.size))

    # 首先将输入转换为 ResNet50 需要的形状 (size, size, 3)
    # x = Conv2D(3, (1, 1))(inp)  # 使用 1x1 卷积增加通道数，这不会改变空间维度
    # x = Reshape((self.size, self.size, 3))(x)  # 将形状转换为 ResNet50 需要的 (size, size, 3)

    base_model = ResNet50(include_top=False, weights=None, input_tensor=inp)

    x = base_model.output
    x = Flatten()(x)

    # 添加两个输出层
    policy_output = Dense(self.size * self.size, activation='softmax', name='policy_output')(x)
    value_output = Dense(1, activation='tanh', name='value_output')(x)

    self.model = tf.keras.models.Model(inputs=base_model.input, outputs=[policy_output, value_output])
    self.model.compile(loss={'policy_output': 'categorical_crossentropy', 'value_output': 'mse'},
                       optimizer=Adam(lr),
                       metrics={'policy_output': 'accuracy', 'value_output': 'mse'})

  def predict(self, state):
    return self.model.predict(state)

  def train(self, x, v, pi):
    return self.model.fit(x, {'policy_output': pi, 'value_output': v}, epochs=epochs)

  def save(self, filepath):
    self.model.save_weights(filepath)

  def load(self, filepath):
    self.model.load_weights(filepath)
