from collections import Counter
for _ in range(int(input())):
    C = Counter(input() + input())
    print(len(C) - 1)
