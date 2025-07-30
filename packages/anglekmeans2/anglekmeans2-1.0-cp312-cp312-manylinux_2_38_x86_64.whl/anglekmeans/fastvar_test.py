import numpy as np
from utils_ import malloc_align_py
from fastvar_ import compute_mask_py, compute_COS_OCX_py, compute_COS_OCiCj_py

num = 640
clu = 8*10
dim = 8*5

C = malloc_align_py(clu, dim)

c_norm = malloc_align_py(clu, 1)
c_norm = c_norm.reshape(-1)

D_CC = malloc_align_py(clu, clu)
D_CC[:] = 0

OCiCj = malloc_align_py(clu, clu)


# verify compute_COS_OCiCj_py
compute_COS_OCiCj_py(C, c_norm, D_CC, OCiCj)
print(c_norm)

ret = np.einsum("ij,ij->i", C, C)
print(ret)


# print(OCiCj)