import pygame
from config import *

class ControllerHandler:
    """PS5手柄输入处理器"""
    
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        
        self.joystick = None
        self.controller_connected = False
        
        # 输入状态
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_pressed = False
        self.attack_pressed = False
        
        # 检测并连接PS5手柄
        self._connect_controller()
    
    def _connect_controller(self):
        """连接PS5手柄"""
        joystick_count = pygame.joystick.get_count()
        
        if joystick_count > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.controller_connected = True
            print(f"已连接手柄: {self.joystick.get_name()}")
        else:
            print("未检测到手柄")
            self.controller_connected = False
    
    def update(self):
        """更新输入状态"""
        if not self.controller_connected:
            return
        
        pygame.event.pump()
        
        # 获取方向键状态
        hat = self.joystick.get_hat(0)
        self.left_pressed = hat[0] == -1
        self.right_pressed = hat[0] == 1
        self.up_pressed = hat[1] == 1
        self.down_pressed = hat[1] == -1
        
        # 获取按键状态
        self.jump_pressed = self.joystick.get_button(PS5_BUTTON_X)
        self.attack_pressed = self.joystick.get_button(PS5_BUTTON_SQUARE)
        
        # 也可以使用左摇杆
        left_stick_x = self.joystick.get_axis(0)
        if abs(left_stick_x) > 0.3:  # 死区
            if left_stick_x < -0.3:
                self.left_pressed = True
            elif left_stick_x > 0.3:
                self.right_pressed = True
    
    def get_input_state(self):
        """获取当前输入状态"""
        return {
            'left': self.left_pressed,
            'right': self.right_pressed,
            'up': self.up_pressed,
            'down': self.down_pressed,
            'jump': self.jump_pressed,
            'attack': self.attack_pressed
        }
    
    def is_connected(self):
        """检查手柄是否连接"""
        return self.controller_connected
    
    def reconnect(self):
        """重新连接手柄"""
        pygame.joystick.quit()
        pygame.joystick.init()
        self._connect_controller() 