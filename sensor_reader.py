#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
传感器数据读取模块
支持虚拟数据和真实传感器数据采集
"""

import random
import time
from datetime import datetime
from typing import Dict, List


class SensorReader:
    """传感器数据读取器"""
    
    def __init__(self, sensor_types: List[str], use_real_sensors: bool = False):
        """
        初始化传感器读取器
        
        Args:
            sensor_types: 传感器类型列表
            use_real_sensors: 是否使用真实传感器(默认False使用虚拟数据)
        """
        self.sensor_types = sensor_types
        self.use_real_sensors = use_real_sensors
        
        print(f"初始化传感器读取器:")
        print(f"  传感器类型: {', '.join(sensor_types)}")
        print(f"  模式: {'真实传感器' if use_real_sensors else '虚拟数据'}")
        
        # 如果使用真实传感器,初始化硬件
        if use_real_sensors:
            self._init_real_sensors()
    
    def _init_real_sensors(self):
        """初始化真实传感器硬件(示例代码)"""
        try:
            # ========== DHT22 温湿度传感器示例 ==========
            # import Adafruit_DHT
            # self.dht_sensor = Adafruit_DHT.DHT22
            # self.dht_pin = 4  # GPIO4
            # print("  ✓ DHT22传感器初始化成功")
            
            # ========== BMP280 气压传感器示例 ==========
            # import board
            # import adafruit_bmp280
            # i2c = board.I2C()
            # self.bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
            # print("  ✓ BMP280传感器初始化成功")
            
            # ========== 光照传感器示例 ==========
            # import RPi.GPIO as GPIO
            # self.light_pin = 17
            # GPIO.setmode(GPIO.BCM)
            # GPIO.setup(self.light_pin, GPIO.IN)
            # print("  ✓ 光照传感器初始化成功")
            
            pass
            
        except Exception as e:
            print(f"  ✗ 真实传感器初始化失败: {str(e)}")
            print("  → 将使用虚拟数据")
            self.use_real_sensors = False
    
    # ========================================
    # 虚拟传感器数据生成
    # ========================================
    
    def read_temperature_virtual(self) -> float:
        """
        读取虚拟温度数据
        模拟范围: 15-35°C
        """
        # 生成带有轻微波动的温度值
        base_temp = 25.0
        variation = random.uniform(-5, 5)
        temperature = round(base_temp + variation, 2)
        return temperature
    
    def read_humidity_virtual(self) -> float:
        """
        读取虚拟湿度数据
        模拟范围: 30-80%
        """
        base_humidity = 55.0
        variation = random.uniform(-15, 15)
        humidity = round(base_humidity + variation, 2)
        return humidity
    
    def read_pressure_virtual(self) -> float:
        """
        读取虚拟气压数据
        模拟范围: 990-1030 hPa
        """
        base_pressure = 1013.25
        variation = random.uniform(-15, 15)
        pressure = round(base_pressure + variation, 2)
        return pressure
    
    def read_light_virtual(self) -> int:
        """
        读取虚拟光照强度
        模拟范围: 0-1000 lux
        """
        light = random.randint(0, 1000)
        return light
    
    # ========================================
    # 真实传感器数据读取(示例代码)
    # ========================================
    
    def read_temperature_real(self) -> float:
        """读取真实温度数据(DHT22示例)"""
        try:
            # import Adafruit_DHT
            # humidity, temperature = Adafruit_DHT.read_retry(self.dht_sensor, self.dht_pin)
            # if temperature is not None:
            #     return round(temperature, 2)
            # else:
            #     print("  ⚠️  温度读取失败,使用虚拟数据")
            #     return self.read_temperature_virtual()
            
            # 暂时返回虚拟数据
            return self.read_temperature_virtual()
            
        except Exception as e:
            print(f"  ⚠️  温度传感器错误: {str(e)}")
            return self.read_temperature_virtual()
    
    def read_humidity_real(self) -> float:
        """读取真实湿度数据(DHT22示例)"""
        try:
            # import Adafruit_DHT
            # humidity, temperature = Adafruit_DHT.read_retry(self.dht_sensor, self.dht_pin)
            # if humidity is not None:
            #     return round(humidity, 2)
            # else:
            #     print("  ⚠️  湿度读取失败,使用虚拟数据")
            #     return self.read_humidity_virtual()
            
            # 暂时返回虚拟数据
            return self.read_humidity_virtual()
            
        except Exception as e:
            print(f"  ⚠️  湿度传感器错误: {str(e)}")
            return self.read_humidity_virtual()
    
    def read_pressure_real(self) -> float:
        """读取真实气压数据(BMP280示例)"""
        try:
            # pressure = self.bmp280.pressure
            # return round(pressure, 2)
            
            # 暂时返回虚拟数据
            return self.read_pressure_virtual()
            
        except Exception as e:
            print(f"  ⚠️  气压传感器错误: {str(e)}")
            return self.read_pressure_virtual()
    
    def read_light_real(self) -> int:
        """读取真实光照强度"""
        try:
            # import RPi.GPIO as GPIO
            # light_detected = GPIO.input(self.light_pin)
            # # 转换为lux值(需要根据实际传感器调整)
            # return 1000 if light_detected else 0
            
            # 暂时返回虚拟数据
            return self.read_light_virtual()
            
        except Exception as e:
            print(f"  ⚠️  光照传感器错误: {str(e)}")
            return self.read_light_virtual()
    
    # ========================================
    # 统一读取接口
    # ========================================
    
    def read_temperature(self) -> float:
        """读取温度(自动选择真实或虚拟)"""
        if self.use_real_sensors:
            return self.read_temperature_real()
        else:
            return self.read_temperature_virtual()
    
    def read_humidity(self) -> float:
        """读取湿度(自动选择真实或虚拟)"""
        if self.use_real_sensors:
            return self.read_humidity_real()
        else:
            return self.read_humidity_virtual()
    
    def read_pressure(self) -> float:
        """读取气压(自动选择真实或虚拟)"""
        if self.use_real_sensors:
            return self.read_pressure_real()
        else:
            return self.read_pressure_virtual()
    
    def read_light(self) -> int:
        """读取光照(自动选择真实或虚拟)"""
        if self.use_real_sensors:
            return self.read_light_real()
        else:
            return self.read_light_virtual()
    
    # ========================================
    # 读取所有传感器
    # ========================================
    
    def read_all_sensors(self) -> Dict:
        """
        读取所有已配置的传感器数据
        
        Returns:
            包含所有传感器数据的字典
        """
        data = {
            'timestamp': datetime.now().isoformat(),
            'sensors': {}
        }
        
        # 根据配置读取对应的传感器
        for sensor_type in self.sensor_types:
            try:
                if sensor_type == 'temperature':
                    value = self.read_temperature()
                    data['sensors']['temperature'] = {
                        'value': value,
                        'unit': '°C'
                    }
                    
                elif sensor_type == 'humidity':
                    value = self.read_humidity()
                    data['sensors']['humidity'] = {
                        'value': value,
                        'unit': '%'
                    }
                    
                elif sensor_type == 'pressure':
                    value = self.read_pressure()
                    data['sensors']['pressure'] = {
                        'value': value,
                        'unit': 'hPa'
                    }
                    
                elif sensor_type == 'light':
                    value = self.read_light()
                    data['sensors']['light'] = {
                        'value': value,
                        'unit': 'lux'
                    }
                    
            except Exception as e:
                print(f"  ⚠️  读取 {sensor_type} 失败: {str(e)}")
        
        return data


# ============================================
# 测试代码
# ============================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("传感器读取器测试")
    print("=" * 60 + "\n")
    
    # 创建传感器读取器
    sensor_types = ['temperature', 'humidity', 'pressure', 'light']
    reader = SensorReader(sensor_types, use_real_sensors=False)
    
    print("\n开始读取传感器数据...\n")
    
    # 读取3次数据
    for i in range(3):
        print(f"第 {i+1} 次读取:")
        print("-" * 60)
        
        data = reader.read_all_sensors()
        
        print(f"时间戳: {data['timestamp']}")
        print("传感器数据:")
        for sensor_name, sensor_data in data['sensors'].items():
            print(f"  {sensor_name:12s}: {sensor_data['value']:8} {sensor_data['unit']}")
        
        print()
        
        if i < 2:  # 最后一次不等待
            time.sleep(2)
    
    print("=" * 60)
    print("测试完成!")
    print("=" * 60)