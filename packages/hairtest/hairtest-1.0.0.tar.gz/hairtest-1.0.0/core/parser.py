#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    :  2025/7/28 16:37
@Author  :  王彦青
@File    :  parser.py
"""
"""
YAML 用例集解析器
与 utils/CoreYmlParser.py 保持完全一致的实现
"""
import os
import yaml


class CoreYmlParser:
    """Core.yml 文件解析器 - 与 utils/CoreYmlParser.py 完全一致"""

    def __init__(self, yml_file_path=None):
        self.yml_file_path = self._resolve_path(yml_file_path) if yml_file_path else None
        self.testcases = []

    def _resolve_path(self, file_path):
        """
        解析文件路径，支持相对路径和绝对路径
        与 utils/CoreYmlParser.py 保持完全一致的路径解析逻辑
        """
        if os.path.isabs(file_path):
            return file_path

        # 如果是相对路径，基于项目根目录解析
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 从 hairtest/core 目录回到项目根目录
        # 检查是否在 hairtest 子目录中
        if 'hairtest' in script_dir:
            # 从 hairtest/core 向上两级到项目根目录
            project_root = os.path.dirname(os.path.dirname(script_dir))
        else:
            # 从 utils 目录向上一级到项目根目录
            project_root = os.path.dirname(script_dir)
        resolved_path = os.path.join(project_root, file_path)
        return os.path.normpath(resolved_path)  # 标准化路径

    def parse(self, yml_file_path=None):
        """
        解析 YAML 文件并返回有效测试用例
        与 utils/CoreYmlParser.py 保持完全一致的实现
        """
        if yml_file_path:
            file_path = self._resolve_path(yml_file_path)
        else:
            file_path = self.yml_file_path

        if not file_path or not os.path.exists(file_path):
            print(f"用例集yml文件不存在: {file_path}")
            print(f"当前工作目录: {os.getcwd()}")
            return []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            self.testcases = []
            for name, info in data.get('testcases', {}).items():
                if isinstance(info, dict) and 'testcase' in info:
                    path = info['testcase']
                    # 解析路径（处理相对路径）
                    resolved_path = self._resolve_path(path)
                    if os.path.exists(resolved_path):
                        # self.testcases.append({name: path})  # 保存原始路径
                        self.testcases.append(path)  # 保存原始路径
                    else:
                        print(f"跳过不存在的文件: {name} -> {path} (解析后: {resolved_path})")

            return self.testcases
        except Exception as e:
            print(f"解析错误: {e}")
            return []

    def show(self):
        """显示解析结果"""
        if not self.testcases:
            print("没有找到有效的测试用例")
            return

        print(f"找到 {len(self.testcases)} 个有效测试用例:")
        # for i, case in enumerate(self.testcases, 1):
        #     for name, path in case.items():
        #         print(f"{i}. {name} -> {path}")


if __name__ == "__main__":
    print("=== 相对路径使用示例 ===")

    # 方式1: 使用相对路径（推荐）
    parser = CoreYmlParser("Tests/TmapiClient/testsuites/core.yaml")
    testcases = parser.parse()
    print(testcases)
    # parser.show()
    #
    # print("\n=== 路径解析调试信息 ===")
    # print(f"当前工作目录: {os.getcwd()}")
    #
    # # 演示路径解析过程
    # relative_path = "Tests/TmapiClient/testsuites/core.yml"
    # resolved_path = parser._resolve_path(relative_path)
    # print(f"相对路径: {relative_path}")
    # print(f"解析后路径: {resolved_path}")
    # print(f"文件是否存在: {os.path.exists(resolved_path)}")
    #
