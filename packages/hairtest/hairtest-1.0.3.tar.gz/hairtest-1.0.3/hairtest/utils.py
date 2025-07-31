#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具函数模块
与 main_run.py 保持一致的工具函数实现
"""
import os
import time
import subprocess


def get_devices():
    """
    获取可用的Android设备列表
    与 main_run.py 中的设备获取逻辑保持一致

    Returns:
        list: 可用设备ID列表
    """
    try:
        from airtest.core.android.adb import ADB
        devices = [tmp[0] for tmp in ADB().devices()]
        return devices
    except Exception as e:
        print(f"获取设备列表失败: {e}")
        return []
