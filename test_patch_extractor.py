import os
import sys
import shutil
import argparse
from create_patches_fp import WSIPatchExtractor

# 初始化提取器
extractor = WSIPatchExtractor()

seg_times, patch_times = extractor.process(
    source="/data2/ranxiangyu/kidney_wsi",  # WSI文件所在目录
    save_dir="/data2/ranxiangyu/patch_test",  # 结果保存目录
    patch_size=512,  # 切片大小
    step_size=128,  # 步长
    patch_level=0,  # 切片层级
    seg=True,  # 是否进行组织分割
    patch=True,  # 是否生成切片
    stitch=True,  # 是否生成拼接图
    save_mask=True,  # 是否保存掩码
    num_files=1  # 处理的文件数量，None表示处理所有
)