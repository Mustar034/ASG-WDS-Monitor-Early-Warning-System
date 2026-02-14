#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连接测试工具
用于测试树莓派到服务器的连接是否正常
"""

import sys
import requests
import json
from datetime import datetime

# 导入配置
import config


def test_basic_connection():
    """测试基本连通性"""
    print("[1/3] 测试基本连通性...")
    
    url = f"http://{config.SERVER_HOST}:{config.HTTP_PORT}/"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✓ 服务器可以访问")
            print(f"  响应: {response.json()}")
            return True
        else:
            print(f"✗ 服务器返回错误状态码: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ 连接超时,请检查:")
        print("  1. 服务器地址是否正确")
        print("  2. 服务器是否正在运行")
        print("  3. 网络连接是否正常")
        return False
        
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器,请检查:")
        print("  1. 服务器地址是否正确")
        print("  2. 防火墙是否开放了端口")
        print("  3. 服务器程序是否运行")
        return False
        
    except Exception as e:
        print(f"✗ 发生错误: {str(e)}")
        return False


def test_api_authentication():
    """测试API密钥认证"""
    print("\n[2/3] 测试API密钥认证...")
    
    url = f"http://{config.SERVER_HOST}:{config.HTTP_PORT}/api/sensor/status"
    headers = {
        'Authorization': f'Bearer {config.API_KEY}'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✓ API密钥验证成功")
            return True
        elif response.status_code == 401:
            print("✗ API密钥验证失败!")
            print("  请检查:")
            print("  1. config.py 中的 API_KEY 是否正确")
            print("  2. 是否与服务器端的 API_KEY 一致")
            return False
        else:
            print(f"✗ 服务器返回状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return False


def test_data_upload():
    """测试数据上传"""
    print("\n[3/3] 测试数据上传...")
    
    url = f"http://{config.SERVER_HOST}:{config.HTTP_PORT}/api/sensor/data"
    
    # 构建测试数据
    test_data = {
        'device_id': config.DEVICE_ID,
        'data': {
            'timestamp': datetime.now().isoformat(),
            'sensors': {
                'temperature': {'value': 25.5, 'unit': '°C'},
                'humidity': {'value': 60.0, 'unit': '%'}
            }
        }
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {config.API_KEY}'
    }
    
    try:
        response = requests.post(
            url,
            json=test_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✓ 测试数据上传成功")
            resp_data = response.json()
            print(f"  服务器响应: {resp_data.get('message', 'OK')}")
            return True
        else:
            print(f"✗ 上传失败,状态码: {response.status_code}")
            print(f"  响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return False


def print_config_info():
    """打印配置信息"""
    print("服务器地址: " + f"http://{config.SERVER_HOST}:{config.HTTP_PORT}")
    print("设备ID: " + config.DEVICE_ID)
    print("上传方式: " + config.UPLOAD_METHOD.upper())
    print()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  连接测试工具")
    print("=" * 60)
    print()
    
    # 打印配置信息
    print_config_info()
    
    # 验证配置
    is_valid, errors = config.validate_config()
    if not is_valid:
        print("✗ 配置验证失败:\n")
        for error in errors:
            print(f"  {error}")
        print("\n请修改 config.py 后重试。\n")
        return False
    
    # 运行测试
    results = []
    
    # 测试1: 基本连通性
    results.append(test_basic_connection())
    
    # 测试2: API认证
    if results[0]:  # 只有基本连通性通过才继续
        results.append(test_api_authentication())
    else:
        print("\n[2/3] 跳过API认证测试(基本连通性未通过)")
        print("[3/3] 跳过数据上传测试(基本连通性未通过)")
        results.append(False)
        results.append(False)
    
    # 测试3: 数据上传
    if results[1]:  # 只有认证通过才继续
        results.append(test_data_upload())
    elif results[0]:
        print("\n[3/3] 跳过数据上传测试(API认证未通过)")
        results.append(False)
    
    # 打印总结
    print("\n" + "=" * 60)
    
    if all(results):
        print("✓ 所有测试通过! 系统配置正确")
        print("=" * 60)
        print("\n下一步: 运行主程序")
        print("  python3 main.py\n")
        return True
    else:
        print("✗ 部分测试失败")
        print("=" * 60)
        print("\n测试结果:")
        print(f"  [1/3] 基本连通性: {'✓ 通过' if results[0] else '✗ 失败'}")
        if len(results) > 1:
            print(f"  [2/3] API认证: {'✓ 通过' if results[1] else '✗ 失败'}")
        if len(results) > 2:
            print(f"  [3/3] 数据上传: {'✓ 通过' if results[2] else '✗ 失败'}")
        
        print("\n请根据上述错误提示修复问题后重试。\n")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
