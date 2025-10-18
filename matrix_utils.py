import numpy as np
from copy import deepcopy

def fmt(x):
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return f"{x:.4f}"

def cetak_matriks(M):
    M = np.array(M)
    rows = []
    for r in M:
        rows.append(" ".join(fmt(x) for x in r))
    return "\n".join(rows)

def _row_to_str(r):
    return " | ".join(fmt(x) for x in r)

def rref_with_steps(A_in, B_in=None, eps=1e-12):
    """
    Return RREF of A (or augmented [A|B]) with step-by-step descriptions.
    If B_in provided, treat augmented matrix.
    Returns: (RREF_matrix, pivots, steps)
    """
    A = np.array(A_in, dtype=float)
    steps = []
    if B_in is None:
        M = A.copy()
    else:
        B = np.array(B_in, dtype=float).reshape(-1, 1)
        M = np.hstack([A.copy(), B])

    rows, cols = M.shape
    n = rows
    m = cols
    pivot_cols = []
    r = 0
    for c in range(m if B_in is None else m-1):
        if r >= n:
            break
        # find pivot
        pivot = None
        maxrow = r + np.argmax(np.abs(M[r:, c]))
        if abs(M[maxrow, c]) > eps:
            pivot = maxrow
        if pivot is None:
            continue
        if pivot != r:
            M[[r, pivot]] = M[[pivot, r]]
            steps.append(f"Swap row {r+1} with row {pivot+1}: \n{_row_to_str(M[r])}\n{_row_to_str(M[pivot])}")
        # normalize pivot row
        pv = M[r, c]
        M[r] = M[r] / pv
        steps.append(f"Normalize row {r+1} by dividing by {fmt(pv)}: \n{_row_to_str(M[r])}")
        # eliminate other rows
        for i in range(n):
            if i != r and abs(M[i, c]) > eps:
                factor = M[i, c]
                M[i] = M[i] - factor * M[r]
                steps.append(f"Eliminate column {c+1} in row {i+1} using row {r+1} * {fmt(factor)} -> row {i+1}: \n{_row_to_str(M[i])}")
        pivot_cols.append(c)
        r += 1
    # final rounding small values to zero
    M[np.abs(M) < eps] = 0.0
    return M, pivot_cols, steps

def solve_obe(A, B):
    """
    Solve linear system A x = B using Gauss-Jordan (RREF) with steps.
    Returns: (solution_vector_or_None, steps, status)
    status: "unique", "infinite", "inconsistent"
    """
    A = np.array(A, dtype=float)
    B = np.array(B, dtype=float).reshape(-1, 1)
    M, pivots, steps = rref_with_steps(A, B)
    rows, cols = M.shape
    n = rows
    vars_count = cols - 1
    # check for inconsistency: a row [0 ... 0 | b] with b != 0
    for i in range(n):
        if all(abs(M[i, j]) < 1e-9 for j in range(vars_count)) and abs(M[i, -1]) > 1e-9:
            steps.append(f"Inconsistent row found at row {i+1}: { _row_to_str(M[i]) }")
            return None, steps, "inconsistent"
    # determine pivots
    pivot_cols = []
    for i in range(n):
        found = False
        for j in range(vars_count):
            if abs(M[i, j] - 1) < 1e-9 and all(abs(M[i, k]) < 1e-9 for k in range(j)) == False or abs(M[i, j]) == 1:
                # better find columns where there is a 1 and rest zeros in that column
                if abs(M[i, j] - 1) < 1e-8 and all(abs(M[k, j]) < 1e-8 for k in range(n) if k != i):
                    pivot_cols.append(j)
                    found = True
                    break
        # continue
    pivot_cols = sorted(set(pivot_cols))
    free_vars = [j for j in range(vars_count) if j not in pivot_cols]

    if len(free_vars) == 0 and len(pivot_cols) == vars_count:
        # unique solution: read off last column
        x = np.zeros(vars_count)
        for i in range(n):
            # find pivot col
            for j in range(vars_count):
                if abs(M[i, j] - 1) < 1e-9:
                    x[j] = M[i, -1]
                    break
        steps.append("Unique solution found.")
        return x, steps, "unique"
    else:
        # infinite solutions: express parametric form
        steps.append(f"Free variables: {free_vars}")
        # construct parametric solution: x = sum t_k * v_k + particular (if any)
        # attempt to extract particular solution (set free vars = 0)
        particular = np.zeros(vars_count)
        for i in range(n):
            # find pivot column
            pivot_col = None
            for j in range(vars_count):
                if abs(M[i, j] - 1) < 1e-9 and all(abs(M[k, j]) < 1e-9 for k in range(n) if k != i):
                    pivot_col = j
                    break
            if pivot_col is not None:
                particular[pivot_col] = M[i, -1]
        # basis vectors for each free var
        basis = []
        for free in free_vars:
            vec = np.zeros(vars_count)
            vec[free] = 1.0
            # set other variables according to -coefficients in rref
            for i in range(n):
                # pivot col in this row?
                pivot_col = None
                for j in range(vars_count):
                    if abs(M[i, j] - 1) < 1e-9 and all(abs(M[k, j]) < 1e-9 for k in range(n) if k != i):
                        pivot_col = j
                        break
                if pivot_col is not None:
                    vec[pivot_col] = -M[i, free]
            basis.append(vec)
        steps.append(f"Particular solution (free vars = 0): [{', '.join(fmt(x) for x in particular)}]")
        for idx, free in enumerate(free_vars):
            steps.append(f"Parameter t{idx+1} corresponds to variable x{free+1} with basis vector: [{', '.join(fmt(x) for x in basis[idx])}]")
        return (particular, free_vars, basis), steps, "infinite"

def solve_homogeneous(A):
    """
    Solve A x = 0. Return parametric solution as (free_vars, basis_vectors)
    basis_vectors: list of vectors forming basis of nullspace
    """
    A = np.array(A, dtype=float)
    # perform RREF on A only
    R, pivots, steps = rref_with_steps(A, None)
    rows, cols = R.shape
    n = rows
    vars_count = cols
    pivot_cols = []
    for i in range(n):
        for j in range(vars_count):
            if abs(R[i, j] - 1) < 1e-9 and all(abs(R[k, j]) < 1e-9 for k in range(n) if k != i):
                pivot_cols.append(j)
                break
    free_vars = [j for j in range(vars_count) if j not in pivot_cols]
    basis = []
    if len(free_vars) == 0:
        # only trivial solution
        return [], []
    for free in free_vars:
        v = np.zeros(vars_count)
        v[free] = 1.0
        for i in range(n):
            # locate pivot col
            pivot_col = None
            for j in range(vars_count):
                if abs(R[i, j] - 1) < 1e-9 and all(abs(R[k, j]) < 1e-9 for k in range(n) if k != i):
                    pivot_col = j
                    break
            if pivot_col is not None:
                v[pivot_col] = -R[i, free]
        basis.append(v)
    return free_vars, basis

def det(A):
    return np.linalg.det(np.array(A, dtype=float))

def inverse(A):
    A = np.array(A, dtype=float)
    if abs(np.linalg.det(A)) < 1e-12:
        raise ValueError("Matrix singular.")
    return np.linalg.inv(A)

# vector utilities
def vec_add(u, v):
    u = np.array(u, dtype=float)
    v = np.array(v, dtype=float)
    return u + v

def vec_sub(u, v):
    u = np.array(u, dtype=float)
    v = np.array(v, dtype=float)
    return u - v

def dot(u, v):
    return float(np.dot(u, v))

def cross(u, v):
    return np.cross(u, v)

def norm(u):
    u = np.array(u, dtype=float)
    return float(np.linalg.norm(u))

def projection(u, v):
    # projection of u onto v (vector)
    v = np.array(v, dtype=float)
    if np.allclose(v, 0):
        raise ValueError("Cannot project onto zero vector")
    return (np.dot(u, v) / np.dot(v, v)) * v

def angle_between(u, v):
    u = np.array(u, dtype=float)
    v = np.array(v, dtype=float)
    cos = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
    cos = max(min(cos, 1.0), -1.0)
    return np.arccos(cos)
