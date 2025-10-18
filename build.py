#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用Nuitka打包SeatsChanger应用程序的构建脚本

可通过修改脚本中的参数来自定义打包行为
"""

import os
import sys
import subprocess
from pathlib import Path

# ============================================
# 打包配置参数（可根据需要修改）
# ============================================

# 程序入口文件
ENTRY_FILE = "main.py"

# 输出目录
OUTPUT_DIR = "dist"

# 是否创建独立可执行文件（不依赖Python环境）
ONEFILE = False  # 修改为False以生成多文件形式输出

# 应用程序名称
APP_NAME = "SeatsChanger"

# 应用版本
APP_VERSION = "1.0.0"

# 作者信息
AUTHOR = "汐光"

# 是否包含控制台窗口
CONSOLE = False  # GUI应用通常设为False

# 需要包含的数据文件或目录（相对于项目根目录）
DATA_FILES = [
    # (源路径, 目标路径)
    # 例如: ("data", "data"),
    # 如果有CSV文件，可以添加: ("*.csv", ".")
]

# 需要包含的额外Python模块（移除通配符格式）
EXTRA_MODULES = [
    "PyQt5",
    "PyQt5.QtWidgets",
    "PyQt5.QtCore",
    "PyQt5.QtGui",
    "qfluentwidgets"
]

# 优化选项
OPTIMIZATION_LEVEL = 2  # 0-3，3为最高优化

# 其他Nuitka参数（支持增量构建版本）
EXTRA_ARGS = [
    "--show-progress",  # 显示构建进度
    # 移除--remove-output以支持增量构建
    "--standalone",     # 创建独立运行环境
    "--enable-plugin=pyqt5",  # 启用PyQt5插件支持
    "--nofollow-import-to=*.test,*.tests",  # 忽略测试模块，加快构建
    "--assume-yes-for-downloads",  # 自动下载依赖
    # 使用缓存目录存储中间文件，加速后续构建
    "--python-cache-dir=".join([os.path.dirname(os.path.abspath(__file__)), "nuitka_cache"]),
]

# ============================================
# 构建脚本主体
# ============================================

def build():
    """执行Nuitka打包命令"""
    
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 构建命令列表
    cmd = [
        sys.executable,
        "-m",
        "nuitka",
    ]
    
    # 添加基本参数
    cmd.extend([
        f"--output-dir={OUTPUT_DIR}",
    ])
    
    # 处理标志类参数
    if ONEFILE:
        cmd.append("--onefile")
    
    # 使用新版Nuitka支持的控制台模式参数
    if os.name == 'nt':
        if not CONSOLE:
            cmd.append("--windows-console-mode=disable")
    
    # 暂时不使用LTO优化，避免可能的兼容性问题
    # cmd.extend([
    #     f"--lto={'yes' if OPTIMIZATION_LEVEL >= 2 else 'no'}",
    # ])
    
    # 添加应用信息（仅Windows）
    if os.name == 'nt':
        cmd.extend([
            f"--windows-product-name={APP_NAME}",
            f"--windows-file-version={APP_VERSION}",
            f"--windows-product-version={APP_VERSION}",
        ])
        if AUTHOR:
            cmd.append(f"--windows-company-name={AUTHOR}")
    
    # 添加需要包含的数据文件
    for src, dst in DATA_FILES:
        cmd.append(f"--include-data-files={src}={dst}")
    
    # 添加需要包含的额外模块
    for module in EXTRA_MODULES:
        cmd.append(f"--include-module={module}")
    
    # 添加其他额外参数
    cmd.extend([arg for arg in EXTRA_ARGS if arg])
    
    # 添加入口文件
    cmd.append(ENTRY_FILE)
    
    # 打印构建命令
    print("构建命令:")
    print(' '.join(cmd))
    print("\n开始构建...")
    
    try:
        # 执行构建命令
        subprocess.run(cmd, check=True)
        print(f"\n✅ 构建成功！输出目录: {OUTPUT_DIR}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 构建失败: {e}")
        sys.exit(1)

def check_requirements():
    """检查构建环境依赖"""
    print("检查构建环境...")
    
    # 检查Nuitka是否安装
    try:
        subprocess.run([sys.executable, "-m", "nuitka", "--version"], 
                      check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ Nuitka已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Nuitka未安装，请运行: pip install nuitka")
        return False
    
    # 检查依赖项是否安装
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        for req in requirements:
            print(f"检查依赖: {req}...")
            # 这里只是简单检查，实际使用时可能需要更复杂的依赖检查
    except Exception as e:
        print(f"检查依赖时出错: {e}")
    
    return True

def main():
    """主函数"""
    print(f"=== SeatsChanger 打包工具 ===\n")
    
    # 检查构建环境
    if not check_requirements():
        print("\n请先安装必要的依赖，然后再次运行此脚本。")
        sys.exit(1)
    
    # 开始构建
    build()

if __name__ == "__main__":
    main()