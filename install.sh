#!/bin/bash

# ============================================
# 树莓派传感器采集系统 - 一键安装脚本
# ============================================

echo "============================================"
echo "  树莓派传感器数据采集系统"
echo "  一键安装脚本"
echo "============================================"
echo ""

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then 
    echo "⚠️  警告: 请不要使用root用户运行此脚本"
    echo "请使用普通用户(如pi)运行: ./install.sh"
    exit 1
fi

# 检查Python3
echo "[1/5] 检查Python3..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ 已安装: $PYTHON_VERSION"
else
    echo "✗ 未安装Python3"
    echo "正在安装Python3..."
    sudo apt update
    sudo apt install python3 python3-pip -y
fi

# 检查pip3
echo ""
echo "[2/5] 检查pip3..."
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version)
    echo "✓ 已安装: $PIP_VERSION"
else
    echo "✗ 未安装pip3"
    echo "正在安装pip3..."
    sudo apt install python3-pip -y
fi

# 升级pip
echo ""
echo "[3/5] 升级pip..."
python3 -m pip install --upgrade pip --user

# 安装依赖库
echo ""
echo "[4/5] 安装Python依赖库..."
echo ""

# 检查网络
echo "正在测试网络连接..."
if ping -c 1 pypi.org &> /dev/null || ping -c 1 8.8.8.8 &> /dev/null; then
    echo "✓ 网络连接正常"
    
    # 询问是否使用国内镜像
    echo ""
    read -p "是否使用清华大学镜像加速下载? [y/N]: " use_mirror
    
    if [[ $use_mirror =~ ^[Yy]$ ]]; then
        echo "使用清华镜像安装..."
        pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple requests paho-mqtt
    else
        echo "使用官方源安装..."
        pip3 install requests paho-mqtt
    fi
else
    echo "✗ 网络连接失败,请检查网络后重试"
    exit 1
fi

# 验证安装
echo ""
echo "[5/5] 验证安装..."
echo ""

# 检查requests
if python3 -c "import requests" 2>/dev/null; then
    echo "✓ requests 安装成功"
else
    echo "✗ requests 安装失败"
    INSTALL_FAILED=1
fi

# 检查paho-mqtt
if python3 -c "import paho.mqtt.client" 2>/dev/null; then
    echo "✓ paho-mqtt 安装成功"
else
    echo "✗ paho-mqtt 安装失败"
    INSTALL_FAILED=1
fi

# 检查安装结果
echo ""
echo "============================================"
if [ -z "$INSTALL_FAILED" ]; then
    echo "✓ 安装完成!"
    echo "============================================"
    echo ""
    echo "下一步:"
    echo "  1. 编辑配置文件: nano config.py"
    echo "  2. 修改服务器地址和API密钥"
    echo "  3. 测试连接: python3 test_connection.py"
    echo "  4. 运行程序: python3 main.py"
    echo ""
else
    echo "✗ 安装过程中出现错误"
    echo "============================================"
    echo ""
    echo "请尝试手动安装:"
    echo "  pip3 install requests paho-mqtt"
    echo ""
    exit 1
fi

# 设置执行权限
echo "设置脚本执行权限..."
chmod +x *.py 2>/dev/null
echo ""

echo "🎉 准备就绪! 祝使用愉快!"
