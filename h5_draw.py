import matplotlib.pyplot as plt
"""
这个文件用来对切好的坐标点进行可视化
"""
points = [
    (160,20778), (160,20906), (160,21034), (160,21162), (160,21290), (160,21418), (160,21546), (160,21674), (160,21802), (160,21930),
    (160,22058), (160,22186), (160,22314), (160,22442),
    (288,20650), (288,20778), (288,20906), (288,21034), (288,21162), (288,21290), (288,21418), (288,21546), (288,21674), (288,21802),
    (288,21930), (288,22058), (288,22186), (288,22314), (288,22442),
    (416,20650), (416,20778), (416,20906), (416,21034), (416,21162)
]

x_coords = [p[0] for p in points]
y_coords = [p[1] for p in points]

padding = 200
x_min, x_max = min(x_coords), max(x_coords)
y_min, y_max = min(y_coords), max(y_coords)

plt.figure(figsize=(12, 10))
plt.scatter(x_coords, y_coords, c='red', s=30, label='Patch Points')

plt.xlim(x_min - padding, x_max + padding)
plt.ylim(y_min - padding, y_max + padding)
plt.gca().invert_yaxis()  # 图像坐标系y轴倒置
plt.axis('equal')
plt.grid(True, linestyle='--', alpha=0.5)
plt.xlabel('X coordinate (pixels)')
plt.ylabel('Y coordinate (pixels)')
plt.title('Patch Coordinates with Distance Annotations')

# 先按坐标排序，方便找相邻点
points_sorted = sorted(points, key=lambda p: (p[0], p[1]))

# 标注竖直方向相邻距离（x相同，y相邻）
for i in range(len(points_sorted)-1):
    x1, y1 = points_sorted[i]
    x2, y2 = points_sorted[i+1]
    if x1 == x2:
        dist = y2 - y1
        # 画双向箭头表示距离
        plt.annotate(
            '',
            xy=(x1, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle='<->', color='blue', lw=1.5)
        )
        # 文字标注在中点左边
        plt.text(x1 - 50, (y1 + y2) / 2, f'{dist}', color='blue', fontsize=8, va='center', ha='right')

# 标注水平方向相邻距离（y相同，x相邻）
# 先按y排序然后x排序方便寻找横向相邻点
points_sorted_x = sorted(points, key=lambda p: (p[1], p[0]))
for i in range(len(points_sorted_x)-1):
    x1, y1 = points_sorted_x[i]
    x2, y2 = points_sorted_x[i+1]
    if y1 == y2:
        dist = x2 - x1
        # 画双向箭头表示距离
        plt.annotate(
            '',
            xy=(x2, y1), xytext=(x1, y1),
            arrowprops=dict(arrowstyle='<->', color='green', lw=1.5)
        )
        # 文字标注在中点下方
        plt.text((x1 + x2)/2, y1 + 40, f'{dist}', color='green', fontsize=8, ha='center', va='bottom')

plt.legend(loc='upper right')
plt.show()


# plt.show()
plt.savefig('patches.png')
