import math
from config import *

class GameObject:
    """游戏对象基类"""
    
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.active = True
    
    def get_rect(self):
        """获取碰撞矩形"""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }
    
    def check_collision(self, other):
        """检查与其他对象的碰撞"""
        rect1 = self.get_rect()
        rect2 = other.get_rect()
        
        return (rect1['x'] < rect2['x'] + rect2['width'] and
                rect1['x'] + rect1['width'] > rect2['x'] and
                rect1['y'] < rect2['y'] + rect2['height'] and
                rect1['y'] + rect1['height'] > rect2['y'])

class Mario(GameObject):
    """马里奥角色类"""
    
    def __init__(self, x, y):
        super().__init__(x, y, MARIO_SIZE, MARIO_SIZE, COLOR_MARIO)
        
        # 物理属性
        self.vx = 0  # 水平速度
        self.vy = 0  # 垂直速度
        self.on_ground = False
        
        # 游戏状态
        self.lives = 3
        self.score = 0
        self.invincible = False
        self.invincible_timer = 0
        
        # 动画状态
        self.facing_right = True
        self.animation_frame = 0
        self.animation_timer = 0
    
    def update(self, input_state, level):
        """更新马里奥状态"""
        if not self.active:
            return
        
        # 处理输入
        self._handle_input(input_state)
        
        # 应用重力
        if not self.on_ground:
            self.vy += GRAVITY
        
        # 更新位置
        new_x = self.x + self.vx
        new_y = self.y + self.vy
        
        # 碰撞检测和位置更新
        self._update_position(new_x, new_y, level)
        
        # 更新无敌状态
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # 更新动画
        self._update_animation()
        
        # 边界检查
        self._check_boundaries()
    
    def _handle_input(self, input_state):
        """处理输入控制"""
        # 水平移动
        if input_state['left']:
            self.vx = -MARIO_SPEED
            self.facing_right = False
        elif input_state['right']:
            self.vx = MARIO_SPEED
            self.facing_right = True
        else:
            self.vx = 0
        
        # 跳跃
        if input_state['jump'] and self.on_ground:
            self.vy = -JUMP_STRENGTH
            self.on_ground = False
    
    def _update_position(self, new_x, new_y, level):
        """更新位置并处理碰撞"""
        # 水平移动碰撞检测
        self.x = new_x
        if self._check_level_collision(level):
            self.x -= self.vx  # 撤销移动
            self.vx = 0
        
        # 垂直移动碰撞检测
        self.y = new_y
        collision = self._check_level_collision(level)
        if collision:
            if self.vy > 0:  # 向下移动，着地
                self.y = collision['y'] - self.height
                self.vy = 0
                self.on_ground = True
            else:  # 向上移动，撞头
                self.y = collision['y'] + collision['height']
                self.vy = 0
        else:
            self.on_ground = False
    
    def _check_level_collision(self, level):
        """检查与关卡的碰撞"""
        for obj in level.solid_objects:
            if self.check_collision(obj):
                return obj.get_rect()
        return None
    
    def _update_animation(self):
        """更新动画帧"""
        self.animation_timer += 1
        if self.animation_timer >= 10:  # 每10帧切换一次
            self.animation_frame = (self.animation_frame + 1) % 2
            self.animation_timer = 0
    
    def _check_boundaries(self):
        """边界检查"""
        # 左边界
        if self.x < 0:
            self.x = 0
            self.vx = 0
        
        # 右边界（相对于相机）
        if self.x > MAP_WIDTH - self.width:
            self.x = MAP_WIDTH - self.width
            self.vx = 0
        
        # 掉出底部
        if self.y > MATRIX_HEIGHT:
            self.die()
    
    def die(self):
        """马里奥死亡"""
        self.lives -= 1
        if self.lives <= 0:
            self.active = False
        else:
            # 重置位置
            self.x = 2
            self.y = MATRIX_HEIGHT - GROUND_HEIGHT - self.height
            self.vx = 0
            self.vy = 0
            self.invincible = True
            self.invincible_timer = 60  # 2秒无敌（30fps）
    
    def take_damage(self):
        """受到伤害"""
        if not self.invincible:
            self.die()

class Brick(GameObject):
    """砖块类"""
    
    def __init__(self, x, y):
        super().__init__(x, y, 1, 1, COLOR_BRICK)
        self.breakable = True

class Ground(GameObject):
    """地面类"""
    
    def __init__(self, x, y, width=1, height=1):
        super().__init__(x, y, width, height, COLOR_GROUND)

class Coin(GameObject):
    """金币类"""
    
    def __init__(self, x, y):
        super().__init__(x, y, 1, 1, COLOR_COIN)
        self.collected = False
        self.value = 100
    
    def collect(self):
        """收集金币"""
        if not self.collected:
            self.collected = True
            self.active = False
            return self.value
        return 0

class Enemy(GameObject):
    """敌人基类"""
    
    def __init__(self, x, y, color=COLOR_ENEMY):
        super().__init__(x, y, 1, 1, color)
        self.vx = -0.5  # 向左移动
        self.vy = 0
        self.direction = -1
    
    def update(self, level):
        """更新敌人状态"""
        if not self.active:
            return
        
        # 移动
        new_x = self.x + self.vx
        
        # 简单的边界和碰撞检测
        if new_x <= 0 or new_x >= MAP_WIDTH - self.width:
            self.direction *= -1
            self.vx *= -1
        else:
            self.x = new_x
        
        # 应用重力（简化）
        if self.y < MATRIX_HEIGHT - GROUND_HEIGHT - self.height:
            self.vy += GRAVITY * 0.5
            self.y += self.vy
        else:
            self.y = MATRIX_HEIGHT - GROUND_HEIGHT - self.height
            self.vy = 0 