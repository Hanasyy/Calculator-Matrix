import numpy as np

def export_matrix(filename, matrices):
    with open(filename, "w") as f:
        for name, mat in matrices.items():
            f.write(f"[{name}]\n")
            np.savetxt(f, mat, fmt="%.4f")
            f.write("\n")

def import_matrix(filename):
    matrices = {}
    with open(filename, "r") as f:
        lines = f.read().splitlines()
    current_name = None
    current_data = []
    for line in lines:
        if line.startswith("[") and line.endswith("]"):
            if current_name:
                matrices[current_name] = np.array(current_data, dtype=float)
            current_name = line.strip("[]")
            current_data = []
        elif line.strip():
            current_data.append([float(x) for x in line.split()])
    if current_name:
        matrices[current_name] = np.array(current_data, dtype=float)
    return matrices
