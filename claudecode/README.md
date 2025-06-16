# Matrix Mario - 36x28 RGB点阵屏超级马里奥游戏

基于PS5手柄控制的36x28 RGB点阵屏超级马里奥风格游戏系统。

## 功能特性

- **超级马里奥游戏逻辑**：适配36x28低分辨率的马里奥游戏
- **PS5手柄控制**：完整的PS5手柄输入支持
- **串口通信**：实时传输RGB矩阵数据到硬件设备
- **可视化界面**：PyQt5 GUI用于调试和演示
- **模块化设计**：清晰的代码结构，易于维护和扩展

## 系统要求

- Python 3.7+
- PS5手柄（DualSense）
- 36x28 RGB点阵屏硬件（可选，支持模拟模式）

## 安装

1. 克隆或下载项目
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 运行方式

### 控制台模式（推荐用于实际硬件）

```bash
python run_console.py
```

支持的命令行参数：
- `--mock-serial`: 使用模拟串口（用于测试）
- `--serial-port PORT`: 指定串口（默认：COM3）
- `--fps FPS`: 设置目标FPS（1-60）

示例：
```bash
# 使用模拟串口测试
python run_console.py --mock-serial

# 指定串口和FPS
python run_console.py --serial-port /dev/ttyUSB0 --fps 60
```

### GUI模式（推荐用于调试和演示）

```bash
python run_gui.py
```

GUI模式提供：
- 实时矩阵显示
- 游戏状态监控
- 串口设置
- 测试模式发送
- 日志显示

## 游戏控制

### PS5手柄控制
- **左摇杆/十字键**：左右移动
- **X键或圆圈键**：跳跃
- **方块键**：攻击（火力马里奥状态下）
- **Options键**：暂停

### 控制台命令（控制台模式）
- `p` 或 `pause`：暂停/继续游戏
- `r` 或 `restart`：重新开始游戏
- `s` 或 `status`：显示详细状态
- `t` 或 `test`：发送测试图案
- `fps <数字>`：设置FPS
- `clear`：清空显示
- `h` 或 `help`：显示帮助
- `q` 或 `quit`：退出游戏

## 配置

编辑 `config.ini` 文件来自定义设置：

```ini
[SERIAL]
port = COM3          # 串口号
baud_rate = 115200   # 波特率

[GAME]
fps = 30            # 游戏FPS
mario_speed = 2     # 马里奥移动速度

[CONTROLLER]
deadzone = 0.3      # 手柄死区

[COLORS]            # RGB颜色设置
mario_hat = 255,0,0
mario_shirt = 0,0,255
# ...
```

## 项目结构

```
claudecode/
├── src/
│   ├── controller/          # PS5手柄输入处理
│   ├── game_logic/          # 游戏逻辑（马里奥、世界、精灵）
│   ├── renderer/            # 矩阵渲染器
│   ├── serial_comm/         # 串口通信
│   ├── gui/                 # PyQt5界面
│   ├── config/              # 配置设置
│   ├── utils/               # 工具函数
│   └── main_app.py          # 主应用程序
├── run_console.py           # 控制台启动器
├── run_gui.py              # GUI启动器
├── config.ini              # 配置文件
├── requirements.txt        # 依赖列表
└── README.md              # 说明文档
```

## 硬件接口

### 串口数据格式

RGB矩阵数据通过串口发送，格式为：
- 帧头：`0xFF 0xFE`
- 数据：36×28×3字节RGB数据（按行排列）
- 帧尾：`0xFD 0xFC`

总共：2 + 3024 + 2 = 3028字节每帧

### 硬件要求

- 串口接收端需要能够处理115200波特率
- 能够驱动36×28 RGB LED矩阵
- 建议使用ESP32或类似微控制器

## 开发和扩展

### 添加新的游戏元素

1. 在 `src/game_logic/` 中创建新的精灵类
2. 继承 `Sprite` 或 `DynamicSprite` 基类
3. 在 `world.py` 中添加到游戏世界

### 修改渲染

编辑 `src/renderer/matrix_renderer.py` 来：
- 改变渲染顺序
- 添加特效
- 调整颜色映射

### 扩展控制器支持

在 `src/controller/` 中添加新的控制器类，实现相同的接口。

## 故障排除

### 常见问题

1. **手柄无法连接**
   - 确保手柄已配对并连接到电脑
   - 检查pygame是否正确识别手柄

2. **串口连接失败**
   - 检查串口号是否正确
   - 确认硬件设备已连接
   - 使用 `--mock-serial` 进行测试

3. **游戏卡顿**
   - 降低FPS设置
   - 检查串口传输速度
   - 确保没有其他程序占用资源

### 测试模式

使用模拟串口进行开发和测试：
```bash
python run_console.py --mock-serial
```

## 许可证

本项目仅供学习和研究使用。

## 致谢

基于经典超级马里奥游戏概念，适配为RGB矩阵显示系统。