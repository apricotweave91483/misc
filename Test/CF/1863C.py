for _ in range(int(input())):
    n, k = map(int, input().split())
    A = list(map(int, input().split()))
    C = set(A)
    not_in = [X for X in range(n + 1) if not X in C]
    print(not_in)
