import numpy as np

def cetak_matriks(M):
    return "\n".join(" ".join(str(int(x)) if float(x).is_integer() else f"{x:.2f}" for x in row) for row in M)

def solve_obe(A, B):
    A = A.astype(float)
    B = np.array(B, dtype=float).flatten()
    n = len(B)
    M = np.hstack([A, B.reshape(-1, 1)])
    steps = []
    for i in range(n):
        if M[i, i] == 0:
            for j in range(i+1, n):
                if M[j, i] != 0:
                    M[[i, j]] = M[[j, i]]
                    steps.append(f"Tukar baris {i+1} dan {j+1}")
                    break
        pivot = M[i, i]
        M[i] = M[i] / pivot
        steps.append(f"Bagi baris {i+1} dengan {pivot:.2f}")
        for j in range(n):
            if j != i:
                factor = M[j, i]
                M[j] = M[j] - factor * M[i]
                steps.append(f"Baris {j+1} - ({factor:.2f})*Baris {i+1}")
    return M[:, -1], steps

def solve_inverse(A, B):
    A_inv = np.linalg.inv(A)
    X = A_inv @ B
    steps = [f"Invers A:\n{cetak_matriks(A_inv)}", f"Hasil X = A_inv @ B:\n{cetak_matriks(X.reshape(-1, 1))}"]
    return X, steps

def solve_cramer(A, B):
    detA = np.linalg.det(A)
    if detA == 0:
        raise ValueError("Determinan 0, Cramer tidak bisa.")
    n = len(B)
    X = np.zeros(n)
    steps = [f"det(A) = {detA:.2f}"]
    for i in range(n):
        Ai = A.copy()
        Ai[:, i] = B
        detAi = np.linalg.det(Ai)
        X[i] = detAi / detA
        steps.append(f"det(A_{i+1}) = {detAi:.2f} → x_{i+1} = {X[i]:.2f}")
    return X, steps
