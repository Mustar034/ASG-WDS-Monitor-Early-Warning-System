#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空地海地面站智能数显系统 - 现代化Tkinter版本
实现与HTML Dashboard一致的视觉效果
"""

import tkinter as tk
from tkinter import font, Canvas
import threading
import time
import requests
import json
from datetime import datetime
import math
import sys

class ModernDashboard:
    """现代化仪表盘界面"""
    
    def __init__(self, url="http://localhost:5002", width=800, height=600, fullscreen=False):
        self.url = url
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        self.running = True
        self.data = {}
        self.history_data = {
            'time': [],
            'temp': [],
            'humidity': [],
            'pressure': [],
            'light': []
        }
        self.max_history = 20
        self.collection_count = 0
        self.start_time = datetime.now()
        self.connected = False
        
        # 现代配色方案 - 深蓝渐变主题
        self.colors = {
            'bg_dark': '#0a0e2a',
            'bg_gradient_start': '#0a0e2a',
            'bg_gradient_end': '#1a237e',
            'primary': '#00bcd4',
            'secondary': '#ff4081',
            'success': '#4caf50',
            'warning': '#ff9800',
            'info': '#2196f3',
            'danger': '#f44336',
            'card_bg': '#1a1f3a',
            'card_border': '#2a3f5f',
            'text_primary': '#ffffff',
            'text_secondary': '#aaaaaa',
            'text_muted': '#666666',
            'progress_bg': '#2a2f4a',
        }
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("空地海地面站智能数显系统")
        
        if fullscreen:
            self.root.attributes('-fullscreen', True)
            self.width = self.root.winfo_screenwidth()
            self.height = self.root.winfo_screenheight()
        else:
            self.root.geometry(f"{width}x{height}")
        
        self.root.configure(bg=self.colors['bg_dark'])
        
        # 绑定快捷键
        self.root.bind('<Escape>', lambda e: self.quit())
        self.root.bind('<F5>', lambda e: self.fetch_data())
        self.root.bind('<f>', lambda e: self.toggle_fullscreen())
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        
        # 创建字体
        self.create_fonts()
        
        # 创建主画布
        self.canvas = Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg=self.colors['bg_dark'],
            highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True)
        
        # 绘制渐变背景
        self.draw_gradient_background()
        
        # 创建UI
        self.create_ui()
        
        # 启动数据更新线程
        self.data_thread = threading.Thread(target=self.update_data_loop, daemon=True)
        self.data_thread.start()
        
        # 启动动画
        self.animation_frame = 0
        self.animate()
        
        # 初始获取数据
        self.root.after(500, self.fetch_data)
    
    def create_fonts(self):
        """创建字体"""
        try:
            # 使用系统可用字体
            self.title_font = font.Font(family='DejaVu Sans', size=24, weight='bold')
            self.heading_font = font.Font(family='DejaVu Sans', size=16, weight='bold')
            self.value_font = font.Font(family='DejaVu Sans Mono', size=36, weight='bold')
            self.label_font = font.Font(family='DejaVu Sans', size=11)
            self.small_font = font.Font(family='DejaVu Sans', size=9)
            self.tiny_font = font.Font(family='DejaVu Sans', size=8)
        except:
            # 备选方案
            self.title_font = font.Font(size=24, weight='bold')
            self.heading_font = font.Font(size=16, weight='bold')
            self.value_font = font.Font(size=36, weight='bold')
            self.label_font = font.Font(size=11)
            self.small_font = font.Font(size=9)
            self.tiny_font = font.Font(size=8)
    
    def draw_gradient_background(self):
        """绘制渐变背景"""
        # 创建垂直渐变
        steps = 100
        for i in range(steps):
            y1 = int(self.height * i / steps)
            y2 = int(self.height * (i + 1) / steps)
            
            # 从深蓝到紫蓝的渐变
            ratio = i / steps
            r1, g1, b1 = self.hex_to_rgb(self.colors['bg_gradient_start'])
            r2, g2, b2 = self.hex_to_rgb(self.colors['bg_gradient_end'])
            
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            
            color = f'#{r:02x}{g:02x}{b:02x}'
            
            self.canvas.create_rectangle(
                0, y1, self.width, y2,
                fill=color, outline='',
                tags='gradient_bg'
            )
    
    def hex_to_rgb(self, hex_color):
        """十六进制转RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def create_ui(self):
        """创建用户界面"""
        # 导航栏
        self.create_navbar()
        
        # 主标题区域
        self.create_header()
        
        # 数据卡片
        self.create_data_cards()
        
        # 图表区域
        self.create_chart_area()
        
        # 底部信息
        self.create_footer_info()
    
    def create_navbar(self):
        """创建导航栏"""
        nav_height = 50
        
        # 导航栏背景
        self.canvas.create_rectangle(
            0, 0, self.width, nav_height,
            fill='#0a0e1a', outline='',
            tags='navbar'
        )
        
        # 底部边框
        self.canvas.create_line(
            0, nav_height, self.width, nav_height,
            fill=self.colors['primary'], width=1,
            tags='navbar'
        )
        
        # Logo和标题
        self.canvas.create_text(
            20, nav_height // 2,
            text='🛰️ 空地海地面站智能数显系统',
            anchor='w',
            font=self.heading_font,
            fill=self.colors['primary'],
            tags='navbar'
        )
        
        # 连接状态
        status_x = self.width - 150
        self.status_dot = self.canvas.create_oval(
            status_x - 5, nav_height // 2 - 5,
            status_x + 5, nav_height // 2 + 5,
            fill=self.colors['danger'],
            outline='',
            tags='status'
        )
        
        self.status_text = self.canvas.create_text(
            status_x + 15, nav_height // 2,
            text='未连接',
            anchor='w',
            font=self.small_font,
            fill=self.colors['text_secondary'],
            tags='status'
        )
        
        # 时间显示
        self.time_text = self.canvas.create_text(
            self.width - 20, nav_height // 2,
            text='',
            anchor='e',
            font=self.tiny_font,
            fill=self.colors['text_muted'],
            tags='time'
        )
    
    def create_header(self):
        """创建头部区域"""
        header_y = 70
        header_height = 100
        
        # 头部卡片背景
        self.draw_card(20, header_y, self.width - 40, header_height)
        
        # 主标题
        self.canvas.create_text(
            40, header_y + 30,
            text='🚀 空地海一体化智能监控平台',
            anchor='w',
            font=self.title_font,
            fill=self.colors['text_primary'],
            tags='header'
        )
        
        # 副标题
        self.canvas.create_text(
            40, header_y + 60,
            text='实时监控无人船(USV)、无人机(UAV)状态及环境数据',
            anchor='w',
            font=self.label_font,
            fill=self.colors['text_secondary'],
            tags='header'
        )
        
        # 状态徽章
        badge_x = self.width - 200
        self.draw_badge(badge_x, header_y + 25, 'UAV: 就绪', self.colors['info'])
        self.draw_badge(badge_x, header_y + 60, 'USV: 活动中', self.colors['success'])
    
    def draw_badge(self, x, y, text, color):
        """绘制状态徽章"""
        # 测量文本宽度
        temp_text = self.canvas.create_text(0, 0, text=text, font=self.small_font)
        bbox = self.canvas.bbox(temp_text)
        self.canvas.delete(temp_text)
        
        width = bbox[2] - bbox[0] + 20
        height = 25
        
        # 背景
        self.canvas.create_rectangle(
            x, y, x + width, y + height,
            fill=color, outline='',
            tags='badge'
        )
        
        # 文字
        self.canvas.create_text(
            x + width // 2, y + height // 2,
            text=text,
            font=self.small_font,
            fill='white',
            tags='badge'
        )
    
    def create_data_cards(self):
        """创建数据卡片"""
        cards_y = 190
        card_width = (self.width - 100) // 4
        card_height = 150
        gap = 20
        
        self.data_cards = {}
        
        cards_config = [
            {'key': 'temp', 'icon': '🌡️', 'label': '温度', 'unit': '°C', 
             'color': self.colors['info'], 'range': (0, 50)},
            {'key': 'humidity', 'icon': '💧', 'label': '湿度', 'unit': '%', 
             'color': self.colors['success'], 'range': (0, 100)},
            {'key': 'pressure', 'icon': '🌊', 'label': '气压', 'unit': 'hPa', 
             'color': self.colors['warning'], 'range': (950, 1050)},
            {'key': 'light', 'icon': '☀️', 'label': '光照强度', 'unit': 'lux', 
             'color': self.colors['primary'], 'range': (0, 2000)},
        ]
        
        for i, config in enumerate(cards_config):
            x = 20 + i * (card_width + gap)
            card = self.create_stat_card(x, cards_y, card_width, card_height, config)
            self.data_cards[config['key']] = card
    
    def create_stat_card(self, x, y, width, height, config):
        """创建统计卡片"""
        card = {'config': config}
        
        # 卡片背景
        card['bg'] = self.draw_card(x, y, width, height, border_color=config['color'])
        
        # 顶部颜色条
        self.canvas.create_rectangle(
            x, y, x + width, y + 3,
            fill=config['color'], outline='',
            tags='card_accent'
        )
        
        # 图标
        card['icon'] = self.canvas.create_text(
            x + width // 2, y + 30,
            text=config['icon'],
            font=('Arial', 28),
            tags='card_icon'
        )
        
        # 标签
        card['label'] = self.canvas.create_text(
            x + width // 2, y + 60,
            text=config['label'],
            font=self.small_font,
            fill=self.colors['text_secondary'],
            tags='card_label'
        )
        
        # 数值
        card['value'] = self.canvas.create_text(
            x + width // 2, y + 95,
            text='--',
            font=self.value_font,
            fill=config['color'],
            tags='card_value'
        )
        
        # 单位
        card['unit'] = self.canvas.create_text(
            x + width // 2, y + 125,
            text=config['unit'],
            font=self.tiny_font,
            fill=self.colors['text_muted'],
            tags='card_unit'
        )
        
        # 进度条
        bar_y = y + height - 15
        bar_padding = 10
        
        card['progress_bg'] = self.canvas.create_rectangle(
            x + bar_padding, bar_y,
            x + width - bar_padding, bar_y + 5,
            fill=self.colors['progress_bg'],
            outline='',
            tags='progress_bg'
        )
        
        card['progress'] = self.canvas.create_rectangle(
            x + bar_padding, bar_y,
            x + bar_padding, bar_y + 5,
            fill=config['color'],
            outline='',
            tags='progress'
        )
        
        card['bounds'] = (x, y, width, height)
        
        return card
    
    def draw_card(self, x, y, width, height, border_color=None):
        """绘制卡片"""
        # 阴影
        shadow_offset = 3
        self.canvas.create_rectangle(
            x + shadow_offset, y + shadow_offset,
            x + width + shadow_offset, y + height + shadow_offset,
            fill='#000000', outline='',
            tags='card_shadow'
        )
        
        # 主背景
        card_bg = self.canvas.create_rectangle(
            x, y, x + width, y + height,
            fill=self.colors['card_bg'],
            outline=border_color or self.colors['card_border'],
            width=1,
            tags='card'
        )
        
        return card_bg
    
    def create_chart_area(self):
        """创建图表区域"""
        chart_y = 360
        chart_width = (self.width - 60) * 2 // 3
        chart_height = 200
        
        # 主图表卡片
        self.draw_card(20, chart_y, chart_width, chart_height)
        
        # 图表标题
        self.canvas.create_text(
            40, chart_y + 20,
            text='📊 环境数据趋势',
            anchor='w',
            font=self.heading_font,
            fill=self.colors['text_primary'],
            tags='chart_title'
        )
        
        # 图表区域
        self.chart_area = {
            'x': 40,
            'y': chart_y + 50,
            'width': chart_width - 40,
            'height': chart_height - 70
        }
        
        # 绘制网格
        self.draw_chart_grid()
        
        # 评分卡片区域
        score_x = 40 + chart_width + 20
        score_width = self.width - score_x - 20
        
        # 水质评分卡
        self.water_card = self.create_score_card(
            score_x, chart_y, score_width, 95,
            '💧 水质评分', self.colors['info']
        )
        
        # 大坝安全卡
        self.dam_card = self.create_score_card(
            score_x, chart_y + 105, score_width, 95,
            '🏗️ 大坝安全', self.colors['success']
        )
    
    def create_score_card(self, x, y, width, height, title, color):
        """创建评分卡片"""
        card = {}
        
        # 背景
        card['bg'] = self.draw_card(x, y, width, height, border_color=color)
        
        # 标题
        card['title'] = self.canvas.create_text(
            x + 15, y + 20,
            text=title,
            anchor='w',
            font=self.small_font,
            fill=self.colors['text_secondary'],
            tags='score_title'
        )
        
        # 数值
        card['value'] = self.canvas.create_text(
            x + 15, y + 55,
            text='--%',
            anchor='w',
            font=('Arial', 32, 'bold'),
            fill=color,
            tags='score_value'
        )
        
        # 进度环
        ring_x = x + width - 40
        ring_y = y + height // 2
        ring_r = 25
        
        card['ring_bg'] = self.canvas.create_oval(
            ring_x - ring_r, ring_y - ring_r,
            ring_x + ring_r, ring_y + ring_r,
            outline=self.colors['card_border'],
            width=3,
            tags='ring_bg'
        )
        
        card['ring'] = self.canvas.create_arc(
            ring_x - ring_r, ring_y - ring_r,
            ring_x + ring_r, ring_y + ring_r,
            start=90,
            extent=0,
            outline=color,
            width=3,
            style='arc',
            tags='ring'
        )
        
        card['color'] = color
        card['ring_pos'] = (ring_x, ring_y, ring_r)
        
        return card
    
    def draw_chart_grid(self):
        """绘制图表网格"""
        area = self.chart_area
        grid_color = '#2a3555'
        
        # 垂直网格线
        for i in range(5):
            x = area['x'] + area['width'] * i / 4
            self.canvas.create_line(
                x, area['y'],
                x, area['y'] + area['height'],
                fill=grid_color,
                dash=(2, 4),
                tags='chart_grid'
            )
        
        # 水平网格线
        for i in range(4):
            y = area['y'] + area['height'] * i / 3
            self.canvas.create_line(
                area['x'], y,
                area['x'] + area['width'], y,
                fill=grid_color,
                dash=(2, 4),
                tags='chart_grid'
            )
    
    def create_footer_info(self):
        """创建底部信息区域"""
        footer_y = 580
        footer_width = self.width - 40
        
        # 信息卡片
        self.draw_card(20, footer_y, footer_width, 80)
        
        # 设备位置标题
        self.canvas.create_text(
            40, footer_y + 15,
            text='📍 设备位置监控',
            anchor='w',
            font=self.label_font,
            fill=self.colors['text_primary'],
            tags='footer'
        )
        
        # UAV位置
        self.uav_pos_text = self.canvas.create_text(
            40, footer_y + 40,
            text='UAV: --, --',
            anchor='w',
            font=self.small_font,
            fill=self.colors['info'],
            tags='footer'
        )
        
        # USV位置
        self.usv_pos_text = self.canvas.create_text(
            40, footer_y + 60,
            text='USV: --, --',
            anchor='w',
            font=self.small_font,
            fill=self.colors['success'],
            tags='footer'
        )
        
        # 系统信息
        info_x = self.width // 2
        
        self.canvas.create_text(
            info_x, footer_y + 15,
            text='⚙️ 系统信息',
            anchor='w',
            font=self.label_font,
            fill=self.colors['text_primary'],
            tags='footer'
        )
        
        self.collection_text = self.canvas.create_text(
            info_x, footer_y + 40,
            text='采集次数: 0',
            anchor='w',
            font=self.small_font,
            fill=self.colors['text_secondary'],
            tags='footer'
        )
        
        self.uptime_text = self.canvas.create_text(
            info_x, footer_y + 60,
            text='运行时间: 00:00:00',
            anchor='w',
            font=self.small_font,
            fill=self.colors['text_secondary'],
            tags='footer'
        )
    
    def fetch_data(self):
        """获取数据"""
        try:
            response = requests.get(f"{self.url}/api/data", timeout=2)
            if response.status_code == 200:
                self.data = response.json()
                self.collection_count += 1
                self.connected = True
                
                # 更新历史数据
                now = datetime.now()
                time_str = now.strftime("%H:%M:%S")
                
                self.history_data['time'].append(time_str)
                usv = self.data.get('usv', {})
                self.history_data['temp'].append(usv.get('temp', 0))
                self.history_data['humidity'].append(usv.get('humidity', 0))
                self.history_data['pressure'].append(usv.get('pressure', 0))
                self.history_data['light'].append(usv.get('light', 0))
                
                # 保持最多max_history个数据点
                for key in self.history_data:
                    if len(self.history_data[key]) > self.max_history:
                        self.history_data[key].pop(0)
                
                self.update_display()
                return True
        except Exception as e:
            self.connected = False
            print(f"获取数据失败: {e}")
        
        return False
    
    def update_data_loop(self):
        """数据更新循环"""
        while self.running:
            self.fetch_data()
            time.sleep(3)
    
    def update_display(self):
        """更新显示"""
        if not self.data:
            return
        
        try:
            usv = self.data.get('usv', {})
            uav = self.data.get('uav', {})
            scores = self.data.get('scores', {})
            
            # 更新数据卡片
            for key, card in self.data_cards.items():
                value = usv.get(key, 0)
                config = card['config']
                
                # 更新数值显示
                if key == 'light':
                    self.canvas.itemconfig(card['value'], text=f"{int(value)}")
                else:
                    self.canvas.itemconfig(card['value'], text=f"{float(value):.1f}")
                
                # 更新进度条
                min_val, max_val = config['range']
                percent = (float(value) - min_val) / (max_val - min_val)
                percent = max(0, min(1, percent))
                
                x, y, width, height = card['bounds']
                bar_padding = 10
                bar_y = y + height - 15
                new_width = (width - 2 * bar_padding) * percent
                
                self.canvas.coords(
                    card['progress'],
                    x + bar_padding, bar_y,
                    x + bar_padding + new_width, bar_y + 5
                )
            
            # 更新评分卡
            water_quality = scores.get('water_quality', 0)
            self.update_score_card(self.water_card, water_quality)
            
            dam_safety = scores.get('dam_safety', 0)
            self.update_score_card(self.dam_card, dam_safety)
            
            # 更新位置信息
            self.canvas.itemconfig(
                self.uav_pos_text,
                text=f"UAV: {uav.get('lat', 0):.6f}, {uav.get('lng', 0):.6f}"
            )
            
            self.canvas.itemconfig(
                self.usv_pos_text,
                text=f"USV: {usv.get('lat', 0):.6f}, {usv.get('lng', 0):.6f}"
            )
            
            # 更新图表
            self.draw_chart()
            
        except Exception as e:
            print(f"更新显示失败: {e}")
    
    def update_score_card(self, card, score):
        """更新评分卡"""
        try:
            self.canvas.itemconfig(
                card['value'],
                text=f"{float(score):.1f}%"
            )
            
            # 更新进度环
            extent = -360 * (float(score) / 100)
            self.canvas.itemconfig(
                card['ring'],
                extent=extent
            )
        except Exception as e:
            print(f"更新评分卡失败: {e}")
    
    def draw_chart(self):
        """绘制图表"""
        # 清除旧的图表线
        self.canvas.delete('chart_line')
        
        if len(self.history_data['time']) < 2:
            return
        
        area = self.chart_area
        
        # 绘制数据线
        datasets = [
            ('temp', self.colors['info'], 0, 50),
            ('humidity', self.colors['success'], 0, 100),
            ('pressure', self.colors['warning'], 950, 1050),
        ]
        
        for key, color, min_val, max_val in datasets:
            points = []
            data_len = len(self.history_data[key])
            
            for i, value in enumerate(self.history_data[key]):
                x = area['x'] + (area['width'] * i / max(1, data_len - 1))
                
                normalized = (float(value) - min_val) / (max_val - min_val)
                normalized = max(0, min(1, normalized))
                y = area['y'] + area['height'] * (1 - normalized)
                
                points.extend([x, y])
            
            if len(points) >= 4:
                self.canvas.create_line(
                    *points,
                    fill=color,
                    width=2,
                    smooth=True,
                    tags='chart_line'
                )
    
    def animate(self):
        """动画循环"""
        if not self.running:
            return
        
        self.animation_frame += 1
        
        # 更新时间
        current_time = datetime.now().strftime("%H:%M:%S")
        self.canvas.itemconfig(self.time_text, text=current_time)
        
        # 更新运行时间
        uptime = datetime.now() - self.start_time
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        seconds = uptime.seconds % 60
        uptime_str = f"运行时间: {hours:02d}:{minutes:02d}:{seconds:02d}"
        self.canvas.itemconfig(self.uptime_text, text=uptime_str)
        
        # 更新采集次数
        self.canvas.itemconfig(
            self.collection_text,
            text=f"采集次数: {self.collection_count}"
        )
        
        # 更新连接状态
        if self.connected:
            self.canvas.itemconfig(self.status_dot, fill=self.colors['success'])
            self.canvas.itemconfig(self.status_text, text='已连接')
            
            # 脉冲效果
            pulse = (math.sin(self.animation_frame * 0.1) + 1) / 2
            # Tkinter不支持alpha，使用缩放代替
        else:
            self.canvas.itemconfig(self.status_dot, fill=self.colors['danger'])
            self.canvas.itemconfig(self.status_text, text='未连接')
        
        # 继续动画
        self.root.after(100, self.animate)
    
    def toggle_fullscreen(self):
        """切换全屏"""
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)
    
    def quit(self):
        """退出程序"""
        self.running = False
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """运行主循环"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.quit()


def main():
    """主函数"""
    # 解析命令行参数
    url = "http://localhost:5002"
    width = 800
    height = 680
    fullscreen = False
    
    for arg in sys.argv[1:]:
        if arg.startswith('--url='):
            url = arg.split('=', 1)[1]
        elif arg.startswith('--width='):
            width = int(arg.split('=', 1)[1])
        elif arg.startswith('--height='):
            height = int(arg.split('=', 1)[1])
        elif arg.startswith('--fullscreen='):
            fullscreen = arg.split('=', 1)[1].lower() == 'true'
    
    print("=" * 60)
    print("空地海地面站智能数显系统")
    print("=" * 60)
    print(f"Dashboard URL: {url}")
    print(f"分辨率: {width}x{height}")
    print(f"全屏模式: {'是' if fullscreen else '否'}")
    print("=" * 60)
    print("快捷键:")
    print("  ESC - 退出")
    print("  F5  - 刷新数据")
    print("  F   - 切换全屏")
    print("=" * 60)
    
    dashboard = ModernDashboard(url=url, width=width, height=height, fullscreen=fullscreen)
    dashboard.run()


if __name__ == "__main__":
    main()
