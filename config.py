#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件 - 空地海地面站智能数显系统
请根据实际情况修改以下配置
"""

# ============================================
# 服务器配置 (必须修改!)
# ============================================

# 阿里云服务器地址 - 改成你的服务器IP或域名
SERVER_HOST = "47.108.55.104"  # 服务器地址

# 服务器端口
HTTP_PORT = 5000               # HTTP服务端口
MQTT_PORT = 1883               # MQTT服务端口

# ============================================
# 认证配置 (必须修改!)
# ============================================

# API密钥 - 必须与服务器端的API_KEY保持一致
API_KEY = "oKgpm6SpsnmdnaXu0O1bbeb4VKbzzU"

# 设备唯一标识 - 给你的树莓派起个名字
DEVICE_ID = "raspberry-pi-001"  # 可以改成你喜欢的名字

# ============================================
# 上传方式选择
# ============================================

# 上传方式: "http" 或 "mqtt"
UPLOAD_METHOD = "http"  # 确保使用HTTP上传

# ============================================
# 传感器配置
# ============================================

# 启用的传感器类型列表
SENSOR_TYPES = [
    'temperature',  # 温度传感器
    'humidity',     # 湿度传感器
    'pressure',     # 气压传感器
    'light'         # 光照传感器
]

# 数据采集间隔(秒)
COLLECT_INTERVAL = 30

# ============================================
# HTTP上传配置
# ============================================

# API端点路径 - 队友服务器的端点
HTTP_ENDPOINT = "/api/esp32"  # 重要：修改为队友的端点

# 请求超时时间(秒)
HTTP_TIMEOUT = 10

# 失败重试次数
HTTP_RETRY_TIMES = 3

# 是否启用数据缓存
ENABLE_CACHE = True

# 缓存文件路径
CACHE_FILE = "cache_data.json"

# ============================================
# 仪表盘显示配置
# ============================================

# 显示模式选择
# 'browser' - 使用浏览器全屏显示（需要桌面环境）
# 'pygame' - 使用Pygame轻量显示（适合小屏幕）
# 'pyqt' - 使用PyQt5显示（功能最全）
# 'tkinter' - 使用Tkinter GUI显示（无需额外安装）
# 'none' - 不自动显示
DISPLAY_MODE = 'tkinter'  # 根据你的显示屏选择

# 显示分辨率（仅对pygame、pyqt和tkinter有效）
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480

# 是否启用全屏
FULLSCREEN = True

# 仪表盘服务器端口（避免与其他服务冲突）
DASHBOARD_PORT = 5002

# 是否自动打开浏览器
AUTO_OPEN_BROWSER = True

# ============================================
# MQTT上传配置
# ============================================

# MQTT主题
MQTT_TOPIC = "sensor/data"

# MQTT服务质量(QoS)
# 0: 至多一次(不保证送达)
# 1: 至少一次(推荐)
# 2: 恰好一次(最严格)
MQTT_QOS = 1

# 是否保留消息
MQTT_RETAIN = False

# 保持连接时间(秒)
MQTT_KEEPALIVE = 60

# ============================================
# 日志配置
# ============================================

# 日志级别: "DEBUG", "INFO", "WARNING", "ERROR"
LOG_LEVEL = "INFO"

# 日志文件路径
LOG_FILE = "sensor_data.log"

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================
# 高级配置(一般不需要修改)
# ============================================

# 是否在控制台显示详细信息
VERBOSE = True

# 数据格式版本
DATA_FORMAT_VERSION = "1.0"

# 用户代理字符串
USER_AGENT = "RaspberryPi-Sensor-Client/1.0"

# 是否使用真实传感器（False则使用虚拟数据）
USE_REAL_SENSORS = False

# ============================================
# 配置验证函数
# ============================================

def validate_config():
    """
    验证配置是否正确
    返回: (是否有效, 错误信息列表)
    """
    errors = []
    
    # 检查服务器地址
    if SERVER_HOST in ["123.456.789.0", ""]:
        errors.append("⚠️  请修改 SERVER_HOST 为你的实际服务器地址!")
    
    # 检查API密钥
    if API_KEY == "your-api-key-here":
        errors.append("⚠️  请修改 API_KEY 为你的实际API密钥!")
    
    # 检查上传方式
    if UPLOAD_METHOD not in ["http", "mqtt"]:
        errors.append(f"⚠️  UPLOAD_METHOD 必须是 'http' 或 'mqtt', 当前值: {UPLOAD_METHOD}")
    
    # 检查采集间隔
    if COLLECT_INTERVAL < 1:
        errors.append("⚠️  COLLECT_INTERVAL 必须大于等于1秒")
    
    # 检查传感器类型
    valid_sensors = ['temperature', 'humidity', 'pressure', 'light']
    for sensor in SENSOR_TYPES:
        if sensor not in valid_sensors:
            errors.append(f"⚠️  无效的传感器类型: {sensor}")
    
    # 检查显示模式 - 已更新包含'tkinter'
    valid_displays = ['browser', 'pygame', 'pyqt', 'tkinter', 'none']
    if DISPLAY_MODE not in valid_displays:
        errors.append(f"⚠️  无效的显示模式: {DISPLAY_MODE}")
    
    return len(errors) == 0, errors


def print_config():
    """打印当前配置"""
    print("=" * 60)
    print("当前配置:")
    print("=" * 60)
    print(f"服务器地址: {SERVER_HOST}:{HTTP_PORT if UPLOAD_METHOD == 'http' else MQTT_PORT}")
    print(f"设备ID: {DEVICE_ID}")
    print(f"上传方式: {UPLOAD_METHOD.upper()}")
    print(f"传感器类型: {', '.join(SENSOR_TYPES)}")
    print(f"采集间隔: {COLLECT_INTERVAL} 秒")
    print(f"显示模式: {DISPLAY_MODE.upper()}")
    if DISPLAY_MODE in ['pygame', 'pyqt', 'tkinter']:
        print(f"显示分辨率: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
        print(f"全屏模式: {'是' if FULLSCREEN else '否'}")
    print("=" * 60)


# ============================================
# 主程序 - 用于测试配置
# ============================================

if __name__ == "__main__":
    print("\n配置文件测试\n")
    
    # 打印配置
    print_config()
    print()
    
    # 验证配置
    is_valid, errors = validate_config()
    
    if is_valid:
        print("✓ 配置验证通过!")
    else:
        print("✗ 配置验证失败,发现以下问题:\n")
        for error in errors:
            print(f"  {error}")
        print("\n请修改 config.py 后重试。")