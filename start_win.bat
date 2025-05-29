@echo off
:: 设置UTF-8编码
chcp 65001 >nul
:: 启用延迟变量扩展
setlocal EnableDelayedExpansion

:: 设置窗口标题
title 体感控制器 客户端

:: 设置Python路径
set "PYTHON_PATH=%~dp0python"
set "PYTHON_EXE=%PYTHON_PATH%\python.exe"
set "PIP_EXE=%PYTHON_PATH%\Scripts\pip.exe"

:: 检查当前目录下的Python
if not exist "%PYTHON_EXE%" (
    echo Python未在当前目录找到，正在下载...
    
    :: 下载安装程序
    powershell -Command "& {Invoke-WebRequest -Uri 'https://oss.drea.cc/cloud/file/docs/ai-sense/primary/python-3.9.13-amd64.exe' -OutFile 'python-3.9.13.exe'}"
    
    if not exist "python-3.9.13.exe" (
        echo Python 安装包下载失败！
        pause
        exit /b 1
    )
    
    echo 正在安装 Python 3.9...
    :: 执行安装到当前目录
    python-3.9.13.exe /quiet InstallAllUsers=0 PrependPath=0 TargetDir="%PYTHON_PATH%"
    
    :: 清理安装文件
    del /f /q python-3.9.13.exe
)

:: 初始化 pip 环境
"%PYTHON_EXE%" -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip 不可用，正在安装...
    "%PYTHON_EXE%" -m ensurepip --default-pip
)

:: 配置 pip 镜像源
"%PYTHON_EXE%" -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

:: 更新 pip 版本
"%PYTHON_EXE%" -m pip install --upgrade pip

:: 安装项目依赖
echo 正在安装依赖...
"%PYTHON_EXE%" -m pip install -r requirements.txt

:: 配置用户信息
set /p "username=请输入云平台用户名（默认为 your_username）："
set /p "password=请输入云平台密码（默认为 your_password）："

:: 设置默认值
if "!username!"=="" set "username=your_username"
if "!password!"=="" set "password=your_password"

:: 配置输入控制
set /p "enable_input=是否启用输入控制？(y/n，默认为 y)："
if /i "!enable_input!"=="n" (
    set "input_enabled=false"
) else (
    set "input_enabled=true"
)

:: 生成配置文件
(
echo # 服务配置
echo server:
echo   port: 5800  # 监听端口
echo.
echo # 云平台配置
echo api:
echo   base_url: https://cloud.drea.cc  # 云平台地址
echo.
echo # 认证配置
echo auth:
echo   username: !username!  # 云平台用户名
echo   password: !password!  # 云平台密码
echo.
echo # 输入配置
echo input:
echo   is_enable: !input_enabled!  # 是否启用输入，调试动作的时候可以关闭
) > config.yaml

:: 启动应用程序
echo.
echo ====================================
echo           正在启动客户端
echo ====================================
echo.

"%PYTHON_EXE%" run.py

pause
