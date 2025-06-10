# 游戏配置
MATRIX_WIDTH = 36
MATRIX_HEIGHT = 28
GAME_FPS = 30

# 马里奥游戏配置
MARIO_SIZE = 2  # 马里奥在点阵屏上的大小（像素）
MARIO_SPEED = 1  # 马里奥移动速度
JUMP_STRENGTH = 3  # 跳跃力度
GRAVITY = 0.2  # 重力加速度

# 颜色定义 (RGB)
COLOR_MARIO = [255, 0, 0]  # 红色
COLOR_GROUND = [139, 69, 19]  # 棕色
COLOR_SKY = [135, 206, 235]  # 天蓝色
COLOR_BRICK = [255, 165, 0]  # 橙色
COLOR_COIN = [255, 255, 0]  # 黄色
COLOR_ENEMY = [128, 0, 128]  # 紫色
COLOR_BLACK = [0, 0, 0]  # 黑色

# PS5手柄按键映射
PS5_BUTTON_X = 0  # 跳跃
PS5_BUTTON_SQUARE = 2  # 攻击
PS5_DPAD_LEFT = 13
PS5_DPAD_RIGHT = 14
PS5_DPAD_UP = 11
PS5_DPAD_DOWN = 12

# 串口配置
SERIAL_PORT = '/dev/ttyUSB0'  # 默认串口，可在GUI中修改
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 1

# 地图配置
GROUND_HEIGHT = 4  # 地面高度
MAP_WIDTH = 200  # 地图宽度（像素） 