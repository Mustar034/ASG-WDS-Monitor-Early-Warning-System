
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门用于GET请求的配置
"""

# ============================================
# 服务器配置
# ============================================

# 服务器地址
SERVER_HOST = "47.108.55.104"  # 队友服务器
HTTP_PORT = 5000               # 端口

# API端点路径（GET方法）
HTTP_ENDPOINT = "/api/data"

# HTTP方法
HTTP_METHOD = "GET"            # 必须是GET！

# ============================================
# 查询参数配置
# ============================================

# 查询参数名称映射
QUERY_PARAMS = {
    'device_id': 'device',      # 你的字段名 -> 服务器参数名
    'temperature': 'temp',
    'humidity': 'humi',
    'timestamp': 'time'
}

# 默认参数值
DEFAULT_PARAMS = {
    'device': 'raspberry-pi-001',
    'format': 'json'
}

# ============================================
# 解析配置
# ============================================

# 数据格式版本
DATA_FORMAT_VERSION = "1.0"

# 用户代理
USER_AGENT = "RaspberryPi-GET-Client/1.0"

# ============================================
# 验证配置
# ============================================

def validate_config():
    """验证配置"""
    errors = []
    
    if HTTP_METHOD != "GET":
        errors.append("HTTP_METHOD 必须是 'GET'")
    
    if not SERVER_HOST or SERVER_HOST == "your-server-ip":
        errors.append("请设置正确的 SERVER_HOST")
    
    return len(errors) == 0, errors

def print_config():
    """打印配置"""
    print("=" * 60)
    print("GET 客户端配置:")
    print("=" * 60)
    print(f"服务器: {SERVER_HOST}:{HTTP_PORT}")
    print(f"端点: {HTTP_ENDPOINT}")
    print(f"方法: {HTTP_METHOD}")
    print(f"查询参数映射: {QUERY_PARAMS}")
    print(f"默认参数: {DEFAULT_PARAMS}")
    print("=" * 60)

if __name__ == "__main__":
    print_config()
    is_valid, errors = validate_config()
    
    if is_valid:
        print("✓ 配置验证通过")
    else:
        print("✗ 配置验证失败:")
        for error in errors:
            print(f"  {error}")