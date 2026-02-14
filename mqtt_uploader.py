#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MQTT数据上传模块
通过MQTT协议将传感器数据上传到服务器
"""

import paho.mqtt.client as mqtt
import json
import time
from typing import Dict
import logging


class MQTTUploader:
    """MQTT数据上传器"""
    
    def __init__(self, config):
        """
        初始化MQTT上传器
        
        Args:
            config: 配置模块(import config)
        """
        self.host = config.SERVER_HOST
        self.port = config.MQTT_PORT
        self.topic = config.MQTT_TOPIC
        self.qos = config.MQTT_QOS
        self.retain = config.MQTT_RETAIN
        self.keepalive = config.MQTT_KEEPALIVE
        self.device_id = config.DEVICE_ID
        self.api_key = config.API_KEY
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 创建MQTT客户端
        self.client = mqtt.Client(
            client_id=self.device_id,
            clean_session=True
        )
        
        # 设置用户名和密码
        self.client.username_pw_set(
            username=self.device_id,
            password=self.api_key
        )
        
        # 设置回调函数
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        
        # 连接状态
        self.connected = False
        self.connect_time = None
        
        print(f"MQTT上传器初始化:")
        print(f"  服务器: {self.host}:{self.port}")
        print(f"  主题: {self.topic}")
        print(f"  QoS: {self.qos}")
        print(f"  设备ID: {self.device_id}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT连接成功回调"""
        if rc == 0:
            self.connected = True
            self.connect_time = time.time()
            self.logger.info(f"✓ 已连接到MQTT服务器: {self.host}:{self.port}")
        else:
            self.connected = False
            error_messages = {
                1: "协议版本不正确",
                2: "无效的客户端标识符",
                3: "服务器不可用",
                4: "错误的用户名或密码",
                5: "未授权"
            }
            error_msg = error_messages.get(rc, f"未知错误 (代码: {rc})")
            self.logger.error(f"✗ MQTT连接失败: {error_msg}")
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT断开连接回调"""
        self.connected = False
        
        if rc != 0:
            self.logger.warning(f"✗ 意外断开连接 (代码: {rc})")
            self.logger.info("将尝试重新连接...")
    
    def _on_publish(self, client, userdata, mid):
        """MQTT消息发布成功回调"""
        self.logger.debug(f"消息已发布 (消息ID: {mid})")
    
    def connect(self, timeout: int = 10) -> bool:
        """
        连接到MQTT服务器
        
        Args:
            timeout: 连接超时时间(秒)
            
        Returns:
            连接是否成功
        """
        try:
            self.logger.info(f"正在连接到MQTT服务器 {self.host}:{self.port}...")
            
            # 连接服务器
            self.client.connect(self.host, self.port, self.keepalive)
            
            # 启动网络循环
            self.client.loop_start()
            
            # 等待连接建立
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.connected:
                return True
            else:
                self.logger.error("连接超时")
                return False
                
        except Exception as e:
            self.logger.error(f"连接失败: {str(e)}")
            return False
    
    def disconnect(self):
        """断开MQTT连接"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            self.logger.info("已断开MQTT连接")
        except Exception as e:
            self.logger.error(f"断开连接时出错: {str(e)}")
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self.connected
    
    def reconnect(self, timeout: int = 10) -> bool:
        """
        重新连接到MQTT服务器
        
        Args:
            timeout: 连接超时时间(秒)
            
        Returns:
            重连是否成功
        """
        self.logger.info("尝试重新连接...")
        
        try:
            # 先断开
            self.disconnect()
            time.sleep(1)
            
            # 再连接
            return self.connect(timeout)
            
        except Exception as e:
            self.logger.error(f"重连失败: {str(e)}")
            return False
    
    def upload(self, sensor_data: Dict) -> bool:
        """
        上传传感器数据
        
        Args:
            sensor_data: 传感器数据字典
            
        Returns:
            上传是否成功
        """
        # 检查连接状态
        if not self.connected:
            self.logger.warning("未连接到MQTT服务器,尝试重连...")
            if not self.reconnect():
                self.logger.error("✗ 重连失败,数据上传失败")
                return False
        
        try:
            # 构建消息负载
            payload = {
                'device_id': self.device_id,
                'data': sensor_data
            }
            
            # 转换为JSON字符串
            message = json.dumps(payload, ensure_ascii=False)
            
            # 发布消息
            result = self.client.publish(
                topic=self.topic,
                payload=message,
                qos=self.qos,
                retain=self.retain
            )
            
            # 检查发布结果
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.info(f"✓ 数据已发布到主题: {self.topic}")
                
                # 等待消息发送完成(仅对QoS>0有效)
                if self.qos > 0:
                    result.wait_for_publish(timeout=5)
                
                return True
            else:
                self.logger.error(f"✗ 发布失败,错误码: {result.rc}")
                return False
                
        except Exception as e:
            self.logger.error(f"✗ 上传出错: {str(e)}")
            return False
    
    def get_connection_info(self) -> Dict:
        """
        获取连接信息
        
        Returns:
            连接信息字典
        """
        info = {
            'connected': self.connected,
            'host': self.host,
            'port': self.port,
            'topic': self.topic,
            'qos': self.qos
        }
        
        if self.connected and self.connect_time:
            info['uptime'] = int(time.time() - self.connect_time)
        
        return info


# ============================================
# 测试代码
# ============================================

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "=" * 60)
    print("MQTT上传器测试")
    print("=" * 60 + "\n")
    
    # 创建模拟配置
    class MockConfig:
        SERVER_HOST = "localhost"
        MQTT_PORT = 1883
        MQTT_TOPIC = "sensor/data"
        MQTT_QOS = 1
        MQTT_RETAIN = False
        MQTT_KEEPALIVE = 60
        API_KEY = "test-api-key"
        DEVICE_ID = "test-device-001"
    
    # 创建上传器
    uploader = MQTTUploader(MockConfig())
    
    # 测试连接
    print("\n测试1: 连接到MQTT服务器")
    print("-" * 60)
    if uploader.connect():
        print("✓ 连接成功!")
        
        # 测试数据上传
        print("\n测试2: 上传数据")
        print("-" * 60)
        test_data = {
            'timestamp': '2024-01-01T12:00:00',
            'sensors': {
                'temperature': {'value': 25.5, 'unit': '°C'},
                'humidity': {'value': 60.2, 'unit': '%'}
            }
        }
        
        result = uploader.upload(test_data)
        
        if result:
            print("✓ 数据上传成功!")
        else:
            print("✗ 数据上传失败!")
        
        # 等待消息发送完成
        time.sleep(2)
        
        # 获取连接信息
        print("\n测试3: 连接信息")
        print("-" * 60)
        info = uploader.get_connection_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        # 断开连接
        uploader.disconnect()
    else:
        print("✗ 连接失败!")
        print("\n提示:")
        print("  1. 请确保MQTT Broker正在运行")
        print("  2. 安装mosquitto: sudo apt install mosquitto -y")
        print("  3. 启动mosquitto: sudo systemctl start mosquitto")
    
    print("\n" + "=" * 60)
