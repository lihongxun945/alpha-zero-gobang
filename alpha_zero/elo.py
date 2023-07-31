import math
# 0 ~ 999: K = 30; 1000 ~ 1999: K = 15; 2000 ~ 2999: K = 10; 3000 ~ : K = 5
K_TABLE = [30, 15, 10, 5]
def calculate_elo(black, white, results):
    for result in results:
        k = K_TABLE[-1]
        if black < 3000:
            k = K_TABLE[math.floor(black / 1000)]
        expected_score = 1 / (1 + 10 ** ((white - black) / 400))
        black = black + k * (result - expected_score)
    return math.floor(black)
