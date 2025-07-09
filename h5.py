import h5py
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

"""
生成的h5文件解析
    kidney_wsi.h5
        └── coords  ← 这是唯一的主键，表示切片坐标      
        coords 是一个大小为 (308, 2) 的数组，代表切片后的 308 个图像块；
        
        每一行 [x, y] 是在 原始 WSI（Whole Slide Image）上每个切片块的左上角坐标；

        步长的逻辑是，x轴从上到下，再向y轴移动，从上到下
"""

# === 可配置参数 ===
h5_path = '/data2/ranxiangyu/patch_test/patches/22811he.h5'
csv_output = '/data2/ranxiangyu/patch_test/clam_patch_coords.csv'
img_output = '/data2/ranxiangyu/patch_test/clam_patch_coords_visualization.png'
patch_size = 512           # 默认 patch 大小
draw_rect = False           # <<< 是否绘制矩形（True/False）

# === 读取 h5 中的坐标 ===
with h5py.File(h5_path, 'r') as f:
    coords = f['coords'][:]

# === 保存为 CSV 文件 ===
df = pd.DataFrame(coords, columns=['x', 'y'])
df.to_csv(csv_output, index=False)
print(f"坐标数据已保存为 {csv_output}")

# === 自动估计 patch 边长 z ===
coords_sorted = coords[np.lexsort((coords[:, 1], coords[:, 0]))]

z_values = []
for i in range(len(coords_sorted) - 1):
    x1, y1 = coords_sorted[i]
    x2, y2 = coords_sorted[i + 1]
    if x1 == x2 and y1 != y2:
        z_values.append(abs(y2 - y1))
    elif y1 == y2 and x1 != x2:
        z_values.append(abs(x2 - x1))

# 使用中位数估计 patch 边长
if len(z_values) == 0:
    z = patch_size
    print("未找到可比较的 patch 相邻坐标，使用默认 z =", z)
else:
    z = int(np.median(z_values))
    print(f"检测到的 patch 边长 z = {z}")

# === 获取画布大小 ===
x_min, y_min = coords[:, 0].min(), coords[:, 1].min()
x_max, y_max = coords[:, 0].max(), coords[:, 1].max()
padding = patch_size
width = x_max - x_min + padding * 2
height = y_max - y_min + padding * 2

# === 创建画布 ===
fig, ax = plt.subplots(figsize=(10, 10))
ax.set_facecolor('white')
plt.title('Patch Grid Visualization')
plt.xlim(x_min - padding, x_max + padding)
plt.ylim(y_min - padding, y_max + padding)
plt.gca().invert_yaxis()
plt.axis('off')

# === 绘制 ===
if draw_rect:
    print("正在绘制 patch 矩形框...")
    for x, y in coords:
        rect = Rectangle((x, y), z, z, edgecolor='red', facecolor='none', linewidth=1)
        ax.add_patch(rect)
else:
    print("仅绘制坐标点（不绘制矩形框）")
    ax.scatter(coords[:, 0], coords[:, 1], s=10, c='blue', alpha=0.6)

# === 保存图像 ===
plt.tight_layout()
plt.savefig(img_output, dpi=300, bbox_inches='tight')
plt.close()
print(f"图像已保存为 {img_output}")
