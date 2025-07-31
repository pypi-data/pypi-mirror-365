#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Hairtest 命令行入口
与 main_run.py 保持一致的参数解析和执行逻辑
"""
import argparse
import sys
import os
import traceback

# 添加当前目录到 Python 路径，支持直接运行
if __name__ == '__main__':
    # 直接运行时使用绝对导入
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from runner import run_all_route_test_case, init_reports_directory
else:
    # 作为包导入时使用相对导入
    from .runner import run_all_route_test_case, init_reports_directory


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='Hairtest - Airtest 并行测试执行器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  hairtest Tests/TmapiClient/testsuites/core.yml
  hairtest Tests/TmapiClient/testAICase/ai_test.py
  hairtest Tests/TmapiClient/testAICase/
  hairtest Tests/TmapiClient/testsuites/core.yml --devices MDX0220918025508
  hairtest Tests/TmapiClient/testsuites/core.yml --mode --retry-data 1753498757687_data.json
        '''
    )

    parser.add_argument('test_path',
                       help='测试用例路径（支持单文件、目录、YAML用例集）')

    parser.add_argument('--devices', '-d',
                       nargs='+',
                       help='指定设备列表，多个设备用空格分隔')

    parser.add_argument('--mode', '-m',
                       action='store_true',
                       help='兼容模式：多台设备并行，单设备脚本串行')

    parser.add_argument('--retry-data', '-r',
                       help='失败重试：指定已运行的测试数据文件（如：1753498757687_data.json）')

    return parser


def parse_args():
    """解析命令行参数 - 与 main_run.py 保持一致"""
    parser = create_parser()
    return parser.parse_args()


def main():
    """主函数 - 支持命令行参数和兼容模式"""
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 命令行模式
        args = parse_args()
        print("=== 命令行模式 ===")
        print(f"测试路径: {args.test_path}")
        print(f"指定设备: {args.devices if args.devices else '自动获取'}")
        print(f"运行模式: {'兼容模式' if args.mode else '负载均衡模式'}")
        print(f"重试数据: {args.retry_data if args.retry_data else '无'}")
        print("-" * 50)

        # 执行测试
        devices_tasks = run_all_route_test_case(
            air=args.test_path,
            devices=args.devices,
            mode=args.mode,
            report_start_data=args.retry_data
        )
        print(f"测试执行完成，共处理 {len(devices_tasks) if devices_tasks else 0} 个任务")
    else:
        # 没有提供命令行参数，显示错误信息和帮助
        print("错误: 缺少必需的测试路径参数", file=sys.stderr)
        print("请使用 'hairtest -h' 查看使用帮助", file=sys.stderr)
        print()
        # 显示帮助信息
        parser = create_parser()
        parser.print_help()
        sys.exit(1)  # 以错误状态退出

if __name__ == '__main__':
    main()
