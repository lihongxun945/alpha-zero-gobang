import numpy as np

def construct_weights(length, gamma=0.95):
  """
  :param length:
  :param gamma:
  :return:
  """
  w = np.empty(length, np.float32)
  w[length - 1] = 1.0  # 最靠后的权重最大
  for i in range(length - 2, -1, -1):
    w[i] = w[i + 1] * gamma
  return length * w / np.sum(w)  # 所有元素之和为length