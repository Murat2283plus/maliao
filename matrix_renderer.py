import numpy as np
from config import *

class MatrixRenderer:
    """点阵屏渲染器"""
    
    def __init__(self):
        self.width = MATRIX_WIDTH
        self.height = MATRIX_HEIGHT
        
        # 创建画布 (height, width, 3) for RGB
        self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
    
    def clear(self):
        """清空画布"""
        self.canvas.fill(0)
    
    def render_level(self, level):
        """渲染整个关卡到点阵"""
        # 清空画布
        self.clear()
        
        # 填充天空背景
        self._fill_background()
        
        # 获取相机位置
        camera_x = int(level.camera_x)
        
        # 渲染所有游戏对象
        all_objects = level.get_all_objects()
        
        for obj in all_objects:
            self._render_object(obj, camera_x)
        
        # 返回点阵数据
        return self._get_matrix_data()
    
    def _fill_background(self):
        """填充背景色"""
        self.canvas[:, :] = COLOR_SKY
    
    def _render_object(self, obj, camera_x):
        """渲染单个游戏对象"""
        # 计算在屏幕上的位置（相对于相机）
        screen_x = int(obj.x - camera_x)
        screen_y = int(obj.y)
        
        # 检查对象是否在屏幕范围内
        if (screen_x + obj.width < 0 or screen_x >= self.width or
            screen_y + obj.height < 0 or screen_y >= self.height):
            return
        
        # 渲染对象
        start_x = max(0, screen_x)
        end_x = min(self.width, screen_x + obj.width)
        start_y = max(0, screen_y)
        end_y = min(self.height, screen_y + obj.height)
        
        # 特殊处理马里奥的闪烁效果
        if hasattr(obj, 'invincible') and obj.invincible:
            # 无敌状态闪烁
            import time
            if int(time.time() * 10) % 2 == 0:  # 每0.1秒闪烁
                return
        
        # 填充像素
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                self.canvas[y, x] = obj.color
    
    def _get_matrix_data(self):
        """获取点阵数据格式"""
        # 转换为列表格式: [[R,G,B], [R,G,B], ...]
        matrix_data = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                pixel = self.canvas[y, x]
                row.append([int(pixel[0]), int(pixel[1]), int(pixel[2])])
            matrix_data.append(row)
        
        return matrix_data
    
    def render_text(self, text, x, y, color=COLOR_BLACK):
        """在指定位置渲染简单文本（仅支持数字）"""
        # 简单的3x5像素字体
        digit_patterns = {
            '0': [
                [1, 1, 1],
                [1, 0, 1],
                [1, 0, 1],
                [1, 0, 1],
                [1, 1, 1]
            ],
            '1': [
                [0, 1, 0],
                [1, 1, 0],
                [0, 1, 0],
                [0, 1, 0],
                [1, 1, 1]
            ],
            '2': [
                [1, 1, 1],
                [0, 0, 1],
                [1, 1, 1],
                [1, 0, 0],
                [1, 1, 1]
            ],
            '3': [
                [1, 1, 1],
                [0, 0, 1],
                [1, 1, 1],
                [0, 0, 1],
                [1, 1, 1]
            ],
            '4': [
                [1, 0, 1],
                [1, 0, 1],
                [1, 1, 1],
                [0, 0, 1],
                [0, 0, 1]
            ],
            '5': [
                [1, 1, 1],
                [1, 0, 0],
                [1, 1, 1],
                [0, 0, 1],
                [1, 1, 1]
            ],
            '6': [
                [1, 1, 1],
                [1, 0, 0],
                [1, 1, 1],
                [1, 0, 1],
                [1, 1, 1]
            ],
            '7': [
                [1, 1, 1],
                [0, 0, 1],
                [0, 0, 1],
                [0, 0, 1],
                [0, 0, 1]
            ],
            '8': [
                [1, 1, 1],
                [1, 0, 1],
                [1, 1, 1],
                [1, 0, 1],
                [1, 1, 1]
            ],
            '9': [
                [1, 1, 1],
                [1, 0, 1],
                [1, 1, 1],
                [0, 0, 1],
                [1, 1, 1]
            ]
        }
        
        current_x = x
        for char in str(text):
            if char in digit_patterns:
                pattern = digit_patterns[char]
                for py, row in enumerate(pattern):
                    for px, pixel in enumerate(row):
                        if pixel and current_x + px < self.width and y + py < self.height:
                            if current_x + px >= 0 and y + py >= 0:
                                self.canvas[y + py, current_x + px] = color
                current_x += 4  # 字符间距
    
    def render_game_over(self):
        """渲染游戏结束画面"""
        self.clear()
        # 填充红色背景表示游戏结束
        self.canvas[:, :] = [64, 0, 0]  # 暗红色
        
        # 在中央绘制简单的"X"图案
        center_x = self.width // 2
        center_y = self.height // 2
        
        # 绘制X
        for i in range(-3, 4):
            if 0 <= center_x + i < self.width and 0 <= center_y + i < self.height:
                self.canvas[center_y + i, center_x + i] = COLOR_BLACK
            if 0 <= center_x + i < self.width and 0 <= center_y - i < self.height:
                self.canvas[center_y - i, center_x + i] = COLOR_BLACK
        
        return self._get_matrix_data()
    
    def render_score_display(self, score, lives):
        """在画面顶部渲染分数和生命"""
        # 渲染分数（右上角）
        score_text = str(score)
        self.render_text(score_text, self.width - len(score_text) * 4, 1, COLOR_BLACK)
        
        # 渲染生命数（左上角）
        self.render_text(str(lives), 1, 1, COLOR_MARIO) 