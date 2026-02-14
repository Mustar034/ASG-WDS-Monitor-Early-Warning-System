#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空地海地面站智能数显系统 - 可视化仪表盘
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import threading
import time
import json
import os

class Dashboard:
    """炫酷的可视化仪表盘"""
    
    def __init__(self, host='0.0.0.0', port=5002):
        """初始化仪表盘"""
        self.host = host
        self.port = port
        self.app = Flask(__name__, 
                         template_folder='templates',
                         static_folder='static')
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # 存储最新数据
        self.latest_data = {
            'uav': {'lat': 36.1250, 'lng': 120.6550, 'alt': 55.2, 'status': 'Ready'},
            'usv': {'lat': 36.1180, 'lng': 120.6620, 'temp': 22.5, 'humidity': 55, 
                    'pressure': 1013.2, 'light': 1200, 'status': 'Active'},
            'scores': {'water_quality': 0.0, 'dam_safety': 0.0},
            'meta': {'last_update_ts': 0, 'source': 'none'}
        }
        
        # 历史数据
        self.history_data = {
            'timestamps': [],
            'temperature': [],
            'humidity': [],
            'pressure': [],
            'light': []
        }
        
        # 设置路由
        self._setup_routes()
    
    def _setup_routes(self):
        """设置路由"""
        @self.app.route('/')
        def index():
            """主页面"""
            return render_template('index.html')
        
        @self.app.route('/api/data')
        def get_data():
            """获取当前数据"""
            return jsonify(self.latest_data)
        
        @self.app.route('/api/history')
        def get_history():
            """获取历史数据"""
            return jsonify(self.history_data)
        
        @self.socketio.on('connect')
        def handle_connect():
            """客户端连接"""
            print('客户端已连接')
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """客户端断开"""
            print('客户端已断开')
    
    def update_data(self, sensor_data):
        """更新数据"""
        # 这里需要根据你的实际数据结构进行调整
        if isinstance(sensor_data, dict):
            # 假设sensor_data的结构是 {'sensors': {...}}
            sensors = sensor_data.get('sensors', {})
            
            # 更新USV数据
            temp = sensors.get('temperature', {}).get('value')
            humidity = sensors.get('humidity', {}).get('value')
            pressure = sensors.get('pressure', {}).get('value')
            light = sensors.get('light', {}).get('value')
            
            if temp:
                self.latest_data['usv']['temp'] = temp
            if humidity:
                self.latest_data['usv']['humidity'] = humidity
            if pressure:
                self.latest_data['usv']['pressure'] = pressure
            if light:
                self.latest_data['usv']['light'] = light
            
            # 更新时间戳
            self.latest_data['meta']['last_update_ts'] = int(time.time())
            self.latest_data['meta']['source'] = 'dashboard'
            
            # 添加到历史数据
            timestamp = time.strftime('%H:%M:%S')
            self.history_data['timestamps'].append(timestamp)
            self.history_data['temperature'].append(temp or 0)
            self.history_data['humidity'].append(humidity or 0)
            self.history_data['pressure'].append(pressure or 0)
            self.history_data['light'].append(light or 0)
            
            # 保持最近100个数据点
            max_points = 100
            for key in self.history_data:
                if len(self.history_data[key]) > max_points:
                    self.history_data[key] = self.history_data[key][-max_points:]
            
            # 通过WebSocket推送数据
            self.socketio.emit('data_update', {
                'data': self.latest_data,
                'timestamp': timestamp
            })
    
    def run(self):
        """运行仪表盘"""
        print(f"🚀 启动空地海地面站智能数显系统...")
        print(f"📊 仪表盘地址: http://{self.host}:{self.port}")
        print(f"🌐 局域网访问: http://[树莓派IP]:{self.port}")
        print("=" * 50)
        
        # 运行Flask应用
        self.socketio.run(self.app, 
                         host=self.host, 
                         port=self.port, 
                         debug=False, 
                         allow_unsafe_werkzeug=True,
                         use_reloader=False)