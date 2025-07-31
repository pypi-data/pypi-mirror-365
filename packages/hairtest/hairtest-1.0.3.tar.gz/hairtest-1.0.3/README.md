# Hairtest

Airtest 并行测试工具 - 支持多设备并行执行测试用例

## 特性

- 🚀 **多设备并行执行** - 支持多台Android设备同时运行测试
- 📱 **智能负载均衡** - 自动分配测试任务到可用设备
- 📝 **多种用例格式** - 支持单文件、目录、YAML用例集
- 🔄 **失败重试机制** - 支持断点续跑和失败用例重试
- 📊 **详细测试报告** - 生成JSON格式的测试结果报告
- 🛠️ **简单易用** - 一条命令即可开始测试
## 构建包
```bash
python setup.py sdist bdist_wheel

# 上传到 PyPI 需要apitoken
twine upload dist/*

```

## 开发
```bash
cd hairtest
python cli.py Tests/TmapiClient/testsuites/core.yml
python cli.py Tests/TmapiClient/testsuites/core.yml --devices device1 --mode
```
## 安装地址https://pypi.org/project/hairtest/

```bash

pip install hairtest
# 国内镜像可能没有，指定官网
pip install --index-url https://pypi.org/simple/ hairtest

# 开发模式安装
pip install -e .
```

## 快速开始

### 基本使用

```bash
# 执行单个测试文件
hairtest Tests/TmapiClient/testAICase/ai_test.py

# 执行测试目录（自动扫描所有 *_test.py 文件）
hairtest Tests/TmapiClient/testAICase/

# 执行 YAML 用例集
hairtest Tests/TmapiClient/testsuites/core.yml
```

### 高级使用

```bash
# 指定设备执行
hairtest core.yml --devices MDX0220918025508

# 多设备并行
hairtest core.yml --devices MDX0220918025508 YWT0222A10000129

# 兼容模式（每个设备执行所有用例）
hairtest core.yml --mode

# 失败重试（基于之前的测试数据）
hairtest core.yml --retry-data 1753498757687_data.json

# 组合使用
hairtest core.yml --devices MDX0220918025508 YWT0222A10000129 --mode --retry-data data.json
```

## 参数说明

| 参数 | 简写 | 说明 |
|------|------|------|
| `test_path` | - | 测试用例路径（必需） |
| `--devices` | `-d` | 指定设备列表，多个设备用空格分隔 |
| `--mode` | `-m` | 兼容模式：多台设备并行，单设备脚本串行 |
| `--retry-data` | `-r` | 失败重试：指定已运行的测试数据文件 |
| `--version` | `-v` | 显示版本信息 |
| `--help` | `-h` | 显示帮助信息 |

## 支持的文件类型

### 1. 单个测试文件
文件名必须以 `_test.py` 结尾：
```
ai_login_test.py
hotel_search_test.py
```

### 2. 测试目录
自动扫描目录下所有 `*_test.py` 文件：
```
Tests/
├── login_test.py
├── search_test.py
└── booking_test.py
```

### 3. YAML 用例集
支持自定义测试用例配置：
```yaml
config:
    author: 王彦青
    create_time: '2022-05-25'
testcases:
  登录测试:
      testcase: Tests/TmapiClient/testAICase/ai_login_test.py
  搜索测试:
      testcase: Tests/TmapiClient/testAICase/ai_search_test.py
  预订测试:
      testcase: Tests/TmapiClient/testAICase/ai_booking_test.py
```

## 运行模式

### 负载均衡模式（默认）
测试用例平均分配到各个设备，每个用例只执行一次：
```
设备A: test1.py, test3.py
设备B: test2.py, test4.py
```

### 兼容模式（--mode）
每个设备都执行所有测试用例：
```
设备A: test1.py, test2.py, test3.py, test4.py
设备B: test1.py, test2.py, test3.py, test4.py
```

## 测试报告

执行完成后会在 `reports/` 目录生成：
- `{timestamp}_data.json` - 详细的测试结果数据
- `{timestamp}_logs/` - 各设备的测试日志

## 开发

```bash
# 克隆项目
git clone https://github.com/yourusername/hairtest.git
![img_1.png](img_1.png)cd hairtest

# 开发模式安装
pip install -e .
# 运行测试
hairtest Tests/TmapiClient/testsuites/core.yml
```

## 依赖

- Python >= 3.7
- airtest >= 1.3.0
- gevent
- pyyaml
- jinja2
- requests

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0
- 初始版本发布
- 支持多设备并行测试
- 支持多种用例格式
- 支持失败重试机制
