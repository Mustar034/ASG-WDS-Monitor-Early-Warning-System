
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析服务器返回的数据结构
"""

import requests
import json
from datetime import datetime

def analyze_server_response():
    """分析服务器响应"""
    
    print("=" * 60)
    print("  服务器数据结构分析")
    print("=" * 60)
    
    # 获取数据
    url = "http://47.108.55.104:5000/api/data"
    
    try:
        response = requests.get(url, params={'device': 'test'}, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 请求失败: {response.status_code}")
            return
        
        data = response.json()
        
        print("✅ 成功获取数据")
        print(f"数据获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. 显示完整数据结构
        print("1. 完整数据结构:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print()
        
        # 2. 分析UAV数据
        print("2. UAV（无人机）数据分析:")
        if 'uav' in data:
            uav = data['uav']
            print(f"  字段数量: {len(uav)}")
            print(f"  字段列表: {list(uav.keys())}")
            
            print("\n  字段详情:")
            for key, value in uav.items():
                print(f"    {key:15s}: {value} ({type(value).__name__})")
        else:
            print("  ❌ 无UAV数据")
        print()
        
        # 3. 分析USV数据
        print("3. USV（无人船）数据分析:")
        if 'usv' in data:
            usv = data['usv']
            print(f"  字段数量: {len(usv)}")
            print(f"  字段列表: {list(usv.keys())}")
            
            print("\n  字段详情:")
            for key, value in usv.items():
                print(f"    {key:15s}: {value} ({type(value).__name__})")
        else:
            print("  ❌ 无USV数据")
        print()
        
        # 4. 分析评分数据
        print("4. 系统评分分析:")
        if 'scores' in data:
            scores = data['scores']
            print(f"  字段数量: {len(scores)}")
            
            print("\n  评分详情:")
            for key, value in scores.items():
                print(f"    {key:20s}: {value}")
                
                # 评分评估
                if isinstance(value, (int, float)):
                    if value >= 90:
                        assessment = "优秀"
                    elif value >= 80:
                        assessment = "良好"
                    elif value >= 60:
                        assessment = "一般"
                    else:
                        assessment = "较差"
                    print(f"     评估: {assessment}")
        else:
            print("  ❌ 无评分数据")
        print()
        
        # 5. 数据更新频率分析
        print("5. 数据更新建议:")
        print("  基于数据结构，建议的查询频率:")
        print("  - UAV位置数据: 每秒1次（实时追踪）")
        print("  - USV传感器数据: 每5秒1次（环境监测）")
        print("  - 系统评分: 每分钟1次（状态评估）")
        print()
        
        # 6. 生成Python数据模型
        print("6. Python数据模型建议:")
        print('''
class UAVData:
    """无人机数据"""
    def __init__(self, data):
        self.status = data.get('status', 'Unknown')
        self.altitude = data.get('alt', 0.0)
        self.latitude = data.get('lat', 0.0)
        self.longitude = data.get('lng', 0.0)
    
    def __str__(self):
        return f"UAV: {self.status} at ({self.latitude:.6f}, {self.longitude:.6f})"

class USVData:
    """无人船数据"""
    def __init__(self, data):
        self.status = data.get('status', 'Unknown')
        self.temperature = data.get('temp', 0.0)
        self.humidity = data.get('humidity', 0.0)
        self.pressure = data.get('pressure', 0.0)
        self.light = data.get('light', 0)
        self.latitude = data.get('lat', 0.0)
        self.longitude = data.get('lng', 0.0)
    
    def __str__(self):
        return f"USV: {self.status}, Temp: {self.temperature}°C, Humidity: {self.humidity}%"

class SystemScores:
    """系统评分"""
    def __init__(self, data):
        self.dam_safety = data.get('dam_safety', 0.0)
        self.water_quality = data.get('water_quality', 0.0)
    
    def get_overall(self):
        """计算总体评分"""
        return (self.dam_safety + self.water_quality) / 2

class ServerData:
    """服务器数据容器"""
    def __init__(self, raw_data):
        self.uav = UAVData(raw_data.get('uav', {}))
        self.usv = USVData(raw_data.get('usv', {}))
        self.scores = SystemScores(raw_data.get('scores', {}))
        self.timestamp = datetime.now()
''')
        
        # 7. 使用建议
        print("7. 使用建议:")
        print("  a. 定时查询: 使用定时任务定期获取数据")
        print("  b. 数据存储: 将历史数据保存到数据库")
        print("  c. 异常检测: 监控数据异常（如温度突变）")
        print("  d. 可视化: 在地图上显示UAV/USV位置")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")

if __name__ == "__main__":
    analyze_server_response()