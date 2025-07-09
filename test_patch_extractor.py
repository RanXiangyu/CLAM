import os
import sys
import shutil
import argparse
from create_patches_fp import WSIPatchExtractor

"""
python test_patch_extractor.py \
  --source /data2/ranxiangyu/kidney_wsi \
  --save_dir /data2/ranxiangyu/patch_test \
  --patch_size 512 \
  --patch_level 1 \
  --num_files 2
"""

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='测试WSIPatchExtractor功能')
    parser.add_argument('--source', type=str, required=True,
                        help='WSI文件源目录')
    parser.add_argument('--save_dir', type=str, required=True,
                        help='保存目录')
    parser.add_argument('--patch_size', type=int, default=256,
                        help='切片大小')
    parser.add_argument('--step_size', type=int, default=256,
                        help='步长大小')
    parser.add_argument('--patch_level', type=int, default=0,
                        help='切片层级')
    parser.add_argument('--no_seg', action='store_true', default=False,
                        help='不进行组织分割')
    parser.add_argument('--no_patch', action='store_true', default=False,
                        help='不进行切片')
    parser.add_argument('--no_stitch', action='store_true', default=False,
                        help='不进行拼接')
    parser.add_argument('--no_auto_skip', action='store_true', default=False,
                        help='不自动跳过已处理文件')
    parser.add_argument('--num_files', type=int, default=None,
                        help='要处理的文件数量')
    parser.add_argument('--preset', type=str, choices=['kidney', 'liver', 'default'], default='default',
                        help='使用预设的分割参数')
    
    return parser.parse_args()

def get_preset_params(preset_name):
    """获取预设参数"""
    presets = {
        'kidney': {
            'seg_params': {
                'seg_level': -1,
                'sthresh': 10,  # 肾脏组织分割阈值增加
                'mthresh': 7,
                'close': 4,
                'use_otsu': False,
                'keep_ids': 'none',
                'exclude_ids': 'none'
            },
            'filter_params': {
                'a_t': 100,
                'a_h': 16,
                'max_n_holes': 8
            }
        },
        'liver': {
            'seg_params': {
                'seg_level': -1,
                'sthresh': 6,  # 肝脏组织可能需要更低的阈值
                'mthresh': 7,
                'close': 4,
                'use_otsu': True,  # 使用Otsu方法可能更适合肝脏
                'keep_ids': 'none',
                'exclude_ids': 'none'
            },
            'filter_params': {
                'a_t': 100,
                'a_h': 16,
                'max_n_holes': 10  # 肝脏可能有更多的空洞
            }
        },
        'default': {
            'seg_params': None,
            'filter_params': None
        }
    }
    
    return presets.get(preset_name, presets['default'])

def test_single_slide(extractor, source_dir, slide_file, save_dir, args, preset_params):
    """测试单个WSI文件处理"""
    print(f"\n测试处理单个文件: {slide_file}")
    
    # 创建临时保存目录
    temp_save_dir = os.path.join(save_dir, 'single_test')
    os.makedirs(temp_save_dir, exist_ok=True)
    
    # 处理单个文件
    source_path = os.path.join(source_dir, slide_file)
    
    # 创建一个包含单个文件的目录
    single_source_dir = os.path.join(save_dir, 'single_source')
    os.makedirs(single_source_dir, exist_ok=True)
    shutil.copy(source_path, os.path.join(single_source_dir, slide_file))
    
    # 运行处理
    seg_time, patch_time = extractor.process(
        source=single_source_dir,
        save_dir=temp_save_dir,
        patch_size=args.patch_size,
        step_size=args.step_size,
        patch_level=args.patch_level,
        seg=not args.no_seg,
        patch=not args.no_patch,
        stitch=not args.no_stitch,
        auto_skip=not args.no_auto_skip,
        num_files=1,
        custom_seg_params=preset_params.get('seg_params'),
        custom_filter_params=preset_params.get('filter_params')
    )
    
    # 检查结果
    slide_id, _ = os.path.splitext(slide_file)
    
    success = True
    result_files = {
        'mask': os.path.join(temp_save_dir, 'masks', f"{slide_id}.jpg"),
        'patch': os.path.join(temp_save_dir, 'patches', f"{slide_id}.h5"),
        'stitch': os.path.join(temp_save_dir, 'stitches', f"{slide_id}.jpg")
    }
    
    for file_type, file_path in result_files.items():
        if os.path.exists(file_path):
            print(f"✓ {file_type}文件生成成功: {file_path}")
        else:
            if (file_type == 'mask' and not args.no_seg) or \
               (file_type == 'patch' and not args.no_patch) or \
               (file_type == 'stitch' and not args.no_stitch):
                print(f"✗ {file_type}文件生成失败: {file_path}")
                success = False
    
    return success

def test_batch_processing(extractor, source_dir, save_dir, args, preset_params):
    """测试批量处理多个WSI文件"""
    print(f"\n测试批量处理: {args.num_files if args.num_files else '所有'}个文件")
    
    # 创建批处理保存目录
    batch_save_dir = os.path.join(save_dir, 'batch_test')
    os.makedirs(batch_save_dir, exist_ok=True)
    
    # 运行批处理
    seg_time, patch_time = extractor.process(
        source=source_dir,
        save_dir=batch_save_dir,
        patch_size=args.patch_size,
        step_size=args.step_size,
        patch_level=args.patch_level,
        seg=not args.no_seg,
        patch=not args.no_patch,
        stitch=not args.no_stitch,
        auto_skip=not args.no_auto_skip,
        num_files=args.num_files,
        custom_seg_params=preset_params.get('seg_params'),
        custom_filter_params=preset_params.get('filter_params')
    )
    
    # 验证结果
    csv_file = os.path.join(batch_save_dir, 'process_list_autogen.csv')
    if os.path.exists(csv_file):
        print(f"✓ 批处理CSV文件生成成功: {csv_file}")
        print(f"✓ 平均分割时间: {seg_time:.2f}秒")
        print(f"✓ 平均切片时间: {patch_time:.2f}秒")
        return True
    else:
        print(f"✗ 批处理CSV文件生成失败")
        return False

def main():
    """主测试函数"""
    args = parse_args()
    
    # 获取预设参数
    preset_params = get_preset_params(args.preset)
    
    # 初始化提取器
    extractor = WSIPatchExtractor()
    
    # 创建测试保存目录
    if not os.path.exists(args.save_dir):
        os.makedirs(args.save_dir)
    
    # 获取源目录中的WSI文件
    slides = [f for f in os.listdir(args.source) 
              if os.path.isfile(os.path.join(args.source, f))]
    
    if not slides:
        print(f"错误: 源目录 {args.source} 中没有找到有效的WSI文件")
        return
    
    print(f"找到 {len(slides)} 个WSI文件")
    
    # 测试单个文件处理
    test_slide = slides[0]  # 使用第一个文件进行测试
    single_success = test_single_slide(
        extractor, args.source, test_slide, args.save_dir, args, preset_params
    )
    
    # 测试批量处理
    batch_success = test_batch_processing(
        extractor, args.source, args.save_dir, args, preset_params
    )
    
    # 输出总结
    print("\n测试结果总结:")
    print(f"单文件处理: {'成功' if single_success else '失败'}")
    print(f"批量处理: {'成功' if batch_success else '失败'}")
    print(f"\n所有结果保存在: {args.save_dir}")

if __name__ == "__main__":
    main()