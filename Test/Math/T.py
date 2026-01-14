#!/opt/homebrew/bin/python3

import numpy as np

A = np.array([list(map(int, input().split())) for i in range(int(input()))])
print(A)
