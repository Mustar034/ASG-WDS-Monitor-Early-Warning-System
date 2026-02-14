
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GET连接测试工具
用于测试树莓派到服务器的GET连接
"""

import sys
import requests
import json
import urllib.parse
from datetime import datetime

# 导入配置
import config_get as config


def build_query_params(sensor_data=None):
    """构建查询参数"""
    
    # 从默认参数开始
    params = config.DEFAULT_PARAMS.copy()
    
    # 如果提供了传感器数据，添加进去
    if sensor_data:
        # 遍历映射，将我们的字段名转换为服务器参数名
        for our_key, server_key in config.QUERY_PARAMS.items():
            if our_key in sensor_data:
                params[server_key] = sensor_data[our_key]
    
    return params


def test_basic_connection():
    """测试基本连通性"""
    print("[1/3] 测试基本连通性...")
    
    # 构建URL
    base_url = f"http://{config.SERVER_HOST}:{config.HTTP_PORT}"
    url = base_url + config.HTTP_ENDPOINT
    
    try:
        # 使用GET方法
        response = requests.get(url, params=config.DEFAULT_PARAMS, timeout=10)
        
        if response.status_code == 200:
            print("✓ 服务器可以访问")
            
            # 尝试解析JSON响应
            try:
                data = response.json()
                print(f"  响应数据:")
                print(f"    状态: {data.get('usv', {}).get('status', 'N/A')}")
                print(f"    温度: {data.get('usv', {}).get('temp', 'N/A')}°C")
                print(f"    湿度: {data.get('usv', {}).get('humidity', 'N/A')}%")
                print(f"    位置: Lat={data.get('usv', {}).get('lat', 'N/A')}, Lng={data.get('usv', {}).get('lng', 'N/A')}")
            except:
                print(f"  响应文本: {response.text[:200]}")
            
            return True
        else:
            print(f"✗ 服务器返回错误状态码: {response.status_code}")
            print(f"  响应: {response.text[:200]}")
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


def test_with_sensor_data():
    """测试带传感器数据的查询"""
    print("\n[2/3] 测试带传感器数据的查询...")
    
    # 构建模拟的传感器数据
    sensor_data = {
        'device_id': 'raspberry-pi-001',
        'temperature': 25.5,
        'humidity': 60.0,
        'timestamp': datetime.now().isoformat()
    }
    
    # 构建查询参数
    params = build_query_params(sensor_data)
    
    base_url = f"http://{config.SERVER_HOST}:{config.HTTP_PORT}"
    url = base_url + config.HTTP_ENDPOINT
    
    print(f"  发送参数: {params}")
    print(f"  完整URL: {url}?{urllib.parse.urlencode(params)}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print("✓ 数据查询成功")
            
            # 显示响应数据
            try:
                data = response.json()
                
                # 打印格式化响应
                print("\n  服务器响应数据:")
                print("  " + "-" * 40)
                
                # UAV数据
                if 'uav' in data:
                    uav = data['uav']
                    print(f"  UAV状态:")
                    print(f"    状态: {uav.get('status', 'N/A')}")
                    print(f"    海拔: {uav.get('alt', 'N/A')}m")
                    print(f"    位置: {uav.get('lat', 'N/A'):.6f}, {uav.get('lng', 'N/A'):.6f}")
                
                # USV数据
                if 'usv' in data:
                    usv = data['usv']
                    print(f"\n  USV状态:")
                    print(f"    状态: {usv.get('status', 'N/A')}")
                    print(f"    温度: {usv.get('temp', 'N/A')}°C")
                    print(f"    湿度: {usv.get('humidity', 'N/A')}%")
                    print(f"    气压: {usv.get('pressure', 'N/A')}hPa")
                    print(f"    光照: {usv.get('light', 'N/A')}lx")
                    print(f"    位置: {usv.get('lat', 'N/A'):.6f}, {usv.get('lng', 'N/A'):.6f}")
                
                # 分数
                if 'scores' in data:
                    scores = data['scores']
                    print(f"\n  系统评分:")
                    print(f"    大坝安全: {scores.get('dam_safety', 'N/A')}")
                    print(f"    水质: {scores.get('water_quality', 'N/A')}")
                
            except json.JSONDecodeError:
                print(f"  响应文本: {response.text[:200]}")
            
            return True
        else:
            print(f"✗ 查询失败,状态码: {response.status_code}")
            print(f"  响应: {response.text[:100]}")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return False


def test_error_handling():
    """测试错误处理"""
    print("\n[3/3] 测试错误处理...")
    
    base_url = f"http://{config.SERVER_HOST}:{config.HTTP_PORT}"
    
    # 测试1: 错误的端点
    print("  测试1: 错误端点...")
    try:
        response = requests.get(base_url + "/api/wrong_endpoint", timeout=5)
        print(f"    状态码: {response.status_code}")
    except Exception as e:
        print(f"    错误: {e}")
    
    # 测试2: 空查询
    print("  测试2: 空查询...")
    try:
        response = requests.get(base_url + config.HTTP_ENDPOINT, params={}, timeout=5)
        print(f"    状态码: {response.status_code}")
    except Exception as e:
        print(f"    错误: {e}")
    
    # 测试3: 超长参数
    print("  测试3: 超长参数...")
    try:
        long_params = {'device': 'a' * 1000}
        response = requests.get(base_url + config.HTTP_ENDPOINT, params=long_params, timeout=5)
        print(f"    状态码: {response.status_code}")
    except Exception as e:
        print(f"    错误: {e}")
    
    return True


def print_config_info():
    """打印配置信息"""
    print("服务器地址: " + f"http://{config.SERVER_HOST}:{config.HTTP_PORT}")
    print("API端点: " + config.HTTP_ENDPOINT)
    print("请求方法: " + config.HTTP_METHOD)
    print()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  GET连接测试工具")
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
        print("\n请修改 config_get.py 后重试。\n")
        return False
    
    # 运行测试
    results = []
    
    # 测试1: 基本连通性
    results.append(test_basic_connection())
    
    # 测试2: 带数据查询
    results.append(test_with_sensor_data())
    
    # 测试3: 错误处理
    results.append(test_error_handling())
    
    # 打印总结
    print("\n" + "=" * 60)
    
    if all(results[:2]):  # 前两个测试通过
        print("✓ 主要测试通过! 系统可以连接")
        print("=" * 60)
        print("\n发现服务器数据:")
        print("  1. 包含UAV（无人机）和USV（无人船）数据")
        print("  2. 包含环境传感器数据（温度、湿度、气压、光照）")
        print("  3. 包含位置信息")
        print("  4. 包含系统评分")
        print("\n下一步: 确认是否需要上传数据")
        print("  当前服务器似乎只提供数据查询，不接收上传")
        return True
    else:
        print("✗ 部分测试失败")
        print("=" * 60)
        print("\n测试结果:")
        print(f"  [1/3] 基本连通性: {'✓ 通过' if results[0] else '✗ 失败'}")
        print(f"  [2/3] 数据查询: {'✓ 通过' if results[1] else '✗ 失败'}")
        print(f"  [3/3] 错误处理: {'✓ 通过' if results[2] else '✗ 失败'}")
        
        print("\n请根据上述错误提示修复问题后重试。\n")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
