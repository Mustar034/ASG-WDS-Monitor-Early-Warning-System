#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连续查询服务器数据
"""

import requests
import json
import time
import sys
from datetime import datetime
import threading

class ContinuousQuery:
    def __init__(self, interval=5):
        self.server_url = "http://47.108.55.104:5000/api/data"
        self.interval = interval  # 查询间隔（秒）
        self.running = False
        self.query_count = 0
        self.last_data = None
        
    def fetch_data(self):
        """获取数据"""
        try:
            params = {
                'device': 'raspberry-pi-monitor',
                'timestamp': int(time.time()),
                'format': 'json'
            }
            
            response = requests.get(self.server_url, params=params, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 请求失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 错误: {e}")
            return None
    
    def display_data(self, data):
        """显示数据"""
        if not data:
            return
        
        self.last_data = data
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 第{self.query_count}次查询")
        print("-" * 60)
        
        # UAV信息
        if 'uav' in data:
            uav = data['uav']
            print(f"✈️  UAV状态: {uav.get('status', 'N/A'):10s} | "
                  f"高度: {uav.get('alt', 0):6.1f}m | "
                  f"位置: {uav.get('lat', 0):.6f}, {uav.get('lng', 0):.6f}")
        
        # USV信息
        if 'usv' in data:
            usv = data['usv']
            print(f"🛥️  USV状态: {usv.get('status', 'N/A'):10s} | "
                  f"温度: {usv.get('temp', 0):6.1f}°C | "
                  f"湿度: {usv.get('humidity', 0):6.1f}% | "
                  f"光照: {usv.get('light', 0):6d}lx")
        
        # 评分
        if 'scores' in data:
            scores = data['scores']
            print(f"📊 系统评分: 大坝安全: {scores.get('dam_safety', 0):5.1f} | "
                  f"水质: {scores.get('water_quality', 0):5.1f}")
    
    def check_anomalies(self, current_data, previous_data):
        """检查数据异常"""
        if not previous_data:
            return
        
        anomalies = []
        
        # 检查USV温度突变
        if 'usv' in current_data and 'usv' in previous_data:
            current_temp = current_data['usv'].get('temp', 0)
            previous_temp = previous_data['usv'].get('temp', 0)
            
            if abs(current_temp - previous_temp) > 5:  # 温度变化超过5度
                anomalies.append(f"温度突变: {previous_temp}°C → {current_temp}°C")
        
        # 检查状态变化
        if 'usv' in current_data and 'usv' in previous_data:
            current_status = current_data['usv'].get('status', '')
            previous_status = previous_data['usv'].get('status', '')
            
            if current_status != previous_status:
                anomalies.append(f"USV状态变化: {previous_status} → {current_status}")
        
        if anomalies:
            print("\n⚠️  检测到异常:")
            for anomaly in anomalies:
                print(f"  • {anomaly}")
    
    def run_continuous(self):
        """连续运行"""
        self.running = True
        previous_data = None
        
        print("=" * 60)
        print("  连续数据查询系统")
        print("=" * 60)
        print(f"服务器: {self.server_url}")
        print(f"查询间隔: {self.interval}秒")
        print("按 Ctrl+C 停止")
        print("=" * 60)
        
        try:
            while self.running:
                self.query_count += 1
                
                # 获取数据
                data = self.fetch_data()
                
                if data:
                    # 显示数据
                    self.display_data(data)
                    
                    # 检查异常
                    self.check_anomalies(data, previous_data)
                    previous_data = data
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 获取数据失败")
                
                # 等待
                for _ in range(self.interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n\n用户中断")
        finally:
            self.running = False
            print("\n" + "=" * 60)
            print(f"查询结束")
            print(f"总查询次数: {self.query_count}")
            print("=" * 60)
    
    def run_once(self):
        """单次运行"""
        print("执行单次查询...")
        data = self.fetch_data()
        if data:
            self.display_data(data)
            return data
        return None
    
    def start_in_thread(self):
        """在后台线程中运行"""
        thread = threading.Thread(target=self.run_continuous, daemon=True)
        thread.start()
        return thread

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='连续查询服务器数据')
    parser.add_argument('--interval', type=int, default=5, help='查询间隔（秒）')
    parser.add_argument('--once', action='store_true', help='只执行一次查询')
    parser.add_argument('--duration', type=int, help='运行持续时间（秒）')
    
    args = parser.parse_args()
    
    query = ContinuousQuery(interval=args.interval)
    
    if args.once:
        query.run_once()
    elif args.duration:
        # 运行指定时间
        print(f"运行 {args.duration} 秒...")
        thread = query.start_in_thread()
        time.sleep(args.duration)
        query.running = False
        thread.join()
    else:
        # 连续运行
        query.run_continuous()

if __name__ == "__main__":
    main()