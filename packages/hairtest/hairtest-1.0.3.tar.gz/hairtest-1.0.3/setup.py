#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Hairtest 包安装配置
"""
from setuptools import setup, find_packages
import os

# 读取版本信息
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return "1.0.0"

# 读取README
def get_long_description():
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "Hairtest - Airtest 并行测试工具"

setup(
    name="hairtest",
    version=get_version(),
    author="王彦青",
    author_email="your.email@example.com",
    description="Airtest 并行测试工具",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/hairtest",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "airtest>=1.3.0",
        "gevent",
        "pyyaml",
        "jinja2",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "hairtest=hairtest.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="airtest automation testing parallel mobile",
    # project_urls={
    #     "Bug Reports": "https://github.com/yourusername/hairtest/issues",
    #     "Source": "https://github.com/yourusername/hairtest",
    # },
)
