import h5py
import os
import numpy as np
import argparse
from tqdm import tqdm
import matplotlib.pyplot as plt

h5_path = '/data2/ranxiangyu/patch_test/patches/22811he.h5'

with h5py.File(h5_path, 'r') as f:
        coords = f['coords'][:]

print(coords)

# 打印坐标信息
print("坐标形状:", coords.shape)
print("坐标数量:", len(coords))
print("坐标类型:", coords.dtype)

# 打印前10个坐标点(如果有的话)
print("\n前10个坐标点:")
for i in range(min(10, len(coords))):
    print(f"坐标 {i+1}: ({coords[i][0]}, {coords[i][1]})")

# 打印坐标范围
if len(coords) > 0:
    x_min, x_max = int(coords[:, 0].min()), int(coords[:, 0].max())
    y_min, y_max = int(coords[:, 1].min()), int(coords[:, 1].max())
    print(f"\nX坐标范围: {x_min} 到 {x_max}")
    print(f"Y坐标范围: {y_min} 到 {y_max}")

