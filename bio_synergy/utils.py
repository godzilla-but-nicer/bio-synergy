import numpy as np


def to_binary(n, digits):
    binary_digits = []
    for _ in range(digits):
        binary_digits.append(int(n % 2))
        n = int(n / 2)
    return np.array(binary_digits[::-1])


def to_decimal(b):
    expos = np.arange(len(b), 0, -1) - 1
    enc = 2**expos
    return np.array(b).T.dot(enc)
