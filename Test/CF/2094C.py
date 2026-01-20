for _ in range(int(input())):
    N = int(input())
    SYS = []
    for __ in range(N):
        SYS.append(list(map(int, input().split())))
    IN = set()
    ANS = [None] * (2 * N)
    for r in range(len(SYS)):
        for i in range(len(SYS[r])):
            ANS[1 + i + r] = SYS[r][i]
            IN.add(SYS[r][i])
    NIN = set([i for i in range(1, 2 * N + 1) if not i in IN])
    for i in range(2 * N):
        if ANS[i] is None:
            ANS[i] = NIN.pop()
    
    for x in ANS:
        print(x, end=" ")
    print()



