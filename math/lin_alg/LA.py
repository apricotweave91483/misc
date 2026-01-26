from fractions import Fraction

class Vector:
    def __init__(self, nums=[]):
        self._nums = list(map(Fraction, nums))
    def __repr__(self):
        return "Vector[" + " ".join(str(x) for x in self._nums) + "]"
    def __len__(self):
        return len(self._nums)
    def __mul__(self, scalar):
        return Vector([x * scalar for x in self._nums])
    def __truediv__(self, scalar):
        return Vector([x / scalar for x in self._nums])
    def __iter__(self):
        return iter(self._nums)
    def __getitem__(self, ind):
        return self._nums[ind]
    def __setitem__(self, ind, new):
        self._nums[ind] = new
    __rmul__ = __mul__
    def __matmul__(self, vec2):
        return sum(x * y for x, y in zip(self, vec2))
    def __add__(self, vec2):
        return Vector([x + y for x, y in zip(self, vec2)])
    def __sub__(self, vec2):
        return self + (vec2 * -1)
    def __abs__(self):
        return (sum(x ** 2 for x in self)) ** Fraction(1, 2)

class Matrix:
    def __init__(self, matrix=[[]]):
        self._rows = list(Vector(row) for row in matrix)
    def take(self):
        self._rows = list(Vector(input().split()) for i in range(int(input())))
    def __repr__(self):
        return "Matrix[\n" + "\n".join([" ".join(str(x) for x in row) for row in self._rows]) + "]"
    def __len__(self):
        return len(self._rows)
    def __getitem__(self, ind):
        return self._rows[ind]
    def __setitem__(self, ind, new):
        self._rows[ind] = new
    def __iter__(self):
        return iter(self._rows)
    def __mul__(self, obj2):
        if isinstance(obj2, Vector): #TODO
            pass
        if isinstance(obj2, Matrix): #TODO
            pass
        else:
            try:
                return Matrix(
                        [Vector([x * obj2 for x in row]) for row in self._rows]
                        )
            except:
                raise TypeError()
    __rmul__ = __mul__
    def __truediv__(self, scalar):
        return Matrix(
                [Vector([x / scalar for x in row]) for row in self._rows]
                )
    def __add__(self, obj2):
        return Matrix(
                [Vector([self[i][j] + obj2[i][j] for j in range(len(self[i]))]) for i in range(len(self))]
                )
    def __sub__(self, obj2):
        return self + (obj2 * -1)

    
    def det(self):
        def __det__(system) -> int:
            def sys_without(SYS, i):
                return [[row[j] for j in range(len(row)) if j != i] for row in SYS[1:]]
            if len(system) == 2:
                return (system[0][0] * system[-1][-1]) - (system[-1][0] * system[0][-1])
            else:
                return sum(((-1) ** x) * system[0][x] * __det__(sys_without(system, x)) for x in range(len(system[0])))
        return __det__(self._rows)



    def ref(self):
        def make_swap(rows, start):
            def first_nonzero(vec):
                for i in range(len(vec)):
                    if vec[i] != 0:
                        return i
                return float("inf")
            F = first_nonzero(rows[start])
            L = None
            G = 0

            for i in range(start + 1, len(rows)):
                L = first_nonzero(rows[i])
                if L < F:
                    G = 1
                    break
            if G:
                rows[i], rows[start] = rows[start], rows[i]

            return

        curr_row = 0
        curr_column = 0
        total_row = len(self)
        total_column = len(self[0])

        while curr_row < total_row and curr_column < total_column:
            make_swap(self, curr_row)

            if self[curr_row][curr_column] == 0:
                curr_column += 1
                continue

            self[curr_row] /= self[curr_row][curr_column]
            for i in range(curr_row + 1, total_row):
                self[i] -= (self[i][curr_column] * self[curr_row])
    
            curr_row += 1
            curr_column += 1
    
    def find_pivots(self) -> set[tuple]:
        # Only works if REF already

        pivots = set()

        for row_num, row in enumerate(self):
            for i, x in enumerate(row):
                if x:
                    pivots.add((row_num, i))
                    break

        return pivots

    def rref(self):
        pivots = self.find_pivots()

        for pivot in pivots:
            r, c = pivot[0], pivot[1]
            for i in range(r - 1, -1, -1):
                self[i] -= (self[r] * self[i][c])

        return

class System:
    def parse_eqs(self, lines):
        n = len(lines)
        eqs = lines

        vars_order = []
        parsed = []

        for eq in eqs:
            lhs, rhs = eq.replace(" ", "").split("=")
            rhs = int(rhs)

            terms = lhs.replace("-", "+-").split("+")
            coeffs = {}

            for term in terms:
                if not term:
                    continue
                if term[-1].isalpha():
                    var = term[-1]
                    coef = term[:-1]

                    if coef in ("", "+"):
                        coef = 1
                    elif coef == "-":
                        coef = -1
                    else:
                        coef = int(coef)

                    coeffs[var] = coef
                    if var not in vars_order:
                        vars_order.append(var)

            parsed.append((coeffs, rhs))

        # Build augmented matrix
        M = []
        for coeffs, rhs in parsed:
            row = [coeffs.get(v, 0) for v in vars_order]
            row.append(rhs)
            M.append(row)

        return M, vars_order

    def __init__(self, data=[[]]):
        if isinstance(data[0], (list, Vector)):
            self.Coeff_Matrix = Matrix(data)
            self.ordered_vars = [f"x{i}" for i in range(len(self.Coeff_Matrix[0]) - 1)]
        else:
            self.Coeff_Matrix, self.ordered_vars = self.parse_eqs(data)
            self.Coeff_Matrix = Matrix(self.Coeff_Matrix)
    def take1(self):
        self.Coeff_Matrix = Matrix([input().split() for i in range(int(input()))])
        self.ordered_vars = [f"x{i}" for i in range(len(self.Coeff_Matrix[0]) - 1)]
    def take2(self):
        self.Coeff_Matrix, self.ordered_vars = self.parse_eqs([input() for i in range(int(input()))])
        self.Coeff_Matrix = Matrix(self.Coeff_Matrix)
    def __repr__(self):
        return "System{" + " ".join(var for var in self.ordered_vars) + "}[\n" + "\n".join([" ".join(str(x) for x in row) for row in self.Coeff_Matrix]) + "]"

    def solve(self):
        self.Coeff_Matrix.ref()
        self.Coeff_Matrix.rref()

