import time

N = 50_000


# ---------------------------
# Tiny Python function
# ---------------------------
def f(x, y):
    return (x + y) & 1


# ---------------------------
# 1. Raw Python nested loops
# ---------------------------
start = time.time()

s = 0
for i in range(N):
    for j in range(N):
        s += f(i, j)

end = time.time()
print("raw nested loops + function call:", end - start)


# ---------------------------
# 2. Generator + sum
# ---------------------------
start = time.time()

s = sum(
    f(i, j)
    for i in range(N)
    for j in range(N)
)

end = time.time()
print("generator + sum:", end - start)

