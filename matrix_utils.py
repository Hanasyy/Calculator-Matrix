import re
import numpy as np

# =======================================
# Utility format & cetak matriks
# =======================================
def fmt(x):
    """Format angka agar tampil rapi dan mudah dibaca."""
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return f"{x:.4f}"

def cetak_matriks(M):
    """Mengembalikan string representasi matriks."""
    return "\n".join(" ".join(fmt(x) for x in row) for row in M)

def _row_to_str(r):
    return " | ".join(fmt(x) for x in r)

# =======================================
# RREF (Gauss-Jordan) dinamis dengan langkah
# =======================================
def rref_with_steps(A_in, B_in=None, eps=1e-12):
    """
    Mengubah matriks A (atau [A|B]) menjadi bentuk eselon baris tereduksi (RREF).
    Dinamis untuk ukuran berapapun, disertai langkah-langkah operasi baris elementer.
    """
    A = np.array(A_in, dtype=float)
    if B_in is not None:
        B = np.array(B_in, dtype=float).reshape(-1, 1)
        M = np.hstack([A, B])
    else:
        M = A.copy()

    n_rows, n_cols = M.shape
    steps = []
    pivot_row = 0

    for pivot_col in range(n_cols - (1 if B_in is not None else 0)):
        # Cari baris pivot (nilai absolut terbesar)
        max_row = np.argmax(np.abs(M[pivot_row:, pivot_col])) + pivot_row
        if abs(M[max_row, pivot_col]) < eps:
            continue  # tidak ada pivot di kolom ini

        # Tukar baris jika perlu
        if pivot_row != max_row:
            M[[pivot_row, max_row]] = M[[max_row, pivot_row]]
            steps.append(f"Tukar baris {pivot_row+1} ↔ baris {max_row+1}\n{cetak_matriks(M)}")

        # Normalisasi baris pivot
        pivot_val = M[pivot_row, pivot_col]
        M[pivot_row] /= pivot_val
        steps.append(f"Normalisasi baris {pivot_row+1} (÷ {fmt(pivot_val)})\n{cetak_matriks(M)}")

        # Hilangkan elemen lain di kolom pivot
        for r in range(n_rows):
            if r != pivot_row and abs(M[r, pivot_col]) > eps:
                factor = M[r, pivot_col]
                M[r] -= factor * M[pivot_row]
                steps.append(f"Baris {r+1} - ({fmt(factor)} × baris {pivot_row+1})\n{cetak_matriks(M)}")

        pivot_row += 1
        if pivot_row == n_rows:
            break

    M[np.abs(M) < eps] = 0.0
    steps.append("\n=== HASIL RREF ===\n" + cetak_matriks(M))
    return M, steps

# =======================================
# OBE solver umum (A·x = B)
# =======================================
def solve_obe(A, B):
    """
    Menyelesaikan sistem linear A·x = B dengan eliminasi Gauss-Jordan.
    Dinamis untuk ukuran apapun.
    """
    A = np.array(A, dtype=float)
    B = np.array(B, dtype=float).reshape(-1, 1)
    M, steps = rref_with_steps(A, B)

    n_rows, n_cols = M.shape
    n_vars = n_cols - 1
    eps = 1e-9

    # Deteksi sistem tidak konsisten
    for i in range(n_rows):
        if np.all(np.abs(M[i, :n_vars]) < eps) and abs(M[i, -1]) > eps:
            steps.append(f"Baris {i+1} menunjukkan sistem tak konsisten.")
            return None, steps, "tidak_konsisten"

    # Temukan kolom pivot
    pivots = []
    for i in range(n_rows):
        for j in range(n_vars):
            if abs(M[i, j] - 1) < eps and np.all(np.abs(np.delete(M[:, j], i)) < eps):
                pivots.append(j)
                break
    free_vars = [j for j in range(n_vars) if j not in pivots]

    # Solusi unik
    if len(pivots) == n_vars:
        x = np.zeros(n_vars)
        for i in range(len(pivots)):
            x[pivots[i]] = M[i, -1]
        steps.append("\n=== Solusi unik ===")
        for i, val in enumerate(x, start=1):
            steps.append(f"x{i} = {fmt(val)}")
        return x, steps, "unik"

    # Solusi tak hingga
    particular = np.zeros(n_vars)
    for i in range(n_rows):
        row = M[i, :n_vars]
        if 1 in row:
            pivot_col = np.where(row == 1)[0][0]
            particular[pivot_col] = M[i, -1]

    basis = []
    for f in free_vars:
        vec = np.zeros(n_vars)
        vec[f] = 1
        for i in range(n_rows):
            row = M[i, :n_vars]
            if 1 in row:
                pivot_col = np.where(row == 1)[0][0]
                vec[pivot_col] = -M[i, f]
        basis.append(vec)

    steps.append("\n=== Solusi tak hingga ===")
    steps.append(f"Variabel bebas: {[f'x{v+1}' for v in free_vars]}")
    steps.append(f"x_partikular = [{', '.join(fmt(x) for x in particular)}]")
    for i, b in enumerate(basis, 1):
        steps.append(f"t{i} * [{', '.join(fmt(x) for x in b)}]")

    return (particular, free_vars, basis), steps, "tak_hingga"

# =======================================
# Sistem homogen A·x = 0
# =======================================
def solve_homogeneous(A):
    """
    Menyelesaikan sistem homogen A·x = 0.
    Menghasilkan variabel bebas & basis ruang null.
    """
    A = np.array(A, dtype=float)
    R, steps = rref_with_steps(A)
    n_rows, n_cols = R.shape
    eps = 1e-9

    pivots = []
    for i in range(n_rows):
        for j in range(n_cols):
            if abs(R[i, j] - 1) < eps and np.all(np.abs(np.delete(R[:, j], i)) < eps):
                pivots.append(j)
                break

    free_vars = [j for j in range(n_cols) if j not in pivots]
    basis = []

    for f in free_vars:
        v = np.zeros(n_cols)
        v[f] = 1
        for i in range(n_rows):
            row = R[i, :n_cols]
            if 1 in row:
                pivot_col = np.where(row == 1)[0][0]
                v[pivot_col] = -R[i, f]
        basis.append(v)

    steps.append("\n=== Ruang Null ===")
    if basis:
        for i, b in enumerate(basis, 1):
            steps.append(f"Basis {i}: [{', '.join(fmt(x) for x in b)}]")
    else:
        steps.append("Hanya solusi trivial (semua nol).")

    return free_vars, basis, steps

# =======================================
# Operasi matriks umum
# =======================================
def det(A):
    """Determinannya dinamis."""
    return float(np.linalg.det(np.array(A, dtype=float)))

def inverse(A):
    """Invers matriks dinamis."""
    A = np.array(A, dtype=float)
    if abs(np.linalg.det(A)) < 1e-12:
        raise ValueError("Matriks singular — tidak memiliki invers.")
    return np.linalg.inv(A)

def transpose(A):
    """Transpose dinamis."""
    return np.array(A, dtype=float).T

def rank(A):
    """Menghitung rank matriks secara dinamis."""
    return np.linalg.matrix_rank(np.array(A, dtype=float))

# =======================================
# Operasi vektor dinamis
# =======================================
def vec_add(u, v):
    return np.array(u, dtype=float) + np.array(v, dtype=float)

def vec_sub(u, v):
    return np.array(u, dtype=float) - np.array(v, dtype=float)

def dot(u, v):
    return float(np.dot(u, v))

def cross(u, v):
    return np.cross(u, v)

def norm(u):
    return float(np.linalg.norm(np.array(u, dtype=float)))

def projection(u, v):
    v = np.array(v, dtype=float)
    if np.allclose(v, 0):
        raise ValueError("Tidak dapat memproyeksikan ke vektor nol.")
    return (np.dot(u, v) / np.dot(v, v)) * v

def angle_between(u, v):
    u = np.array(u, dtype=float)
    v = np.array(v, dtype=float)
    cos = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
    cos = max(min(cos, 1.0), -1.0)
    return np.arccos(cos)
