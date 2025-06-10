#!/usr/bin/env python3
"""
超级马里奥点阵屏游戏 - 主程序
适配36x28 RGB点阵屏，支持PS5手柄控制和串口数据传输
"""

import sys
import time
import threading
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication

from controller_handler import ControllerHandler
from matrix_renderer import MatrixRenderer
from serial_transmitter import SerialTransmitter
from level import Level
from gui_display import create_gui_application
from config import *

class GameEngine(QThread):
    """游戏引擎线程"""
    
    # 信号定义
    matrix_updated = pyqtSignal(list)  # 点阵数据更新
    game_status_updated = pyqtSignal(int, int, bool)  # 游戏状态更新(分数, 生命, 手柄连接)
    status_message = pyqtSignal(str)  # 状态消息
    
    def __init__(self):
        super().__init__()
        
        # 游戏状态
        self.running = False
        self.paused = False
        self.game_over = False
        
        # 初始化组件
        self.controller = ControllerHandler()
        self.renderer = MatrixRenderer()
        self.serial_transmitter = SerialTransmitter()
        self.level = Level()
        
        # 游戏循环计时
        self.last_update_time = time.time()
        self.frame_time = 1.0 / GAME_FPS
        
        print("游戏引擎初始化完成")
    
    def run(self):
        """游戏主循环"""
        self.running = True
        self.status_message.emit("游戏运行中...")
        
        while self.running:
            current_time = time.time()
            
            # 控制帧率
            if current_time - self.last_update_time >= self.frame_time:
                if not self.paused:
                    self.update_game()
                    self.render_frame()
                
                self.last_update_time = current_time
            else:
                # 短暂休眠避免CPU占用过高
                time.sleep(0.001)
        
        self.status_message.emit("游戏已停止")
    
    def update_game(self):
        """更新游戏逻辑"""
        # 更新手柄输入
        self.controller.update()
        input_state = self.controller.get_input_state()
        
        # 更新关卡
        self.level.update(input_state)
        
        # 检查游戏结束
        if self.level.is_game_over():
            self.game_over = True
            self.status_message.emit("游戏结束！")
        
        # 发送游戏状态更新信号
        self.game_status_updated.emit(
            self.level.get_score(),
            self.level.get_lives(),
            self.controller.is_connected()
        )
    
    def render_frame(self):
        """渲染游戏画面"""
        if self.game_over:
            # 渲染游戏结束画面
            matrix_data = self.renderer.render_game_over()
        else:
            # 渲染正常游戏画面
            matrix_data = self.renderer.render_level(self.level)
            
            # 添加分数和生命显示
            self.renderer.render_score_display(
                self.level.get_score(),
                self.level.get_lives()
            )
        
        # 发送点阵数据更新信号
        self.matrix_updated.emit(matrix_data)
        
        # 通过串口发送数据
        if self.serial_transmitter.is_connected:
            success = self.serial_transmitter.send_matrix_data(matrix_data)
            if not success:
                self.status_message.emit("串口传输失败")
    
    def start_game(self):
        """开始游戏"""
        if not self.isRunning():
            self.start()
        else:
            self.paused = False
            self.status_message.emit("游戏继续")
    
    def pause_game(self):
        """暂停游戏"""
        self.paused = True
        self.status_message.emit("游戏已暂停")
    
    def reset_game(self):
        """重置游戏"""
        self.level = Level()
        self.game_over = False
        self.paused = False
        self.status_message.emit("游戏已重置")
    
    def stop_game(self):
        """停止游戏"""
        self.running = False
        self.wait()  # 等待线程结束
    
    def reconnect_controller(self):
        """重新连接手柄"""
        self.controller.reconnect()
    
    def change_serial_port(self, port, baudrate):
        """更改串口设置"""
        self.serial_transmitter.change_port(port)
        self.serial_transmitter.change_baudrate(int(baudrate))
    
    def send_test_pattern(self):
        """发送测试图案"""
        if self.serial_transmitter.is_connected:
            success = self.serial_transmitter.send_test_pattern()
            if success:
                self.status_message.emit("测试图案发送成功")
            else:
                self.status_message.emit("测试图案发送失败")
        else:
            self.status_message.emit("串口未连接")

class MarioGame:
    """马里奥游戏主应用"""
    
    def __init__(self):
        # 创建GUI应用
        self.app, self.window = create_gui_application()
        
        # 创建游戏引擎
        self.game_engine = GameEngine()
        
        # 连接信号和槽
        self.connect_signals()
        
        # GUI定时器
        self.gui_timer = QTimer()
        self.gui_timer.timeout.connect(self.update_gui)
        self.gui_timer.start(50)  # 20fps GUI更新
        
        print("马里奥游戏应用初始化完成")
    
    def connect_signals(self):
        """连接信号和槽"""
        # 游戏引擎信号
        self.game_engine.matrix_updated.connect(self.window.update_matrix_display)
        self.game_engine.game_status_updated.connect(self.window.update_game_status)
        self.game_engine.status_message.connect(self.window.update_status)
        
        # GUI控制信号
        self.window.control_panel.start_btn.clicked.connect(self.start_game)
        self.window.control_panel.pause_btn.clicked.connect(self.pause_game)
        self.window.control_panel.reset_btn.clicked.connect(self.reset_game)
        self.window.control_panel.test_btn.clicked.connect(self.send_test_pattern)
        self.window.control_panel.connect_btn.clicked.connect(self.toggle_serial_connection)
    
    def start_game(self):
        """开始游戏"""
        self.game_engine.start_game()
        self.window.control_panel.start_btn.setText("继续游戏")
    
    def pause_game(self):
        """暂停游戏"""
        self.game_engine.pause_game()
    
    def reset_game(self):
        """重置游戏"""
        self.game_engine.reset_game()
        self.window.control_panel.start_btn.setText("开始游戏")
    
    def send_test_pattern(self):
        """发送测试图案"""
        self.game_engine.send_test_pattern()
    
    def toggle_serial_connection(self):
        """切换串口连接"""
        if self.window.control_panel.is_connected:
            # 断开连接
            self.game_engine.serial_transmitter.disconnect()
            self.window.control_panel.disconnect_serial()
            self.window.update_status("串口已断开")
        else:
            # 连接串口
            port = self.window.control_panel.port_combo.currentText()
            baudrate = self.window.control_panel.baudrate_combo.currentText()
            
            if port:
                self.game_engine.change_serial_port(port, baudrate)
                if self.game_engine.serial_transmitter.is_connected:
                    self.window.control_panel.connect_serial()
                    self.window.update_status(f"串口已连接: {port}")
                else:
                    self.window.update_status("串口连接失败")
            else:
                self.window.update_status("请选择串口")
    
    def update_gui(self):
        """更新GUI"""
        # 这里可以添加定期的GUI更新逻辑
        pass
    
    def run(self):
        """运行应用程序"""
        # 显示启动消息
        self.window.update_status("应用程序已启动，请连接PS5手柄和串口设备")
        
        # 运行Qt应用程序
        return self.app.exec_()
    
    def cleanup(self):
        """清理资源"""
        self.game_engine.stop_game()
        self.game_engine.serial_transmitter.disconnect()

def main():
    """主函数"""
    print("="*50)
    print("超级马里奥点阵屏游戏")
    print("适配36x28 RGB点阵屏")
    print("支持PS5手柄控制和串口传输")
    print("="*50)
    
    try:
        # 创建并运行游戏应用
        game = MarioGame()
        
        # 设置退出时的清理
        import atexit
        atexit.register(game.cleanup)
        
        # 运行应用
        exit_code = game.run()
        
        # 清理资源
        game.cleanup()
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\n用户中断程序")
        return 1
    except Exception as e:
        print(f"程序运行错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 