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
        self.found_yml_files = []  # 存储找到的yml文件列表

    def _resolve_path(self, file_path):
        """
        解析文件路径，支持相对路径和绝对路径
        如果不是绝对路径，判断当前目录是否以AUI结尾，如果是则基于当前工作目录解析
        """
        if os.path.isabs(file_path):
            return file_path

        # 如果是相对路径，检查当前工作目录
        current_dir = os.getcwd()

        # 判断当前目录是否以 AUI 结尾
        if not current_dir.endswith('AUI'):
            raise ValueError(f"当前工作目录必须以 'AUI'（项目根目录） 结尾，当前目录: {current_dir}")

        # 基于当前工作目录解析路径
        resolved_path = os.path.join(current_dir, file_path)
        resolved_path = os.path.normpath(resolved_path)  # 标准化路径

        # 检查路径是否存在
        if not os.path.exists(resolved_path):
            raise FileNotFoundError(f"路径不存在: {resolved_path}")

        return resolved_path

    def _find_yml_files_with_testsuites(self, directory):
        """
        递归遍历目录，查找包含 testsuites 节点的 yml 文件

        Args:
            directory (str): 要搜索的目录路径

        Returns:
            list: 包含 testsuites 的 yml 文件路径列表
        """
        yml_files = []
        if not os.path.isdir(directory):
            return yml_files
        print(f"正在搜索目录: {directory}")
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(('.yml', '.yaml')):
                        file_path = os.path.join(root, file)
                        yml_files.append(file_path)
        except Exception as e:
            print(f"✗ 查找文件失败 {file_path}: {e}")
        return yml_files

    def parse(self, yml_file_path=None):
        """
        解析 YAML 文件或目录并返回有效测试用例

        Args:
            yml_file_path (str, optional): YAML文件路径或目录路径

        Returns:
            list: 有效的测试用例路径列表
        """
        if yml_file_path:
            file_path = self._resolve_path(yml_file_path)
        else:
            file_path = self.yml_file_path

        if not file_path or not os.path.exists(file_path):
            print(f"路径不存在: {file_path}")
            print(f"当前工作目录: {os.getcwd()}")
            return []

        self.testcases = []
        self.found_yml_files = []

        # 判断输入是文件还是目录
        if os.path.isfile(file_path):
            # 处理单个文件
            if file_path.endswith(('.yml', '.yaml')):
                self.found_yml_files = [file_path]
                print(f"解析单个YAML文件: {file_path}")
            else:
                print(f"不是YAML文件: {file_path}")
                return []
        elif os.path.isdir(file_path):
            # 处理目录 - 递归查找包含 testsuites 的 yml 文件
            print(f"解析目录: {file_path}")
            self.found_yml_files = self._find_yml_files_with_testsuites(file_path)

            if not self.found_yml_files:
                print(f"在目录 {file_path} 中未找到包含testsuites/testcases的YAML文件")
                return []
        else:
            print(f"无效的路径类型: {file_path}")
            return []

        # 解析所有找到的 yml 文件
        for yml_file in self.found_yml_files:
            try:
                testcases_from_file = self._parse_single_yml_file(yml_file)
                self.testcases.extend(testcases_from_file)
            except Exception as e:
                print(f"解析文件 {yml_file} 时出错: {e}")

        print(f"总共解析到 {len(self.testcases)} 个测试用例")
        return self.testcases

    def _parse_single_yml_file(self, yml_file_path):
        """
        解析单个 YAML 文件

        Args:
            yml_file_path (str): YAML文件路径

        Returns:
            list: 该文件中的测试用例路径列表
        """
        testcases = []

        try:
            with open(yml_file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                print(f"YAML文件格式错误: {yml_file_path}")
                return testcases

            # 支持 testcases 和 testsuites 两种格式
            test_data = data.get('testcases',  {})

            if not test_data:
                print(f"文件中没有找到testcases或testsuites节点: {yml_file_path}")
                return testcases

            for name, info in test_data.items():
                if isinstance(info, dict) and 'testcase' in info:
                    path = info['testcase']

                    # 解析路径（处理相对路径）
                    try:
                        resolved_path = self._resolve_path(path)
                        testcases.append(path)  # 保存原始路径
                        print(f"  ✓ 加载测试用例: {name} -> {path}")
                    except FileNotFoundError:
                        print(f"  ✗ 跳过不存在的文件: {name} -> {path}")
                    except Exception as e:
                        print(f"  ✗ 解析路径失败: {name} -> {path}, 错误: {e}")
                else:
                    print(f"  ✗ 跳过无效的测试用例配置: {name}")

        except Exception as e:
            print(f"解析文件 {yml_file_path} 时出错: {e}")

        return testcases

    def show(self):
        """显示解析结果"""
        if not self.testcases:
            print("没有找到有效的测试用例")
            return

        print(f"\n=== 解析结果汇总 ===")
        print(f"扫描的YAML文件数: {len(self.found_yml_files)}")
        for yml_file in self.found_yml_files:
            print(f"  - {yml_file}")

        print(f"\n找到 {len(self.testcases)} 个有效测试用例:")
        for i, case in enumerate(self.testcases, 1):
            test_name = os.path.basename(case).replace('.py', '')
            print(f"  {i}. {test_name} -> {case}")

    def get_found_yml_files(self):
        """获取找到的YAML文件列表"""
        return self.found_yml_files

    def get_testcases_count(self):
        """获取测试用例数量"""
        return len(self.testcases)


if __name__ == "__main__":
    print("=== CoreYmlParser 使用示例 ===")

    # 示例1: 解析单个YAML文件
    print("\n1. 解析单个YAML文件:")
    parser1 = CoreYmlParser("Tests/TmapiClient/testsuites/core.yml")
    testcases1 = parser1.parse()
    # parser1.show()
    #
    # # 示例2: 解析目录（递归查找包含testsuites的YAML文件）
    # print("\n2. 解析目录:")
    # parser2 = CoreYmlParser("Tests/TmapiClient")
    # testcases2 = parser2.parse()
    # parser2.show()
    #
    # # 示例3: 解析指定的testsuites目录
    # print("\n3. 解析testsuites目录:")
    # parser3 = CoreYmlParser("Tests/TmapiClient/testsuites")
    # testcases3 = parser3.parse()
    # parser3.show()
    #
    # print(f"\n=== 总结 ===")
    # print(f"单个文件解析结果: {len(testcases1)} 个测试用例")
    # print(f"目录解析结果: {len(testcases2)} 个测试用例")
    # print(f"testsuites目录解析结果: {len(testcases3)} 个测试用例")
