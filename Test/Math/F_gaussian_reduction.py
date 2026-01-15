#!/opt/homebrew/bin/python3

from fractions import Fraction
import numpy as np

DTYPE = Fraction

A = np.array([list(map(DTYPE, input().split())) for i in range(int(input()))], dtype=DTYPE)

total_row = len(A)
total_column = len(A[0])

def first_nonzero(array):
    z = (np.nonzero(array))[0]

    if z.size:
        return z[0]

    return np.inf

def make_swap(start):
    global A

    F = first_nonzero(A[start])
    L = None
    G = 0

    for i in range(start + 1, len(A)):
        L = first_nonzero(A[i])
        if L < F:
            G = 1
            break

    if G:
        A[[i, start]] = A[[start, i]]
        return

    return

def ref():
    global A, total_row, total_column

    curr_row = 0
    curr_column = 0

    while curr_row < total_row and curr_column < total_column:
        make_swap(curr_row)

        if A[curr_row][curr_column] == 0:
            curr_column += 1
            continue

        A[curr_row] /= A[curr_row][curr_column]
        for i in range(curr_row + 1, total_row):
            A[i] -= (A[i][curr_column] * A[curr_row])
    
        curr_row += 1
        curr_column += 1

def find_pivots() -> set[tuple]:
    # Only works if REF already
    global A

    pivots = set()

    for row_num, row in enumerate(A):
        for i, x in enumerate(row):
            if x:
                pivots.add((row_num, i))
                break

    return pivots

def rref():
    global A

    pivots = find_pivots()

    for pivot in pivots:
        r, c = pivot[0], pivot[1]
        for i in range(r - 1, -1, -1):
            A[i] -= (A[r] * A[i][c])

    return

def parameterize_infinite_solutions():
    pivots = find_pivots()

    basic = set()
    for pivot in pivots:
        basic.add(pivot[1])
    free = set(v for v in range(total_column - 1) if not v in basic)

    maps = {}

    for f in free:
        t = [0] * (total_column) 
        t[f] = 1
        maps[f] = tuple(t)

    for pivot in pivots:
        t = list(A[pivot[0]])
        for x in range(total_column - 1):
            t[x] *= -1
        maps[pivot[1]] = tuple(t)
    
    rep = []
    
    rep.append(tuple(maps[i][-1] for i in range(total_column - 1)))
    for x in range(total_column - 1):
        if x in free:
            rep.append(x)
            t = []
            for j in range(total_column - 1):
                t.append(maps[j][x])
            rep.append(tuple(t))
    
    ret_str = []
    
    ret_str.append("[" + "  ".join(str(x) for x in rep[0]) + "]")
    for i in range(1, len(rep), 2):
        ret_str.append(f"x{rep[i] + 1}[" + "  ".join(str(x) for x in rep[i + 1]) + "]")
    return " + ".join(ret_str)


def interpret():
    # No Solution
    for row in A:
        nz = (np.nonzero(row))[0]
        if len(nz) == 1 and nz[0] == total_row - 1:
            return 0
    
    pivots = find_pivots()
    
    # One Solution
    if len(pivots) == total_column - 1:
        return np.array([A[i][-1] for i in range(total_row)])
    
    # Infinite Solutions
    return parameterize_infinite_solutions()
    
def print_solution():
    interpretation = interpret()

    if isinstance(interpretation, int):
        print("System Inconsistent/No Solution.")
    
    elif isinstance(interpretation, str):
        print("Infinite Solutions.")
        print(interpretation)
     
    else:
        print("[" + "  ".join(f"x{i + 1}" for i in range(total_column - 1)) + "]", end=" = ")
        if DTYPE is Fraction:
            print("[" + "  ".join(str(x) for x in interpretation) + "]")
        else:
            print(interpretation)
    return

ref()
rref()
print_solution()
