import numpy as np
import json
import csv
import os

def export_matrix_txt(filename, matrices):
    with open(filename, "w") as f:
        for name, mat in matrices.items():
            f.write(f"[{name}]\n")
            np.savetxt(f, mat, fmt="%.6f")
            f.write("\n")

def import_matrix_txt(filename):
    matrices = {}
    with open(filename, "r") as f:
        content = f.read()
    blocks = content.split("\n\n")
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        header = lines[0].strip()
        if header.startswith("[") and header.endswith("]"):
            name = header[1:-1]
            data = []
            for row in lines[1:]:
                if row.strip():
                    data.append([float(x) for x in row.split()])
            matrices[name] = np.array(data)
    return matrices

def export_matrix_json(filename, matrices):
    payload = {}
    for name, mat in matrices.items():
        payload[name] = np.array(mat).tolist()
    with open(filename, "w") as f:
        json.dump(payload, f, indent=2)

def import_matrix_json(filename):
    with open(filename, "r") as f:
        payload = json.load(f)
    matrices = {}
    for name, mat in payload.items():
        matrices[name] = np.array(mat, dtype=float)
    return matrices

def export_matrix_csv(filename, matrices):
    # if multiple matrices, write them sequentially with header rows
    with open(filename, "w", newline='') as f:
        writer = csv.writer(f)
        for name, mat in matrices.items():
            writer.writerow([f"[{name}]"])
            for row in mat:
                writer.writerow(row)
            writer.writerow([])

def import_matrix_csv(filename):
    matrices = {}
    with open(filename, "r", newline='') as f:
        reader = csv.reader(f)
        current = None
        rows = []
        for row in reader:
            if not row:
                if current:
                    matrices[current] = np.array(rows, dtype=float)
                    current = None
                    rows = []
                continue
            if len(row) == 1 and row[0].startswith("[") and row[0].endswith("]"):
                current = row[0][1:-1]
                rows = []
            else:
                # numeric row
                rows.append([float(x) for x in row])
        if current:
            matrices[current] = np.array(rows, dtype=float)
    return matrices

# Simple history persistence
def save_history(history_list, filename="history.json"):
    with open(filename, "w") as f:
        json.dump(history_list, f, indent=2)

def load_history(filename="history.json"):
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as f:
        return json.load(f)
