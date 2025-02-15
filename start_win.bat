@echo off
chcp 65001
setlocal EnableDelayedExpansion

:: 设置窗口标题
title 体感控制器 客户端

:: 检查并安装 Python 环境
python --version 2>nul | findstr "Python 3.9" >nul
if %errorlevel% neq 0 (
    echo Python 3.9 未安装，正在下载...
    
    :: 下载安装程序
    powershell -Command "& {Invoke-WebRequest -Uri 'https://oss.drea.cc/cloud/file/docs/ai-sense/primary/python-3.9.13-amd64.exe' -OutFile 'python-3.9.13.exe'}"
    
    if not exist "python-3.9.13.exe" (
        echo Python 安装包下载失败！
        pause
        exit /b 1
    )
    
    echo 正在安装 Python 3.9...
    :: 执行静默安装
    python-3.9.13.exe /quiet InstallAllUsers=1 PrependPath=1
    
    :: 清理安装文件
    del /f /q python-3.9.13.exe
    
    :: 更新环境变量
    call RefreshEnv.cmd >nul 2>&1
)

:: 初始化 pip 环境
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip 不可用，正在安装...
    python -m ensurepip --default-pip
)

:: 配置 pip 镜像源
python -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

:: 更新 pip 版本
python -m pip install --upgrade pip

:: 安装项目依赖
echo 正在安装依赖...
python -m pip install -r requirements.txt

:: 配置用户信息
set /p username=请输入云平台用户名（默认为 your_username）：
set /p password=请输入云平台密码（默认为 your_password）：

:: 设置默认值
if "!username!"=="" set username=your_username
if "!password!"=="" set password=your_password

:: 配置输入控制
set /p enable_input=是否启用输入控制？(y/n，默认为 y)：
if /i "!enable_input!"=="n" (
    set input_enabled=false
) else (
    set input_enabled=true
)

:: 生成配置文件
echo # 服务配置> config.yaml
echo server:>> config.yaml
echo   port: 5800  # 监听端口>> config.yaml
echo.>> config.yaml
echo # 云平台配置>> config.yaml
echo api:>> config.yaml
echo   base_url: https://cloud.drea.cc  # 云平台地址>> config.yaml
echo.>> config.yaml
echo # 认证配置>> config.yaml
echo auth:>> config.yaml
echo   username: !username!  # 云平台用户名>> config.yaml
echo   password: !password!  # 云平台密码>> config.yaml
echo.>> config.yaml
echo # 输入配置>> config.yaml
echo input:>> config.yaml
echo   is_enable: !input_enabled!  # 是否启用输入，调试动作的时候可以关闭>> config.yaml

:: 启动应用程序
echo.
echo ====================================
echo           正在启动客户端
echo ====================================
echo.

python run.py

pause
