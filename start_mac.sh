#!/bin/bash

# 设置窗口标题
echo -e "\033]0;体感控制器 客户端\007"

# 检查并安装 Python 环境
if ! command -v python3.9 &> /dev/null; then
    echo "Python 3.9 未安装，请访问以下地址下载安装："
    echo "https://oss.drea.cc/cloud/file/docs/ai-sense/primary/python-3.9.13-macos11.pkg"
    echo "安装完成后重新运行此脚本"
    exit 1
fi

# 初始化 pip 环境
if ! python3.9 -m pip --version &> /dev/null; then
    echo "pip 不可用，正在安装..."
    python3.9 -m ensurepip --default-pip
fi

# 配置 pip 镜像源
python3.9 -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 更新 pip 版本
python3.9 -m pip install --upgrade pip

# 安装项目依赖
echo "正在安装依赖..."
python3.9 -m pip install -r requirements.txt

# 配置用户信息
read -p "请输入云平台用户名（默认为 your_username）：" username
read -p "请输入云平台密码（默认为 your_password）：" password

# 设置默认值
username=${username:-your_username}
password=${password:-your_password}

# 配置输入控制
read -p "是否启用输入控制？(y/n，默认为 y)：" enable_input
if [[ ${enable_input,,} == "n" ]]; then
    input_enabled=false
else
    input_enabled=true
fi

# 生成配置文件
cat > config.yaml << EOF
# 服务配置
server:
  port: 5800  # 监听端口

# 云平台配置
api:
  base_url: https://cloud.drea.cc  # 云平台地址

# 认证配置
auth:
  username: $username  # 云平台用户名
  password: $password  # 云平台密码

# 输入配置
input:
  is_enable: $input_enabled  # 是否启用输入，调试动作的时候可以关闭
EOF

# 启动应用程序
echo
echo "===================================="
echo "          正在启动客户端"
echo "===================================="
echo

python3.9 run.py

read -p "按回车键退出..." 