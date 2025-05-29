#!/bin/bash

# 设置标题
echo "体感控制器 客户端打包工具"

# 检查Python 3是否存在
if ! command -v python3 &> /dev/null; then
    echo "Python 3未安装，请先下载安装！"
    echo "下载地址：https://oss.drea.cc/cloud/file/docs/ai-sense/primary/python-3.9.13-macos11.pkg"
    exit 1
fi

# 配置pip镜像源
python3 -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 更新pip版本
python3 -m pip install --upgrade pip

# 安装项目依赖和打包工具
echo "正在安装依赖..."
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller
python3 -m pip install eventlet

# 执行打包脚本
echo
echo "===================================="
echo "           开始打包程序"
echo "===================================="
echo

# 直接使用PyInstaller命令进行打包
python3 -m PyInstaller build.spec

# 打包完成
echo
echo "===================================="
echo "      打包完成，请查看dist目录"
echo "===================================="

echo
read -p "按回车键继续..." 