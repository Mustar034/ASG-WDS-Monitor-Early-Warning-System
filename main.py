#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空地海地面站智能数显系统 - 主程序
负责协调各个模块,实现定时采集、上传和可视化显示功能
"""

import time
import signal
import sys
import logging
import webbrowser
import threading
import os
import subprocess

# 导入自定义模块
import config
from sensor_reader import SensorReader
from http_uploader import HTTPUploader
from data_logger import DataLogger

# 导入Dashboard
try:
    from dashboard.app import Dashboard
    HAS_DASHBOARD = True
except ImportError as e:
    HAS_DASHBOARD = False
    print(f"⚠️  Dashboard模块导入失败: {str(e)}")
    print("⚠️  可视化功能将不可用，但数据采集和上传仍可正常工作")

# 导入显示模块
try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

try:
    from PyQt5.QtWidgets import QApplication
    HAS_PYQT = True
except ImportError:
    HAS_PYQT = False

# 添加Tkinter导入检测 - 确保这部分存在
try:
    import tkinter
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False

class SensorSystem:
    """传感器数据采集系统"""
    
    def __init__(self):
        """初始化系统"""
        print("\n" + "=" * 60)
        print("  空地海地面站智能数显系统")
        print("=" * 60 + "\n")
        
        # 验证配置
        is_valid, errors = config.validate_config()
        if not is_valid:
            print("✗ 配置验证失败:\n")
            for error in errors:
                print(f"  {error}")
            print("\n请修改 config.py 后重试。\n")
            sys.exit(1)
        
        # 打印配置
        config.print_config()
        print()
        
        # 初始化日志记录器
        self.data_logger = DataLogger(config)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("系统正在初始化...")
        
        # 初始化传感器读取器
        self.sensor_reader = SensorReader(
            sensor_types=config.SENSOR_TYPES,
            use_real_sensors=config.USE_REAL_SENSORS
        )
        
        # 初始化数据上传器
        self.uploader = None
        self._init_uploader()
        
        # 设置数据记录器引用
        if hasattr(self.uploader, 'set_data_logger'):
            self.uploader.set_data_logger(self.data_logger)
        
        # 初始化Dashboard
        self.dashboard = None
        if HAS_DASHBOARD and config.DISPLAY_MODE != 'none':
            self._init_dashboard()
        
        # 采集间隔
        self.interval = config.COLLECT_INTERVAL
        
        # 运行状态
        self.running = False
        
        # 统计信息
        self.stats = {
            'total_collections': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'start_time': None
        }
        
        self.logger.info("系统初始化完成!\n")
    
    def _init_uploader(self):
        """初始化数据上传器"""
        upload_method = config.UPLOAD_METHOD.lower()
        
        if upload_method == 'http':
            self.logger.info("使用HTTP上传方式")
            self.uploader = HTTPUploader(config)
            
        elif upload_method == 'mqtt':
            self.logger.info("使用MQTT上传方式")
            # 延迟导入MQTTUploader，避免在不使用时导入
            try:
                from mqtt_uploader import MQTTUploader
                self.uploader = MQTTUploader(config)
            except ImportError:
                self.logger.error("MQTT上传器需要安装 paho-mqtt 库")
                self.logger.error("请运行: pip install paho-mqtt")
                sys.exit(1)
            
            # MQTT需要先连接
            self.logger.info("正在连接到MQTT服务器...")
            if not self.uploader.connect():
                self.logger.error("无法连接到MQTT服务器,请检查配置")
                sys.exit(1)
            self.logger.info("MQTT连接成功!")
            
        else:
            self.logger.error(f"不支持的上传方式: {upload_method}")
            sys.exit(1)
    
    def _init_dashboard(self):
        """初始化可视化仪表盘"""
        try:
            self.logger.info("正在启动可视化仪表盘...")
            self.dashboard = Dashboard(
                host='0.0.0.0', 
                port=config.DASHBOARD_PORT
            )
            
            # 在后台线程中启动Dashboard
            dashboard_thread = threading.Thread(
                target=self.dashboard.run,
                daemon=True
            )
            dashboard_thread.start()
            
            # 等待Dashboard启动
            time.sleep(2)
            
            # 根据配置选择显示方式
            display_mode = config.DISPLAY_MODE
            
            if display_mode == 'browser':
                self._open_kiosk_browser()
            elif display_mode == 'pygame' and HAS_PYGAME:
                self._start_pygame_display()
            elif display_mode == 'pyqt' and HAS_PYQT:
                self._start_pyqt_display()
            elif display_mode == 'tkinter' and HAS_TKINTER:
                self._start_tkinter_display()
            else:
                self.logger.info(f"显示模式: {display_mode}，请手动访问: http://localhost:{config.DASHBOARD_PORT}")
            
            self.logger.info("✓ 可视化仪表盘启动完成")
            
        except Exception as e:
            self.logger.error(f"仪表盘启动失败: {str(e)}")
            self.dashboard = None
    
    def _open_kiosk_browser(self):
        """打开Kiosk模式浏览器"""
        try:
            # 关闭可能已经存在的chromium实例
            subprocess.run(['pkill', 'chromium'], stderr=subprocess.DEVNULL)
            subprocess.run(['pkill', 'chrome'], stderr=subprocess.DEVNULL)
            time.sleep(1)
            
            # 检查浏览器是否可用
            browsers = ['chromium-browser', 'chromium', 'chrome']
            browser_cmd = None
            
            for browser in browsers:
                try:
                    subprocess.run(['which', browser], check=True, 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    browser_cmd = browser
                    break
                except:
                    continue
            
            if not browser_cmd:
                self.logger.warning("未找到浏览器，无法自动打开仪表盘")
                self.logger.info(f"请手动访问: http://localhost:{config.DASHBOARD_PORT}")
                return
            
            # 启动浏览器，全屏无边框
            cmd = [
                browser_cmd,
                '--noerrdialogs',
                '--disable-infobars',
                '--kiosk',
                '--incognito',
                f'http://localhost:{config.DASHBOARD_PORT}'
            ]
            
            # 在后台运行浏览器
            subprocess.Popen(cmd, 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL,
                           start_new_session=True)
            
            self.logger.info(f"✓ 已启动 {browser_cmd} 全屏显示仪表盘")
            
            # 隐藏鼠标光标（需要unclutter）
            try:
                subprocess.Popen(['unclutter', '-idle', '0.5'], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL,
                               start_new_session=True)
            except:
                pass  # unclutter不可用也没关系
            
        except Exception as e:
            self.logger.error(f"无法启动全屏浏览器: {str(e)}")
            self.logger.info(f"请手动访问: http://localhost:{config.DASHBOARD_PORT}")
    
    def _start_pygame_display(self):
        """启动Pygame显示窗口"""
        try:
            # 创建Pygame显示脚本
            pygame_script = """
import pygame
import requests
import json
import time
import threading

class PygameDisplay:
    def __init__(self, width=800, height=480):
        self.width = width
        self.height = height
        self.running = True
        self.data = {}
        
        # Pygame初始化
        pygame.init()
        pygame.display.set_caption("空地海地面站")
        
        # 创建窗口
        self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        
        # 字体
        self.title_font = pygame.font.SysFont(None, 48)
        self.value_font = pygame.font.SysFont(None, 72)
        self.label_font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # 颜色
        self.colors = {
            'background': (10, 14, 42),
            'title': (0, 188, 212),
            'value': (255, 255, 255),
            'label': (170, 170, 170),
            'temp': (0, 188, 212),
            'humidity': (76, 175, 80),
            'pressure': (255, 152, 0),
            'light': (33, 150, 243),
            'border': (50, 50, 70)
        }
        
        # 启动数据获取线程
        self.data_thread = threading.Thread(target=self.fetch_data_loop, daemon=True)
        self.data_thread.start()
    
    def fetch_data(self):
        try:
            response = requests.get("http://localhost:%d/api/data" % %d, timeout=2)
            if response.status_code == 200:
                self.data = response.json()
                return True
        except:
            pass
        return False
    
    def fetch_data_loop(self):
        while self.running:
            self.fetch_data()
            time.sleep(2)
    
    def draw(self):
        # 清屏
        self.screen.fill(self.colors['background'])
        
        # 绘制标题
        title = self.title_font.render("空地海地面站智能数显系统", True, self.colors['title'])
        self.screen.blit(title, (self.width//2 - title.get_width()//2, 20))
        
        # 绘制数据
        self.draw_data()
        
        # 更新时间
        time_str = time.strftime("%Y-%m-%d %H:%M:%S")
        time_text = self.small_font.render(f"更新时间: {time_str}", True, self.colors['label'])
        self.screen.blit(time_text, (20, self.height - 40))
        
        # 刷新显示
        pygame.display.flip()
    
    def draw_data(self):
        usv = self.data.get('usv', {})
        scores = self.data.get('scores', {})
        
        # 四列布局
        col_width = self.width // 4
        col_height = self.height - 120
        
        # 温度
        self.draw_data_card(0, col_width, "温度", f"{usv.get('temp', '--'):.1f}", "°C", 
                          self.colors['temp'], 0, 100)
        
        # 湿度
        self.draw_data_card(col_width, col_width, "湿度", f"{usv.get('humidity', '--'):.1f}", "%", 
                          self.colors['humidity'], 0, 100)
        
        # 气压
        self.draw_data_card(col_width*2, col_width, "气压", f"{usv.get('pressure', '--'):.1f}", "hPa", 
                          self.colors['pressure'], 950, 1050)
        
        # 光照
        self.draw_data_card(col_width*3, col_width, "光照", f"{usv.get('light', '--'):.0f}", "lux", 
                          self.colors['light'], 0, 2000)
        
        # 底部评分
        y_bottom = self.height - 100
        water_score = scores.get('water_quality', 0)
        dam_score = scores.get('dam_safety', 0)
        
        # 水质评分
        water_text = self.small_font.render(f"水质评分: {water_score:.1f}%", True, self.colors['temp'])
        self.screen.blit(water_text, (col_width - water_text.get_width()//2, y_bottom))
        
        # 大坝安全评分
        dam_text = self.small_font.render(f"大坝安全: {dam_score:.1f}%", True, self.colors['humidity'])
        self.screen.blit(dam_text, (col_width*3 - dam_text.get_width()//2, y_bottom))
    
    def draw_data_card(self, x, width, label, value, unit, color, min_val, max_val):
        # 卡片背景
        card_rect = pygame.Rect(x + 10, 100, width - 20, self.height - 200)
        pygame.draw.rect(self.screen, (20, 24, 52), card_rect, border_radius=15)
        pygame.draw.rect(self.screen, self.colors['border'], card_rect, 2, border_radius=15)
        
        # 标签
        label_text = self.label_font.render(label, True, self.colors['label'])
        self.screen.blit(label_text, (x + width//2 - label_text.get_width()//2, 120))
        
        # 数值
        value_text = self.value_font.render(value, True, color)
        self.screen.blit(value_text, (x + width//2 - value_text.get_width()//2, 170))
        
        # 单位
        unit_text = self.label_font.render(unit, True, self.colors['label'])
        self.screen.blit(unit_text, (x + width//2 - unit_text.get_width()//2, 250))
        
        # 进度条背景
        bar_y = 300
        bar_width = width - 40
        bar_height = 20
        bar_x = x + 20
        
        pygame.draw.rect(self.screen, (50, 50, 70), 
                        (bar_x, bar_y, bar_width, bar_height), border_radius=10)
        
        # 进度条前景
        try:
            val = float(value) if value != '--' else 0
            percent = (val - min_val) / (max_val - min_val)
            percent = max(0, min(1, percent))
            fill_width = int(bar_width * percent)
            
            pygame.draw.rect(self.screen, color, 
                            (bar_x, bar_y, fill_width, bar_height), border_radius=10)
        except:
            pass
        
        # 刻度标签
        min_text = self.small_font.render(str(min_val), True, self.colors['label'])
        max_text = self.small_font.render(str(max_val), True, self.colors['label'])
        self.screen.blit(min_text, (bar_x, bar_y + 25))
        self.screen.blit(max_text, (bar_x + bar_width - max_text.get_width(), bar_y + 25))
    
    def run(self):
        print("Pygame显示启动，按ESC键退出")
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            self.draw()
            self.clock.tick(30)
        
        pygame.quit()

if __name__ == "__main__":
    display = PygameDisplay(%d, %d)
    display.run()
""" % (config.DASHBOARD_PORT, config.DASHBOARD_PORT, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT)
            
            # 写入临时文件
            temp_file = "/tmp/pygame_display.py"
            with open(temp_file, "w") as f:
                f.write(pygame_script)
            
            # 在子进程中运行
            subprocess.Popen(
                [sys.executable, temp_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            self.logger.info("✓ 已启动Pygame全屏显示")
            
        except Exception as e:
            self.logger.error(f"启动Pygame显示失败: {str(e)}")
            # 回退到浏览器模式
            self._open_kiosk_browser()
    def _start_tkinter_display(self):
        """启动Tkinter显示窗口"""
        try:
            # 检查display_tkinter.py文件是否存在
            display_script = os.path.join(os.path.dirname(__file__), "display_tkinter.py")
            
            if not os.path.exists(display_script):
                self.logger.error("display_tkinter.py 文件不存在")
                self.logger.info(f"当前目录: {os.path.dirname(__file__)}")
                # 回退到浏览器模式
                self._open_kiosk_browser()
                return
            
            self.logger.info(f"找到Tkinter显示脚本: {display_script}")
            
            # 在子进程中运行display_tkinter.py
            cmd = [
                sys.executable,
                display_script,
                f"--url=http://localhost:{config.DASHBOARD_PORT}",
                f"--width={config.DISPLAY_WIDTH}",
                f"--height={config.DISPLAY_HEIGHT}",
                f"--fullscreen={str(config.FULLSCREEN).lower()}"
            ]
            
            self.logger.info(f"启动命令: {' '.join(cmd)}")
            
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            # 等待一下确保窗口启动
            time.sleep(2)
            
            self.logger.info(f"✓ 已启动Tkinter显示 ({config.DISPLAY_WIDTH}x{config.DISPLAY_HEIGHT})")
            
        except Exception as e:
            self.logger.error(f"启动Tkinter显示失败: {str(e)}")
            # 回退到浏览器模式
            self._open_kiosk_browser()
    def collect_and_upload(self):
        """采集一次数据并上传"""
        try:
            # 更新统计
            self.stats['total_collections'] += 1
            
            # 读取传感器数据
            self.logger.info(f"[{self.stats['total_collections']}] 开始采集传感器数据...")
            sensor_data = self.sensor_reader.read_all_sensors()
            
            # 上传数据到远程服务器
            self.logger.info("正在上传数据到服务器...")
            success = self.uploader.upload(sensor_data)
            
            # 更新Dashboard（如果启用）
            if self.dashboard:
                try:
                    self.dashboard.update_data(sensor_data)
                    if self.stats['total_collections'] % 10 == 0:  # 每10次记录一次
                        self.logger.info("✓ 数据已更新到本地仪表盘")
                except Exception as e:
                    self.logger.error(f"更新Dashboard失败: {str(e)}")
            
            # 记录传感器数据
            self.data_logger.log_sensor_data(sensor_data, upload_success=success)
            
            # 备份数据到本地
            self.data_logger.backup_data(sensor_data)
            
            # 更新统计
            if success:
                self.stats['successful_uploads'] += 1
                self.logger.info("✓ 本次采集与上传完成\n")
            else:
                self.stats['failed_uploads'] += 1
                self.logger.warning("✗ 数据上传失败\n")
            
            return success
            
        except KeyboardInterrupt:
            raise  # 向上传递中断信号
            
        except Exception as e:
            self.logger.error(f"采集或上传过程出错: {str(e)}")
            self.stats['failed_uploads'] += 1
            return False
    
    def print_stats(self):
        """打印统计信息"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("运行统计:")
        self.logger.info("=" * 60)
        self.logger.info(f"总采集次数: {self.stats['total_collections']}")
        self.logger.info(f"成功上传: {self.stats['successful_uploads']}")
        self.logger.info(f"上传失败: {self.stats['failed_uploads']}")
        
        if self.stats['total_collections'] > 0:
            success_rate = (self.stats['successful_uploads'] / self.stats['total_collections']) * 100
            self.logger.info(f"成功率: {success_rate:.1f}%")
        
        if self.stats['start_time']:
            runtime = time.time() - self.stats['start_time']
            hours = int(runtime // 3600)
            minutes = int((runtime % 3600) // 60)
            seconds = int(runtime % 60)
            self.logger.info(f"运行时长: {hours}小时 {minutes}分钟 {seconds}秒")
        
        self.logger.info("=" * 60 + "\n")
    
    def run(self):
        """运行主循环"""
        self.running = True
        self.stats['start_time'] = time.time()
        
        self.logger.info(f"开始定时采集,间隔: {self.interval} 秒")
        self.logger.info("按 Ctrl+C 停止程序\n")
        
        try:
            while self.running:
                # 采集并上传
                self.collect_and_upload()
                
                # 等待下一次采集
                if self.running:
                    self.logger.info(f"等待 {self.interval} 秒后进行下一次采集...")
                    time.sleep(self.interval)
                    
        except KeyboardInterrupt:
            self.logger.info("\n收到中断信号,正在停止...")
        
        finally:
            self.stop()
    
    def stop(self):
        """停止系统"""
        self.running = False
        
        # 打印统计信息
        self.print_stats()
        
        # 如果使用MQTT,断开连接
        if hasattr(self.uploader, 'disconnect'):
            self.uploader.disconnect()
        
        self.logger.info("系统已停止")
        self.logger.info("=" * 60 + "\n")


# ============================================
# 信号处理
# ============================================

sensor_system = None

def signal_handler(sig, frame):
    """处理系统信号"""
    global sensor_system
    print('\n收到终止信号...')
    if sensor_system:
        sensor_system.stop()
    sys.exit(0)


# ============================================
# 主函数
# ============================================

def main():
    """主函数"""
    global sensor_system
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 创建并运行系统
        sensor_system = SensorSystem()
        sensor_system.run()
        
    except Exception as e:
        print(f"\n✗ 系统启动失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()