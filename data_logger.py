#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据日志记录模块
记录传感器数据和系统运行日志
"""

import logging
import json
import os
import time  # 需要导入 time 模块
from datetime import datetime
from typing import Dict


class DataLogger:
    """数据日志记录器"""
    
    def __init__(self, config):
        """
        初始化数据日志记录器
        
        Args:
            config: 配置模块(import config)
        """
        self.log_file = config.LOG_FILE
        self.log_level = getattr(logging, config.LOG_LEVEL)
        self.log_format = config.LOG_FORMAT
        
        # 数据备份目录
        self.data_backup_dir = "data_backup"
        if not os.path.exists(self.data_backup_dir):
            os.makedirs(self.data_backup_dir)
        
        # 最后上传成功的时间戳
        self.last_successful_upload = None
        
        # 配置日志系统
        self._setup_logging()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("数据日志记录器初始化完成")
    
    def _setup_logging(self):
        """配置日志系统"""
        # 创建日志格式器
        formatter = logging.Formatter(self.log_format)
        
        # 文件处理器
        file_handler = logging.FileHandler(
            self.log_file,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        
        # 配置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    def log_sensor_data(self, data: Dict, upload_success: bool = False):
        """
        记录传感器数据
        
        Args:
            data: 传感器数据
            upload_success: 是否上传成功
        """
        logger = logging.getLogger(__name__)
        
        # 记录时间戳
        timestamp = data.get('timestamp', datetime.now().isoformat())
        logger.info(f"采集时间: {timestamp}")
        
        # 记录传感器数据
        sensors = data.get('sensors', {})
        for sensor_name, sensor_info in sensors.items():
            value = sensor_info.get('value')
            unit = sensor_info.get('unit')
            logger.info(f"  {sensor_name}: {value} {unit}")
        
        # 记录上传状态
        if upload_success:
            logger.info("  上传状态: ✓ 成功")
        else:
            logger.warning("  上传状态: ✗ 失败")
    
    def backup_data(self, data: Dict):
        """
        备份传感器数据到本地文件
        
        Args:
            data: 传感器数据
        """
        try:
            # 按日期创建文件
            date_str = datetime.now().strftime('%Y-%m-%d')
            backup_file = os.path.join(
                self.data_backup_dir,
                f"{date_str}.jsonl"
            )
            
            # 追加写入JSONL格式
            with open(backup_file, 'a', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
                f.write('\n')
            
            self.logger.debug(f"数据已备份到: {backup_file}")
            
        except Exception as e:
            self.logger.error(f"数据备份失败: {str(e)}")
    
    def mark_upload_success(self, timestamp=None):
        """标记数据上传成功"""
        if not timestamp:
            timestamp = int(time.time())
        
        # 更新最后上传成功的记录
        self.last_successful_upload = timestamp
        
        # 可以在这里添加更多逻辑，比如更新日志文件等
        self.logger.info(f"✓ 数据上传成功已标记 (TS: {timestamp})")
    
    def log_error(self, error_msg: str, exception: Exception = None):
        """
        记录错误信息
        
        Args:
            error_msg: 错误消息
            exception: 异常对象(可选)
        """
        logger = logging.getLogger(__name__)
        
        if exception:
            logger.error(f"{error_msg}: {str(exception)}")
        else:
            logger.error(error_msg)
    
    def log_system_info(self, info: Dict):
        """
        记录系统信息
        
        Args:
            info: 系统信息字典
        """
        logger = logging.getLogger(__name__)
        logger.info("系统信息:")
        
        for key, value in info.items():
            logger.info(f"  {key}: {value}")
    
    def get_log_stats(self) -> Dict:
        """
        获取日志统计信息
        
        Returns:
            日志统计字典
        """
        stats = {
            'log_file': self.log_file,
            'log_exists': os.path.exists(self.log_file),
            'backup_dir': self.data_backup_dir,
            'backup_count': 0,
            'last_successful_upload': self.last_successful_upload
        }
        
        # 统计日志文件大小
        if stats['log_exists']:
            stats['log_size'] = os.path.getsize(self.log_file)
            stats['log_size_mb'] = round(stats['log_size'] / 1024 / 1024, 2)
        
        # 统计备份文件数量
        if os.path.exists(self.data_backup_dir):
            backup_files = [f for f in os.listdir(self.data_backup_dir) if f.endswith('.jsonl')]
            stats['backup_count'] = len(backup_files)
            stats['backup_files'] = backup_files
        
        return stats
    

# ============================================
# 测试代码
# ============================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("数据日志记录器测试")
    print("=" * 60 + "\n")
    
    # 创建模拟配置
    class MockConfig:
        LOG_FILE = "test_sensor.log"
        LOG_LEVEL = "INFO"
        LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 创建日志记录器
    data_logger = DataLogger(MockConfig())
    
    # 测试记录传感器数据
    print("测试1: 记录传感器数据")
    print("-" * 60)
    test_data = {
        'timestamp': '2024-01-01T12:00:00',
        'sensors': {
            'temperature': {'value': 25.5, 'unit': '°C'},
            'humidity': {'value': 60.2, 'unit': '%'}
        }
    }
    data_logger.log_sensor_data(test_data, upload_success=True)
    
    # 测试备份数据
    print("\n测试2: 备份数据到本地")
    print("-" * 60)
    data_logger.backup_data(test_data)
    print("✓ 数据已备份")
    
    # 测试标记上传成功
    print("\n测试3: 标记上传成功")
    print("-" * 60)
    data_logger.mark_upload_success(int(time.time()))
    
    # 测试记录错误
    print("\n测试4: 记录错误信息")
    print("-" * 60)
    data_logger.log_error("这是一个测试错误")
    
    # 测试系统信息
    print("\n测试5: 记录系统信息")
    print("-" * 60)
    system_info = {
        'Python版本': '3.9.2',
        '操作系统': 'Raspbian GNU/Linux 11',
        '主机名': 'raspberrypi'
    }
    data_logger.log_system_info(system_info)
    
    # 获取日志统计
    print("\n测试6: 日志统计信息")
    print("-" * 60)
    stats = data_logger.get_log_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)