@echo off
:: 设置UTF-8编码
chcp 65001 >nul
:: 启用延迟变量扩展
setlocal EnableDelayedExpansion

:: 设置窗口标题
title 体感控制器 客户端打包工具

:: 检查Python 3是否存在
python --version 2>nul | findstr /C:"Python 3" >nul
if %errorlevel% neq 0 (
    echo Python 3未安装，正在下载安装程序...
    
    :: 下载Python安装程序
    powershell -Command "& {Invoke-WebRequest -Uri 'https://oss.drea.cc/cloud/file/docs/ai-sense/primary/python-3.9.13-amd64.exe' -OutFile 'python-3.9.13.exe'}"
    
    echo 正在安装Python 3.9.13...

    :: 执行安装
    python-3.9.13.exe /quiet InstallAllUsers=1 PrependPath=1
    
    :: 等待安装完成
    timeout /t 10 /nobreak
    
    :: 清理安装文件
    del /f /q python-3.9.13.exe

)

:: 配置 pip 镜像源
python -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

:: 更新 pip 版本
python -m pip install --upgrade pip

:: 安装项目依赖和打包工具
echo 正在安装依赖...
python -m pip install -r requirements.txt
python -m pip install pyinstaller
python -m pip install eventlet

:: 执行打包脚本
echo.
echo ====================================
echo           开始打包程序
echo ====================================
echo.

:: 直接使用PyInstaller命令进行打包
python -m PyInstaller build.spec

:: 打包完成
echo.
echo ====================================
echo      打包完成，请查看dist目录
echo ====================================

echo.
pause 