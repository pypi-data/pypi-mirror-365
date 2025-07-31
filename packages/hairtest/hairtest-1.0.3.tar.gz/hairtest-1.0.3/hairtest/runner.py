#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    :  2025/7/28 16:37
@Author  :  王彦青
@File    :  runner.py
"""
"""
Hairtest 核心运行器
与 main_run.py 保持完全一致的实现逻辑
"""
# 关键补丁 - 必须在其他导入之前
from gevent import monkey; monkey.patch_all(select=False)

import os
import traceback
import subprocess
import webbrowser
import time
import json
import shutil
import requests
import sys
from gevent.pool import Pool
from jinja2 import Environment, FileSystemLoader

# 处理导入问题
try:
    from .parser import CoreYmlParser
except ImportError:
    # 直接运行时的导入方式
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from parser import CoreYmlParser

try:
    from airtest.core.android.adb import ADB
except ImportError:
    ADB = None

# 默认初始化目录配置，根目录文件夹下 reports 文件夹生成，如果不存在则创建该文件夹
testReport_path = "reports/"


def init_reports_directory():
    """初始化reports目录"""
    print("🔧 初始化报告目录...")
    try:
        # 创建目录（如果不存在）
        if not os.path.exists(testReport_path):
            os.makedirs(testReport_path)
            print(f"✅ 成功创建目录: {testReport_path}")
        else:
            print(f"📁 目录已存在: {testReport_path}")

        # 下载模板文件
        _template_url = "http://10.152.25.230/tools/aiTools/report_tpl.html"
        _template_filename = "report_tpl.html"
        template_path = os.path.join(testReport_path, _template_filename)

        if not os.path.exists(template_path):
            print(f"📥 正在下载报告模板文件...")
            print(f"   URL: {_template_url}")

            response = requests.get(_template_url, timeout=30)
            response.raise_for_status()  # 检查请求是否成功

            with open(template_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ 成功下载模板文件到: {template_path}")
        else:
            print(f"📄 模板文件已存在: {template_path}")

        print("✅ 报告目录初始化完成")

    except requests.exceptions.RequestException as e:
        print(f"⚠️  模板文件下载失败: {str(e)}")
        print("   将使用默认模板继续执行...")
    except Exception as e:
        print(f"❌ 初始化过程中出现错误: {str(e)}")
        raise


# 获取指定目录的被测文件列表，以"xx"（test_）前缀为准，xx结尾的文件为测试用例，未考虑重名文件
def find_test_files(root_dir):
    """
    识别测试文件，自动处理文件和目录两种输入

    Args:
        root_dir (str): 文件路径或目录路径

    Returns:
        list: 测试文件路径列表
              - 如果输入是_test.py文件，返回该文件路径
              - 如果输入是.yml文件，返回解析出的测试文件列表
              - 如果输入是目录，返回目录下所有_test.py文件路径
              - 其他情况返回空列表
    """
    print(f"🔍 正在扫描测试文件: {root_dir}")

    # # 处理相对路径 - 如果在 hairtest 目录中运行，需要调整路径
    # original_path = root_dir
    # if not os.path.isabs(root_dir):
    #     # 检查当前工作目录是否在 hairtest 中
    #     current_dir = os.getcwd()
    #     if 'hairtest' in current_dir:
    #         # 从 hairtest 目录向上一级到项目根目录
    #         project_root = os.path.dirname(current_dir)
    #         root_dir = os.path.join(project_root, root_dir)
    #         print(f"📂 路径调整: {original_path} -> {root_dir}")

    if os.path.isfile(root_dir):
        # 处理单个文件情况
        if root_dir.endswith('_test.py'):
            print(f"📄 发现单个测试文件: {os.path.basename(root_dir)}")
            return [root_dir]
        # 处理yml用例集文件情况
        elif root_dir.endswith('.yml') or root_dir.endswith('.yaml'):
            print(f"📋 解析YAML用例集文件: {os.path.basename(root_dir)}")
            try:
                parser = CoreYmlParser(root_dir)
                test_files = parser.parse()
                print(f"✅ YAML解析成功，找到 {len(test_files)} 个测试文件")
                for i, file in enumerate(test_files, 1):
                    print(f"   {i}. {os.path.basename(file)}")
                return test_files
            except Exception as e:
                print(f"❌ YAML解析失败: {str(e)}")
                return []
        else:
            print(f"⚠️  不支持的文件类型: {os.path.basename(root_dir)}")
            return []
    elif os.path.isdir(root_dir):
        # 处理目录情况
        print(f"📁 扫描目录中的测试文件...")
        result = []
        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith('_test.py'):
                    file_path = os.path.join(root, file)
                    result.append(file_path)
                    print(f"   ✓ {os.path.relpath(file_path, root_dir)}")

        if result:
            print(f"✅ 目录扫描完成，共找到 {len(result)} 个测试文件")
        else:
            print("⚠️  目录中未找到任何 *_test.py 文件")
        return result
    else:
        print(f"❌ 路径不存在: {root_dir}")
        return []


# 动态负载均衡设备执行脚本
def map_tasks(devices, air, mode=False):
    """
    Args:
        devices:    可使用设备列表，动态获取
        test_files: 获取指定目录的被测文件列表
        mode:   模式 0默认负载均衡，1手动设置为兼容模型
    Returns:
       动态负载均衡均分并行执行
    """
    print("📋 开始任务分配...")
    test_files = find_test_files(air)

    if not test_files:
        print("❌ 未找到任何测试文件，无法分配任务")
        raise Exception("❌ 未找到任何测试文件，无法分配任务")
        # return {}

    result = {}
    len_devices = len(devices)
    len_test_files = len(test_files)

    print(f"📊 任务分配统计:")
    print(f"   设备数量: {len_devices}")
    print(f"   测试文件数量: {len_test_files}")
    print(f"   分配模式: {'兼容模式' if mode else '负载均衡模式'}")

    # 兼容模式
    if mode:
        print("🔄 兼容模式: 每台设备执行所有测试文件")
        for device in devices:
            result[device] = [
                {"py_path": file_path, "log_path": f"{device}_{os.path.basename(file_path)}"}
                for file_path in test_files
            ]
            print(f"   📱 {device}: {len(test_files)} 个任务")

    # 负载均衡模式
    else:
        print("⚖️  负载均衡模式: 测试文件均分到各设备")
        # 计算每个设备应该分配多少个测试文件
        base = len_test_files // len_devices
        remainder = len_test_files % len_devices

        print(f"   基础分配: 每台设备 {base} 个文件")
        if remainder > 0:
            print(f"   额外分配: 前 {remainder} 台设备各多分配 1 个文件")

        start = 0
        for i, device in enumerate(devices):
            # 计算当前 device 应分配的用例数量
            count = base + (1 if i < remainder else 0)
            # 生成对应的字典结构
            result[device] = [
                {"py_path": file_path, "log_path": f"{device}_{os.path.basename(file_path)}"}
                for file_path in test_files[start:start + count]
            ]

            print(f"   📱 {device}: {count} 个任务")
            for j, task in enumerate(result[device]):
                print(f"      {j+1}. {os.path.basename(task['py_path'])}")

            start += count

    total_tasks = sum(len(tasks) for tasks in result.values())
    print(f"✅ 任务分配完成，总计 {total_tasks} 个执行任务")
    return result


# 并发执行Airtest测试脚本
def execute_concurrent_airtest_run(devices_tasks):
    """
    并发执行Airtest测试脚本
    参数:
        devices_tasks (dict):
            - 必须包含设备ID作为键
            - 每个设备ID对应一个测试脚本配置列表
            - 每个配置需包含:
                 py_path: 测试脚本路径
                 log_path: 日志保存路径
                 airtest_run_cmd: 完整的airtest命令行参数列表
    返回:
        dict: 修改后的测试数据字典，每个测试配置会新增:
            - status: 子进程执行状态码（0表示成功）
    """
    print("🚀 开始并发执行测试脚本...")

    total_tasks = sum(len(tasks) for tasks in devices_tasks.values())
    print(f"📊 执行统计: {len(devices_tasks)} 台设备，共 {total_tasks} 个任务")

    def airtest_run_cme(device):
        device_tasks = devices_tasks[device]
        print(f"📱 设备 {device} 开始执行 {len(device_tasks)} 个任务")

        for i, device_info in enumerate(device_tasks, 1):
            cmd = device_info.get("airtest_run_cmd", None)
            if cmd:
                test_name = os.path.basename(device_info["py_path"])
                print(f"   🏃 [{i}/{len(device_tasks)}] 执行: {test_name}")
                print(f"   📝 命令: {' '.join(cmd)}")

                device_info["start_time"] = time.time()
                start_time_str = time.strftime("%H:%M:%S", time.localtime(device_info["start_time"]))
                print(f"   ⏰ 开始时间: {start_time_str}")

                try:
                    status = subprocess.call(cmd, shell=False, cwd=os.getcwd())
                    device_info["status"] = status
                    device_info["end_time"] = time.time()
                    device_info["spend_time"] = device_info["end_time"] - device_info["start_time"]

                    end_time_str = time.strftime("%H:%M:%S", time.localtime(device_info["end_time"]))
                    spend_time_str = f"{device_info['spend_time']:.2f}秒"

                    if status == 0:
                        print(f"   ✅ 执行成功: {test_name} (耗时: {spend_time_str})")
                    else:
                        print(f"   ❌ 执行失败: {test_name} (状态码: {status}, 耗时: {spend_time_str})")

                except Exception as e:
                    print(f"   💥 执行异常: {test_name} - {str(e)}")
                    device_info["status"] = -1
                    device_info["end_time"] = time.time()
                    device_info["spend_time"] = device_info["end_time"] - device_info["start_time"]

        print(f"📱 设备 {device} 所有任务执行完成")

    print("🔄 启动并发执行池...")
    producer_tasks = []
    producer_pool = Pool(size=len(devices_tasks))

    for device in devices_tasks:
        producer_tasks.append(producer_pool.spawn(airtest_run_cme, device))

    print("⏳ 等待所有设备任务完成...")
    producer_pool.join()

    # 统计执行结果
    success_count = 0
    fail_count = 0
    total_time = 0

    for device, tasks in devices_tasks.items():
        for task in tasks:
            if task.get("status") == 0:
                success_count += 1
            else:
                fail_count += 1
            if "spend_time" in task:
                total_time += task["spend_time"]

    print("📊 执行结果统计:")
    print(f"   ✅ 成功: {success_count} 个")
    print(f"   ❌ 失败: {fail_count} 个")
    print(f"   ⏱️  总耗时: {total_time:.2f} 秒")
    print("🏁 并发执行完成")

    return devices_tasks


def run(devices, air, report_start, mode=False, run_all=False):
    """"
        mode
            = True: 兼容模式，多台设备并行，单设备脚本串行，每个脚本只执行设备数据的次数
            = False: 负载均衡模式，多台设备并行，单设备脚本串行，每个脚本只执行1次
        run_all
            = True: 从头开始完整测试 (run test fully) ;
            = False: 续着data.json的进度继续测试 (continue test with the progress in data.jason)
    """
    try:
        print("🔧 初始化测试环境...")
        # 确保reports目录存在
        init_reports_directory()

        logs = f"{testReport_path}{report_start}_logs"
        print(f"📂 日志目录: {logs}")

        print("📄 加载测试数据...")
        results = load_jdon_data(air, logs, report_start, run_all)

        print("🚀 开始多设备测试执行...")
        devices_tasks = run_on_multi_device(devices, air, logs, results, mode, run_all)

        print("📊 处理测试结果...")
        report_count = 0
        for device in devices_tasks:
            for task in devices_tasks[device]:
                status = task.get("status", "no value")
                if status != "no value":
                    test_name = os.path.basename(task['py_path'])
                    print(f"   📝 生成报告: {test_name}")

                    airtest_one_report = run_one_report(task['py_path'], logs, task['log_path'])
                    airtest_one_report["airtest_run_cmd"] = task["airtest_run_cmd"]
                    airtest_one_report["spend_time"] = task["spend_time"]
                    results['tests'][task['log_path']] = airtest_one_report
                    results['tests'][task['log_path']]['status'] = status
                    report_count += 1

        print(f"✅ 已生成 {report_count} 个测试报告")

        # 计算总耗时
        results['end'] = time.time()
        results['spend_time'] = results['end'] - results['start']

        # 保存测试数据
        data_file = f'{testReport_path}{report_start}_data.json'
        print(f"💾 保存测试数据: {data_file}")
        json.dump(results, open(data_file, "w"), indent=4)

        # 生成汇总报告
        print("📋 生成汇总报告...")
        run_summary(results, report_start)

        print("🎉 测试执行完成！")
        return results

    except Exception as e:
        print(f"💥 测试执行过程中发生错误: {str(e)}")
        traceback.print_exc()
        return None



def run_on_multi_device(devices, air, logs, results, mode, run_all):
    """
    在多台设备上运行airtest脚本 - 与 main_run.py 完全一致
    Run airtest on multi-device
    """
    print("🔧 准备多设备执行环境...")
    devices_tasks = map_tasks(devices, air, mode)

    if not devices_tasks:
        print("❌ 任务分配失败，无法继续执行")
        raise Exception("❌ 任务分配失败，无法继续执行")
        # return {}

    airtest_run_num = 0
    skip_count = 0

    print("🔍 检查任务执行状态...")
    for device in devices_tasks:
        print(f"📱 处理设备 {device} 的任务:")
        for device_tasks in devices_tasks[device]:
            dev = device_tasks["log_path"]
            test_name = os.path.basename(device_tasks["py_path"])

            # 检查是否需要跳过已成功的任务
            if (not run_all and results['tests'].get(dev) and results['tests'].get(dev).get('status') == 0):
                print(f"   ⏭️  跳过已成功的任务: {test_name}")
                skip_count += 1
                continue
            else:
                log_dir = get_log_dir(dev, logs)
                airtest_run_cmd = [
                    "airtest",
                    "run",
                    device_tasks["py_path"],
                    "--device",
                    "Android:///" + device,
                    "--log",
                    log_dir
                ]
                device_tasks["airtest_run_cmd"] = airtest_run_cmd
                airtest_run_num += 1
                print(f"   ✅ 准备执行: {test_name}")
                print(f"      📂 日志目录: {log_dir}")

    print(f"📊 任务准备完成:")
    print(f"   🆕 待执行任务: {airtest_run_num} 个")
    print(f"   ⏭️  跳过任务: {skip_count} 个")

    if airtest_run_num == 0:
        print("ℹ️  所有任务都已完成，无需重新执行")
        return devices_tasks

    print("🚀 开始多设备并行执行...")
    # 多设备并行执行 airtest_run_cmd
    devices_tasks = execute_concurrent_airtest_run(devices_tasks)
    return devices_tasks


def run_one_report(air, logs, dev):
    """"
        生成一个脚本的测试报告
        Build one test report for one air script
    """
    try:
        log_dir = get_log_dir(dev, logs)
        log = os.path.join(log_dir, 'log.txt')
        if os.path.isfile(log):
            airtest_report_cmd = [
                "airtest",
                "report",
                air,
                "--log_root",
                log_dir,
                "--outfile",
                os.path.join(log_dir, 'log.html'),
                "--lang",
                "zh"
            ]
            ret = subprocess.call(airtest_report_cmd, shell=False, cwd=os.getcwd())
            return {
                    'airtest_report_cmd': airtest_report_cmd,
                    'status': ret,
                    'path': os.path.relpath(os.path.normpath(os.path.join(log_dir, 'log.html')), start='reports'),
                    'path_time': time.time(),
            }
        else:
            print("Report build Failed. File not found in dir %s" % log)
    except Exception as e:
        traceback.print_exc()
    return {'status': -1, 'device': dev, 'path': '', 'path_time': time.time(), 'airtest_report_cmd': ''}


def run_summary(data, report_start):
    """"
        生成汇总的测试报告
        Build sumary test report
    """
    print("📋 生成汇总测试报告...")
    try:
        # 计算统计数据
        total_count = len(data['tests'])
        success_count = [item['status'] for item in data['tests'].values()].count(0)
        fail_count = total_count - success_count
        total_time = time.time() - data['start']

        print(f"📊 测试结果统计:")
        print(f"   总测试数: {total_count}")
        print(f"   成功数: {success_count}")
        print(f"   失败数: {fail_count}")
        print(f"   成功率: {(success_count/total_count*100):.1f}%" if total_count > 0 else "   成功率: 0%")
        print(f"   总耗时: {total_time:.3f} 秒")

        summary = {
            'time': "%.3f" % total_time,
            'success': success_count,
            'count': total_count,
            "start": data['start'],
        }
        summary.update(data)

        print("🎨 渲染HTML报告...")
        env = Environment(loader=FileSystemLoader(testReport_path), trim_blocks=True)
        html = env.get_template('report_tpl.html').render(data=summary)

        report_html = f"{testReport_path}{report_start}_report.html"
        with open(report_html, "w", encoding="utf-8") as f:
            f.write(html)

        report_path = os.path.abspath(report_html)
        print(f"✅ 汇总报告已生成: {report_path}")

        print("🌐 正在打开浏览器查看报告...")
        webbrowser.open(report_path)

    except Exception as e:
        print(f"❌ 生成汇总报告失败: {str(e)}")
        traceback.print_exc()


def load_jdon_data(air, logs, report_start, run_all):
    """"
        加载进度
            如果data.json存在且run_all=False，加载进度
            否则，返回一个空的进度数据
        Loading data
            if data.json exists and run_all=False, loading progress in data.json
            else return an empty data
    """
    json_file = os.path.join(os.getcwd(), f'{testReport_path}{report_start}_data.json')
    if (not run_all) and os.path.isfile(json_file):
        data = json.load(open(json_file))
        data['start'] = time.time()
        return data
    else:
        clear_log_dir(logs)
        return {
            'start': time.time(),
            'script': air,
            'tests': {},
            'data_json': f'{report_start}_data.json',
            'report_html': f'{report_start}_report.html'
        }


def clear_log_dir(logs):
    """"
        清理log文件夹 test_blackjack.air/log
        Remove folder test_blackjack.air/log
    """
    log_path = os.path.join(os.getcwd(), logs)
    if os.path.exists(log_path):
        shutil.rmtree(log_path)
    os.makedirs(log_path, exist_ok=True)


def get_log_dir(device, logs):
    """"
        在 test_blackjack.air/log/ 文件夹下创建每台设备的运行日志文件夹
        Create log folder based on device name under test_blackjack.air/log/
    """
    log_dir = os.path.join(logs, device.replace(".", "_").replace(':', '_'))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_dir


def run_all_route_test_case(air, devices=None, mode=False, report_start_data=None):
    """
        air
            传入用例目录，扫描目录中的 _test.py 命名结尾的文件
            传入用例文件，需以 _test.py 命名结尾的用例
        devices
            传入可用设备列表 ['66J5T19730001281', 'YWT0222A10000129']，adb指定设备运行
            不传入，默认获取已连接设备
        modedevices_tasks = run_all_route_test_case(air, mode=False)
            = True: 兼容模式，多台设备并行，单设备脚本串行，每个脚本只执行设备数据的次数
            = False: 负载均衡模式，多台设备并行，单设备脚本串行，每个脚本只执行1次
        report_start_data
            传入断点续跑 或 重试失败的用例，传入 1753085644830_data.json 记录用例执行报告的数据
    """
    print("=" * 60)
    print("🚀 开始执行 Hairtest 测试任务")
    print("=" * 60)

    # 参数验证
    if air is None:
        print("❌ 错误: 测试路径参数为空")
        return False

    print(f"📁 测试路径: {air}")

    # 设备处理
    if devices is None:
        print("🔍 未指定设备，正在自动获取已连接的设备...")
        try:
            devices = [tmp[0] for tmp in ADB().devices()]
            if not devices:
                raise Exception("❌ 错误: 未找到任何已连接的设备")
            print(f"✅ 自动获取到 {len(devices)} 台设备: {devices}")
        except Exception as e:
            raise Exception(f"❌ 获取设备失败: {str(e)}")
    else:
        print(f"📱 使用指定设备 ({len(devices)} 台): {devices}")

    # 运行模式
    mode_text = "兼容模式 (多设备并行，单设备串行)" if mode else "负载均衡模式 (任务均分到设备)"
    print(f"⚙️  运行模式: {mode_text}")

    # 报告配置
    if report_start_data is None:
        report_start = int(time.time() * 1000)
        run_all = True
        print(f"🆕 新测试任务，报告ID: {report_start}")
    else:
        report_start = report_start_data.split("_")[0]
        run_all = False
        print(f"🔄 续跑模式，使用已有报告ID: {report_start}")
        print(f"📄 数据文件: {report_start_data}")

    print("-" * 60)
    print("🏃 开始执行测试...")

    devices_tasks = run(devices, air, report_start, mode=mode, run_all=run_all)

    print("-" * 60)
    print("✅ 测试任务执行完成")
    print("=" * 60)

    return devices_tasks





