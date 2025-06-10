#!/usr/bin/env python3
"""
系统测试脚本 - 验证各个模块是否正常工作
"""

import sys
import time

def test_imports():
    """测试所有模块是否能正常导入"""
    print("测试模块导入...")
    
    try:
        import pygame
        print("✓ pygame 导入成功")
    except ImportError as e:
        print(f"✗ pygame 导入失败: {e}")
        return False
    
    try:
        import serial
        print("✓ pyserial 导入成功")
    except ImportError as e:
        print(f"✗ pyserial 导入失败: {e}")
        return False
    
    try:
        from PyQt5.QtWidgets import QApplication
        print("✓ PyQt5 导入成功")
    except ImportError as e:
        print(f"✗ PyQt5 导入失败: {e}")
        return False
    
    try:
        import numpy as np
        print("✓ numpy 导入成功")
    except ImportError as e:
        print(f"✗ numpy 导入失败: {e}")
        return False
    
    try:
        import config
        print("✓ config 导入成功")
    except ImportError as e:
        print(f"✗ config 导入失败: {e}")
        return False
    
    return True

def test_controller():
    """测试手柄模块"""
    print("\n测试手柄模块...")
    
    try:
        from controller_handler import ControllerHandler
        controller = ControllerHandler()
        print(f"✓ 手柄模块初始化成功")
        print(f"  手柄连接状态: {'已连接' if controller.is_connected() else '未连接'}")
        
        # 测试输入状态获取
        input_state = controller.get_input_state()
        print(f"  输入状态: {input_state}")
        
        return True
    except Exception as e:
        print(f"✗ 手柄模块测试失败: {e}")
        return False

def test_game_objects():
    """测试游戏对象模块"""
    print("\n测试游戏对象模块...")
    
    try:
        from game_objects import Mario, Enemy, Coin, Brick
        
        # 创建测试对象
        mario = Mario(10, 10)
        enemy = Enemy(20, 20)
        coin = Coin(15, 15)
        brick = Brick(5, 5)
        
        print("✓ 游戏对象创建成功")
        print(f"  马里奥位置: ({mario.x}, {mario.y})")
        print(f"  敌人位置: ({enemy.x}, {enemy.y})")
        print(f"  金币位置: ({coin.x}, {coin.y})")
        
        # 测试碰撞检测
        collision = mario.check_collision(coin)
        print(f"  碰撞检测: {'有碰撞' if collision else '无碰撞'}")
        
        return True
    except Exception as e:
        print(f"✗ 游戏对象模块测试失败: {e}")
        return False

def test_renderer():
    """测试渲染器模块"""
    print("\n测试渲染器模块...")
    
    try:
        from matrix_renderer import MatrixRenderer
        from level import Level
        
        renderer = MatrixRenderer()
        level = Level()
        
        print("✓ 渲染器初始化成功")
        print(f"  画布尺寸: {renderer.width}x{renderer.height}")
        
        # 测试渲染
        matrix_data = renderer.render_level(level)
        print(f"  渲染输出: {len(matrix_data)}行 x {len(matrix_data[0])}列")
        print(f"  像素格式: {type(matrix_data[0][0])}")
        
        return True
    except Exception as e:
        print(f"✗ 渲染器模块测试失败: {e}")
        return False

def test_serial():
    """测试串口模块"""
    print("\n测试串口模块...")
    
    try:
        from serial_transmitter import SerialTransmitter
        
        # 获取可用串口
        ports = SerialTransmitter.list_available_ports()
        print(f"✓ 串口模块初始化成功")
        print(f"  可用串口: {ports}")
        
        # 创建串口传输器（不真正连接）
        transmitter = SerialTransmitter('/dev/null')  # 使用虚拟端口
        print(f"  连接状态: {'已连接' if transmitter.is_connected else '未连接'}")
        
        return True
    except Exception as e:
        print(f"✗ 串口模块测试失败: {e}")
        return False

def test_level():
    """测试关卡模块"""
    print("\n测试关卡模块...")
    
    try:
        from level import Level
        
        level = Level()
        print("✓ 关卡初始化成功")
        print(f"  马里奥位置: ({level.mario.x}, {level.mario.y})")
        print(f"  敌人数量: {len(level.enemies)}")
        print(f"  金币数量: {len(level.coins)}")
        print(f"  地形对象数量: {len(level.solid_objects)}")
        
        # 测试输入处理
        test_input = {
            'left': False,
            'right': True,
            'up': False,
            'down': False,
            'jump': False,
            'attack': False
        }
        
        level.update(test_input)
        print(f"  更新后马里奥位置: ({level.mario.x}, {level.mario.y})")
        
        return True
    except Exception as e:
        print(f"✗ 关卡模块测试失败: {e}")
        return False

def test_complete_system():
    """测试完整系统集成"""
    print("\n测试完整系统集成...")
    
    try:
        from controller_handler import ControllerHandler
        from matrix_renderer import MatrixRenderer
        from level import Level
        
        # 初始化所有组件
        controller = ControllerHandler()
        renderer = MatrixRenderer()
        level = Level()
        
        print("✓ 所有组件初始化成功")
        
        # 模拟几帧游戏循环
        for frame in range(3):
            # 获取输入
            controller.update()
            input_state = controller.get_input_state()
            
            # 更新游戏
            level.update(input_state)
            
            # 渲染画面
            matrix_data = renderer.render_level(level)
            
            print(f"  帧 {frame + 1}: 渲染完成，分数: {level.get_score()}")
            time.sleep(0.1)  # 模拟帧间隔
        
        print("✓ 系统集成测试成功")
        return True
        
    except Exception as e:
        print(f"✗ 系统集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("="*50)
    print("超级马里奥点阵屏游戏 - 系统测试")
    print("="*50)
    
    tests = [
        ("模块导入", test_imports),
        ("手柄模块", test_controller),
        ("游戏对象", test_game_objects),
        ("渲染器", test_renderer),
        ("串口模块", test_serial),
        ("关卡模块", test_level),
        ("系统集成", test_complete_system),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"\n❌ {test_name} 测试失败")
        except Exception as e:
            print(f"\n❌ {test_name} 测试异常: {e}")
    
    print("\n" + "="*50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统准备就绪。")
        print("\n可以运行以下命令启动游戏:")
        print("  python main.py")
    else:
        print("⚠️  部分测试失败，请检查依赖和配置。")
        print("\n安装依赖:")
        print("  pip install -r requirements.txt")
    
    print("="*50)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main()) 