#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

typedef long long i64;

typedef struct {
    i64 num;
    i64 den;
} Rat;

/* ---------- Rational arithmetic ---------- */

static i64 i64_abs(i64 x) { return x < 0 ? -x : x; }

static i64 gcd_i64(i64 a, i64 b) {
    a = i64_abs(a); b = i64_abs(b);
    while (b) {
        i64 t = a % b;
        a = b;
        b = t;
    }
    return a ? a : 1;
}

static Rat rat_norm(Rat r) {
    if (r.num == 0) { r.den = 1; return r; }
    if (r.den < 0) { r.den = -r.den; r.num = -r.num; }
    i64 g = gcd_i64(r.num, r.den);
    r.num /= g;
    r.den /= g;
    return r;
}

static Rat rat_from_i64(i64 x) { return (Rat){x,1}; }
static int rat_is_zero(Rat r) { return r.num == 0; }

static Rat rat_add(Rat a, Rat b) {
    return rat_norm((Rat){a.num*b.den + b.num*a.den, a.den*b.den});
}

static Rat rat_sub(Rat a, Rat b) {
    return rat_norm((Rat){a.num*b.den - b.num*a.den, a.den*b.den});
}

static Rat rat_mul(Rat a, Rat b) {
    return rat_norm((Rat){a.num*b.num, a.den*b.den});
}

static Rat rat_div(Rat a, Rat b) {
    if (b.num == 0) { fprintf(stderr, "Divide by zero\n"); exit(1); }
    return rat_norm((Rat){a.num*b.den, a.den*b.num});
}

static Rat rat_neg(Rat a) { return (Rat){-a.num, a.den}; }

static Rat rat_parse(const char *s) {
    char *slash = strchr(s, '/');
    if (!slash) return rat_from_i64(atoll(s));
    i64 a = atoll(s);
    i64 b = atoll(slash + 1);
    return rat_norm((Rat){a, b});
}

static void rat_print(Rat r) {
    if (r.den == 1) printf("%lld", (long long)r.num);
    else printf("%lld/%lld", (long long)r.num, (long long)r.den);
}

/* ---------- Matrix helpers ---------- */

static Rat **mat_alloc(int m, int n) {
    Rat **A = calloc(m, sizeof(*A));
    for (int i = 0; i < m; i++)
        A[i] = calloc(n, sizeof(**A));
    return A;
}

static void mat_free(Rat **A, int m) {
    for (int i = 0; i < m; i++) free(A[i]);
    free(A);
}

static void swap_rows(Rat **A, int r1, int r2, int n) {
    if (r1 == r2) return;
    for (int j = 0; j < n; j++) {
        Rat t = A[r1][j];
        A[r1][j] = A[r2][j];
        A[r2][j] = t;
    }
}

static void print_matrix(Rat **A, int m, int n) {
    for (int i = 0; i < m; i++) {
        printf("[ ");
        for (int j = 0; j < n; j++) {
            rat_print(A[i][j]);
            if (j < n-1) printf("\t");
        }
        printf(" ]\n");
    }
}

/* ---------- RREF ---------- */

static void rref(Rat **A, int m, int n, int *pivot_col, int *is_pivot) {
    memset(is_pivot, 0, n * sizeof(int));
    for (int i = 0; i < m; i++) pivot_col[i] = -1;

    int lead = 0;
    for (int r = 0; r < m && lead < n; r++) {
        int i = r;
        while (i < m && rat_is_zero(A[i][lead])) i++;
        if (i == m) { lead++; r--; continue; }

        swap_rows(A, r, i, n);

        Rat piv = A[r][lead];
        for (int j = 0; j < n; j++)
            A[r][j] = rat_div(A[r][j], piv);

        for (int rr = 0; rr < m; rr++) {
            if (rr == r) continue;
            Rat f = A[rr][lead];
            if (rat_is_zero(f)) continue;
            for (int j = 0; j < n; j++)
                A[rr][j] = rat_sub(A[rr][j], rat_mul(f, A[r][j]));
        }

        pivot_col[r] = lead;
        is_pivot[lead] = 1;
        lead++;
    }
}

/* ---------- Main ---------- */

int main(void) {
    int m;
    if (scanf("%d", &m) != 1 || m <= 0) return 1;
    getchar(); // eat newline

    char line[1024];
    Rat **A = NULL;
    int n = -1;

    for (int i = 0; i < m; i++) {
        fgets(line, sizeof(line), stdin);

        char *tok;
        int count = 0;

        // First pass: count columns
        char tmp[1024];
        strcpy(tmp, line);
        tok = strtok(tmp, " \t\n");
        while (tok) { count++; tok = strtok(NULL, " \t\n"); }

        if (i == 0) {
            n = count;
            A = mat_alloc(m, n);
        } else if (count != n) {
            fprintf(stderr, "Row %d has wrong number of columns\n", i+1);
            return 1;
        }

        // Second pass: parse
        tok = strtok(line, " \t\n");
        for (int j = 0; j < n; j++) {
            A[i][j] = rat_parse(tok);
            tok = strtok(NULL, " \t\n");
        }
    }

    int vars = n - 1;
    int *pivot_col = malloc(sizeof(int)*m);
    int *is_pivot = calloc(n, sizeof(int));

    rref(A, m, n, pivot_col, is_pivot);

    printf("\nRREF:\n");
    print_matrix(A, m, n);

    // Inconsistency check
    for (int i = 0; i < m; i++) {
        int all_zero = 1;
        for (int j = 0; j < vars; j++)
            if (!rat_is_zero(A[i][j])) all_zero = 0;
        if (all_zero && !rat_is_zero(A[i][vars])) {
            printf("\nNO SOLUTION\n");
            return 0;
        }
    }

    int rank = 0;
    for (int j = 0; j < vars; j++) if (is_pivot[j]) rank++;

    if (rank == vars) {
        printf("\nUNIQUE SOLUTION:\n");
        for (int j = 0; j < vars; j++)
            for (int i = 0; i < m; i++)
                if (pivot_col[i] == j) {
                    printf("x%d = ", j+1);
                    rat_print(A[i][vars]);
                    printf("\n");
                }
    } else {
        printf("\nINFINITE SOLUTIONS\n");
        int t = 1;
        int *free = malloc(sizeof(int)*vars);

        for (int j = 0; j < vars; j++)
            if (!is_pivot[j]) free[t-1] = j, t++;

        for (int k = 0; k < t-1; k++)
            printf("x%d = t%d\n", free[k]+1, k+1);

        for (int j = 0; j < vars; j++) {
            if (!is_pivot[j]) continue;
            for (int i = 0; i < m; i++) if (pivot_col[i] == j) {
                printf("x%d = ", j+1);
                rat_print(A[i][vars]);
                for (int k = 0; k < t-1; k++) {
                    Rat a = A[i][free[k]];
                    if (!rat_is_zero(a)) {
                        if (a.num > 0) printf(" - ");
                        else { printf(" + "); a = rat_neg(a); }
                        rat_print(a);
                        printf("*t%d", k+1);
                    }
                }
                printf("\n");
            }
        }
    }

    mat_free(A, m);
    free(pivot_col);
    free(is_pivot);
    return 0;
}

