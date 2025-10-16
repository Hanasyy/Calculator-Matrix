import numpy as np

def tambah_vector(v1, v2):
    return np.add(v1, v2)

def kurang_vector(v1, v2):
    return np.subtract(v1, v2)

def dot_product(v1, v2):
    return np.dot(v1, v2)

def cross_product(v1, v2):
    return np.cross(v1, v2)

def magnitude(v):
    return np.linalg.norm(v)
