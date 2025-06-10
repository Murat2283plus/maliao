from game_objects import *
from config import *

class Level:
    """游戏关卡类"""
    
    def __init__(self, level_data=None):
        self.mario = Mario(2, MATRIX_HEIGHT - GROUND_HEIGHT - MARIO_SIZE)
        self.enemies = []
        self.coins = []
        self.solid_objects = []  # 可碰撞的对象（地面、砖块等）
        
        # 相机位置
        self.camera_x = 0
        
        # 创建关卡
        if level_data:
            self._load_level_data(level_data)
        else:
            self._create_default_level()
    
    def _create_default_level(self):
        """创建默认关卡"""
        # 创建地面
        for x in range(MAP_WIDTH):
            for y in range(GROUND_HEIGHT):
                ground = Ground(x, MATRIX_HEIGHT - GROUND_HEIGHT + y)
                self.solid_objects.append(ground)
        
        # 创建一些平台
        # 平台1
        for x in range(10, 15):
            brick = Brick(x, MATRIX_HEIGHT - GROUND_HEIGHT - 5)
            self.solid_objects.append(brick)
        
        # 平台2
        for x in range(20, 25):
            brick = Brick(x, MATRIX_HEIGHT - GROUND_HEIGHT - 8)
            self.solid_objects.append(brick)
        
        # 创建一些砖块
        for x in range(30, 35):
            for y in range(2):
                brick = Brick(x, MATRIX_HEIGHT - GROUND_HEIGHT - 6 - y)
                self.solid_objects.append(brick)
        
        # 创建金币
        coin_positions = [(12, MATRIX_HEIGHT - GROUND_HEIGHT - 7),
                         (22, MATRIX_HEIGHT - GROUND_HEIGHT - 10),
                         (32, MATRIX_HEIGHT - GROUND_HEIGHT - 8),
                         (45, MATRIX_HEIGHT - GROUND_HEIGHT - 3)]
        
        for x, y in coin_positions:
            coin = Coin(x, y)
            self.coins.append(coin)
        
        # 创建敌人
        enemy_positions = [(25, MATRIX_HEIGHT - GROUND_HEIGHT - 1),
                          (40, MATRIX_HEIGHT - GROUND_HEIGHT - 1),
                          (60, MATRIX_HEIGHT - GROUND_HEIGHT - 1)]
        
        for x, y in enemy_positions:
            enemy = Enemy(x, y)
            self.enemies.append(enemy)
    
    def _load_level_data(self, level_data):
        """从数据加载关卡（预留接口）"""
        # TODO: 实现从文件或数据加载关卡
        pass
    
    def update(self, input_state):
        """更新关卡状态"""
        # 更新马里奥
        self.mario.update(input_state, self)
        
        # 更新敌人
        for enemy in self.enemies[:]:  # 使用切片复制，避免修改列表时的问题
            enemy.update(self)
            
            # 检查马里奥与敌人的碰撞
            if self.mario.check_collision(enemy) and enemy.active:
                # 检查是否是踩踏
                if self.mario.vy > 0 and self.mario.y < enemy.y:
                    # 踩踏敌人
                    enemy.active = False
                    self.mario.vy = -JUMP_STRENGTH * 0.5  # 小跳
                    self.mario.score += 200
                else:
                    # 被敌人伤害
                    self.mario.take_damage()
        
        # 检查金币收集
        for coin in self.coins[:]:
            if coin.active and self.mario.check_collision(coin):
                score = coin.collect()
                self.mario.score += score
        
        # 更新相机位置
        self._update_camera()
    
    def _update_camera(self):
        """更新相机位置以跟随马里奥"""
        # 让马里奥保持在屏幕中央偏左的位置
        target_camera_x = self.mario.x - MATRIX_WIDTH // 3
        
        # 限制相机边界
        if target_camera_x < 0:
            target_camera_x = 0
        elif target_camera_x > MAP_WIDTH - MATRIX_WIDTH:
            target_camera_x = MAP_WIDTH - MATRIX_WIDTH
        
        # 平滑相机移动
        self.camera_x += (target_camera_x - self.camera_x) * 0.1
    
    def get_all_objects(self):
        """获取所有活动对象"""
        objects = []
        
        # 添加马里奥
        if self.mario.active:
            objects.append(self.mario)
        
        # 添加地面和砖块
        objects.extend(self.solid_objects)
        
        # 添加活动的敌人
        for enemy in self.enemies:
            if enemy.active:
                objects.append(enemy)
        
        # 添加活动的金币
        for coin in self.coins:
            if coin.active:
                objects.append(coin)
        
        return objects
    
    def is_game_over(self):
        """检查游戏是否结束"""
        return not self.mario.active
    
    def get_score(self):
        """获取当前分数"""
        return self.mario.score
    
    def get_lives(self):
        """获取剩余生命数"""
        return self.mario.lives 