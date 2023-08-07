import random
def get_random_opening(size):
  center = size // 2
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
