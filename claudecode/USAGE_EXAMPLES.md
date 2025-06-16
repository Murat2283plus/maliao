# Matrix Mario 使用示例

## 快速开始示例

### 1. 模拟模式测试（推荐新手）

```bash
# 安装依赖
pip install -r requirements.txt

# 运行模拟模式，无需硬件
python run_console.py --mock-serial

# 在控制台中输入命令：
# 't' - 发送测试图案
# 's' - 查看状态
# 'h' - 查看帮助
# 'q' - 退出
```

### 2. GUI模式演示

```bash
# 启动图形界面
python run_gui.py

# 在GUI中：
# 1. 勾选 "Use Mock Serial"
# 2. 点击 "Start Game"
# 3. 观察矩阵显示区域的游戏画面
# 4. 在 "Test Pattern" 下拉菜单选择图案并点击 "Send Test"
```

### 3. 实际硬件模式

```bash
# 连接硬件后运行
python run_console.py --serial-port COM3 --fps 30

# 或者使用不同的串口
python run_console.py --serial-port /dev/ttyUSB0
```

## 控制器使用示例

### PS5手柄操作

```python
# 连接PS5手柄到电脑（蓝牙或USB）
# 游戏中的控制：

# 移动马里奥
左摇杆向左  → 马里奥向左移动
左摇杆向右  → 马里奥向右移动
十字键左    → 马里奥向左移动（备选）
十字键右    → 马里奥向右移动（备选）

# 跳跃
X按键      → 马里奥跳跃
圆圈按键    → 马里奥跳跃（备选）

# 攻击（火力马里奥状态下）
方块按键    → 发射火球

# 暂停
Options按键 → 暂停游戏
```

### 手柄测试

```bash
# 测试手柄连接
python -c "
import sys
sys.path.insert(0, 'src')
from src.controller.ps5_controller import PS5ControllerHandler

controller = PS5ControllerHandler()
if controller.is_connected():
    info = controller.get_controller_info()
    print(f'手柄已连接: {info[\"name\"]}')
else:
    print('未检测到手柄')
"
```

## 配置示例

### 修改游戏参数

编辑 `config.ini`：

```ini
[GAME]
fps = 60              # 提高帧率到60FPS
mario_speed = 3       # 增加马里奥移动速度
jump_power = 8        # 增强跳跃力度

[SERIAL]
port = /dev/ttyACM0   # 使用不同的串口
baud_rate = 230400    # 使用更高的波特率

[COLORS]
mario_hat = 0,255,0   # 马里奥帽子改为绿色
mario_shirt = 255,0,255 # 马里奥衣服改为紫色
```

### 自定义颜色方案

```python
# 在 src/config/settings.py 中添加新颜色
COLORS = {
    'MARIO_RAINBOW': [255, 128, 0],  # 橙色马里奥
    'NIGHT_SKY': [25, 25, 112],      # 夜空背景
    'GOLD_COIN': [255, 215, 0],      # 金币颜色
    # ... 更多自定义颜色
}
```

## 开发示例

### 添加新的游戏元素

```python
# 在 src/game_logic/world.py 中添加新敌人
class NewEnemy(DynamicSprite):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, 2, 2, COLORS['PURPLE'])
        self.speed = 1.5
        self.points = 300
    
    def update(self, dt: float) -> None:
        # 自定义敌人行为
        self.x += self.speed
        super().update(dt)

# 在关卡中添加新敌人
def _create_level_1(self) -> None:
    # ... 现有代码 ...
    self.dynamic_sprites.append(NewEnemy(25, ground_y - 2))
```

### 自定义渲染效果

```python
# 在 src/renderer/matrix_renderer.py 中添加特效
def _render_sprite_with_glow(self, sprite: Sprite, camera_x: int) -> None:
    """为精灵添加发光效果"""
    # 正常渲染精灵
    self._render_sprite(sprite, camera_x)
    
    # 添加发光边框
    if isinstance(sprite, Mario) and sprite.invincible:
        self._draw_glow_effect(sprite, camera_x)

def _draw_glow_effect(self, sprite: Sprite, camera_x: int) -> None:
    """绘制发光效果"""
    screen_x = sprite.x - camera_x
    screen_y = sprite.y
    
    glow_color = [255, 255, 255]  # 白色发光
    
    # 在精灵周围绘制发光像素
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            draw_pixel(self.frame_buffer, screen_x + dx, screen_y + dy,
                      glow_color, self.width, self.height)
```

## 调试示例

### 性能监控

```bash
# 运行性能测试
python tests/test_system.py

# 在游戏运行时查看状态
# 控制台模式下输入 's' 查看详细状态
# GUI模式下查看右侧状态面板
```

### 调试渲染

```python
# 开启调试模式查看精灵边界
renderer = MatrixRenderer()
renderer.set_debug_mode(True)

# 或在主程序中
app = MatrixMarioApp()
app.renderer.set_debug_mode(True)
```

### 串口调试

```python
# 监控串口数据
serial = SerialTransmitter('COM3')
serial.connect()

# 查看传输统计
status = serial.get_status()
print(f"已发送帧数: {status['frames_sent']}")
print(f"传输速率: {status['fps']:.1f} FPS")
print(f"错误次数: {status['transmission_errors']}")
```

## 高级使用示例

### 录制游戏画面

```python
# 录制矩阵数据到文件
import pickle
import time

frames = []
app = MatrixMarioApp(use_mock_serial=True)
app.initialize()

# 录制10秒
start_time = time.time()
while time.time() - start_time < 10:
    app.world.update(1.0/30)
    matrix = app.renderer.render_frame(app.world)
    frames.append(matrix)
    time.sleep(1.0/30)

# 保存录制数据
with open('game_recording.pkl', 'wb') as f:
    pickle.dump(frames, f)

print(f"录制了 {len(frames)} 帧")
```

### 回放录制内容

```python
# 回放录制的游戏画面
import pickle

with open('game_recording.pkl', 'rb') as f:
    frames = pickle.load(f)

serial = MockSerialTransmitter()
serial.connect()

for frame in frames:
    serial.send_frame_blocking(frame)
    time.sleep(1.0/30)  # 30 FPS回放

print("回放完成")
```

### 网络远程控制

```python
# 简单的网络控制服务器示例
import socket
import threading

class RemoteController:
    def __init__(self, app):
        self.app = app
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def start_server(self, port=8888):
        self.server.bind(('localhost', port))
        self.server.listen(1)
        print(f"远程控制服务器启动，端口: {port}")
        
        while True:
            conn, addr = self.server.accept()
            threading.Thread(target=self.handle_client, args=(conn,)).start()
    
    def handle_client(self, conn):
        while True:
            try:
                command = conn.recv(1024).decode()
                if command == 'JUMP':
                    self.app.world.mario.jump()
                elif command == 'LEFT':
                    self.app.world.mario.move_left()
                elif command == 'RIGHT':
                    self.app.world.mario.move_right()
                # 发送游戏状态回客户端
                status = self.app.world.get_status()
                conn.send(str(status).encode())
            except:
                break
        conn.close()

# 使用示例
app = MatrixMarioApp()
remote = RemoteController(app)
threading.Thread(target=remote.start_server).start()
app.start()
```

这些示例展示了Matrix Mario系统的灵活性和扩展性，用户可以根据需要进行各种自定义和扩展。