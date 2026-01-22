from math import ceil
for _ in range(int(input())):
    a, b, c = map(int, input().split())
    S = -1
    if not (3 - (b % 3) > c) or not b % 3:
        S = a
        S += ceil((b + c)/3)
    print(S)

