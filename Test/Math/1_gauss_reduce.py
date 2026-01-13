#!/opt/homebrew/bin/python3

from fractions import Fraction
from numpy import array

system = []

def print_system():
    for y in range(len(system)):
        for x in system[y]:
            print(x, end=' ')
        print()
    return

def sort_system(index: int, starting_row: int):
    global system
    final_sys = []
    poi = index
    curr_row = -1

    done = False
    while (poi < len(system[0])):
        for x in range(starting_row, len(system)):
            row = system[x]
            curr_row = x
            if row[poi] != 0:
                done = True
                break
        if done:
            break

        poi += 1
    for x in range(starting_row):
        final_sys.append(system[x])
    if curr_row != -1:
        final_sys.append(system[curr_row])
    for x in range(starting_row, len(system)):
        if x != curr_row:
            final_sys.append(system[x])
    system = final_sys
    return

def ref_system():
    global system
    size = len(system[0])
    row_cnt = len(system)
    curr_row = curr_column = 0

    while (curr_column < size and curr_row < row_cnt):
        sort_system(curr_column, curr_row)

        curr_pivot = system[curr_row][curr_column]        
        if not curr_pivot:
            curr_column += 1
            continue
        system[curr_row] /= curr_pivot

        for i in range(curr_row + 1, row_cnt):
            system[i] -= (system[curr_row] * system[i][curr_column])

        curr_row += 1
        curr_column += 1

def rref_system():
    # Only works after REF is done
    global system

    def find_piv(row):
        for i in range(len(row)):
            if row[i]:
                return i
        return -1


    last_pivot = (-1, -1)
    for row_num, row in enumerate(system):
        for i in range(len(row)):
            if row[i]:
                last_pivot = (row_num, i)
                break
    t = last_pivot[0]
    while t:
        for i in range(last_pivot[0] - 1, -1, -1):
            pass
            system[i] -= (system[last_pivot[0]] * system[i][last_pivot[1]])
        last_pivot = (t - 1, find_piv(system[t - 1]))
        t -= 1
    return
        
def interp_system():
    
    # Is it consistent?
    for row in system:
        zeroed = 1
        for x in row[:-1]:
            if x:
                zeroed = 0
                break
        if zeroed and row[-1]:
            return "NO SOLUTION"

    rank = 0
    for row in system:
        for x in row:
            if x:
                rank += 1
                break
    if rank == len(system):
        return "ONE SOLUTION"

    
    return "INF. SOLUTIONS"

for i in range(int(input())):
    system.append(array(list(map(Fraction, input().split()))))

ref_system()
print("\nREF:")
print_system()

rref_system()
print("\nRREF:")
print_system()

print("ANS:", interp_system())
