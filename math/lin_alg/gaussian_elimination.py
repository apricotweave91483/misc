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
            return None

    rank = 0
    for row in system:
        for x in row:
            if x:
                rank += 1
                break
    if rank == len(system[0]) - 1:
        ans = tuple(system[x][-1] for x in range(rank))
        return ans

    return 1

def parameterize_solution():
    basics = []
    frees = []
    for row in system:
        for i, x in enumerate(row):
            if x:
                basics.append(i)
                break

    coeff_num = len(system[0]) - 1
    basic_set = set(basics)

    for i in range(coeff_num):
        if i not in basic_set:
            frees.append(i)
    
    i = 0
    maps = {}
    for coeff in range(coeff_num):
        temp = []
        if coeff in basic_set:
            for x in range(coeff_num): 
                temp.append(-1 * system[i][x])
            temp.append(system[i][-1])
            i += 1
        else:
            for j in range(coeff_num):
                temp.append(1 if j == coeff else 0)
            temp.append(0)

        maps[coeff] = temp.copy()
    
    right_hand = []
    right_hand.append(tuple([maps[coeff][-1] for coeff in range(coeff_num)]))

    for free_var in frees:
        right_hand.append(free_var)
        temp_coeff = []
        for coeff in range(coeff_num):
            temp_coeff.append(maps[coeff][free_var])
        right_hand.append(tuple(temp_coeff.copy()))

    return right_hand

def print_parameter(right_hand):
    coeff_num = len(system[0]) - 1

    def prettify(tup):
        return "(" + ", ".join([str(x) for x in tup]) + ")"

    print("(" + ", ".join(f"x{i}" for i in range(coeff_num)) + ")", end=" = ")

    for t in right_hand:
        if isinstance(t, tuple):
                print(prettify(t), end="")
        else:
            print(f" + x{t}", end="")

    print()

def print_answer(answer):
    if not answer:
        print("Inconsistent / No Solution.")

    elif isinstance(answer, tuple):
        print("(" + ", ".join([f"x{i}" for i in range(len(answer))]) + ")" + " = " + "(" + ", ".join([str(x) for x in answer]) + ")")

    elif answer == 1:
        print("Infinite Solutions:")
        print_parameter(parameterize_solution())

for i in range(int(input())):
    system.append(array(list(map(Fraction, input().split()))))

ref_system()
rref_system()

print("\nRREF:")
print_system()
print()

print_answer(interp_system())
