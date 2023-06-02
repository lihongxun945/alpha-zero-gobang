# -*- coding: utf-8 -*-
import sys
sys.path.append(r"..")
'''
写一个Net类的测试用例，用unittest来写
'''
import unittest
import tensorflow as tf
import numpy as np
from alpha_zero.board import Board
from alpha_zero.net import Net

class TestNet(unittest.TestCase):
  def setUp(self):
    self.size = 15
    self.net = Net(self.size)

  def test_predict(self):
    board = Board(self.size)
    x, y = board.get_data(100)
    x = np.expand_dims(x, axis=0)  # 转换为四维张量，因为模型需要 batch 维度
    # self.net.model.summary()
    probs, value = self.net.predict(x)
    self.assertEqual(probs.shape, (self.size*self.size,))
    self.assertEqual(value.shape, (1,))

  def test_train(self):
    board = Board(self.size)
    x, y = board.get_data(100)
    x = np.expand_dims(x, axis=0)  # 转换为四维张量，因为模型需要 batch 维度
    v, pi = y[0], y[1]
    v = np.array([v])
    pi = np.array([pi])
    history = self.net.train(x, v, pi)
    self.assertIsInstance(history, tf.keras.callbacks.History)

  def test_save_and_load(self):
    net = Net(15)
    net.save("test.h5")

    loaded_net = Net(15)
    loaded_net.load("test.h5")

    # Compare the weights of the two models
    for layer1, layer2 in zip(net.model.layers, loaded_net.model.layers):
      weights1 = layer1.get_weights()
      weights2 = layer2.get_weights()

      # For each layer, assert that the weights are almost equal
      for w1, w2 in zip(weights1, weights2):
        np.testing.assert_array_almost_equal(w1, w2)

if __name__ == "__main__":
  unittest.main()
