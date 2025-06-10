import serial
import struct
import time
from config import *

class SerialTransmitter:
    """串口数据传输器"""
    
    def __init__(self, port=SERIAL_PORT, baudrate=SERIAL_BAUDRATE):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        self.is_connected = False
        
        # 尝试连接串口
        self.connect()
    
    def connect(self):
        """连接串口"""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=SERIAL_TIMEOUT,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            self.is_connected = True
            print(f"成功连接串口: {self.port} at {self.baudrate} baud")
        except serial.SerialException as e:
            self.is_connected = False
            print(f"串口连接失败: {e}")
        except Exception as e:
            self.is_connected = False
            print(f"连接错误: {e}")
    
    def disconnect(self):
        """断开串口连接"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.is_connected = False
            print("串口已断开")
    
    def send_matrix_data(self, matrix_data):
        """发送点阵数据"""
        if not self.is_connected or not self.serial_connection:
            return False
        
        try:
            # 构建数据包
            data_packet = self._build_data_packet(matrix_data)
            
            # 发送数据
            bytes_written = self.serial_connection.write(data_packet)
            self.serial_connection.flush()
            
            return bytes_written > 0
            
        except serial.SerialException as e:
            print(f"串口发送错误: {e}")
            self.is_connected = False
            return False
        except Exception as e:
            print(f"数据发送错误: {e}")
            return False
    
    def _build_data_packet(self, matrix_data):
        """构建数据包"""
        # 数据包格式：
        # 帧头(2字节) + 数据长度(2字节) + RGB数据(3024字节) + 校验和(1字节) + 帧尾(1字节)
        
        # 帧头
        header = b'\xAA\x55'
        
        # 数据长度 (36 * 28 * 3 = 3024 字节)
        data_length = MATRIX_WIDTH * MATRIX_HEIGHT * 3
        length_bytes = struct.pack('<H', data_length)  # 小端序，无符号短整数
        
        # RGB数据
        rgb_data = bytearray()
        for row in matrix_data:
            for pixel in row:
                rgb_data.extend([pixel[0], pixel[1], pixel[2]])  # R, G, B
        
        # 计算校验和（简单的XOR校验）
        checksum = 0
        for byte in rgb_data:
            checksum ^= byte
        checksum_byte = struct.pack('B', checksum & 0xFF)
        
        # 帧尾
        footer = b'\x0D'
        
        # 组装完整数据包
        packet = header + length_bytes + rgb_data + checksum_byte + footer
        
        return packet
    
    def send_test_pattern(self):
        """发送测试图案"""
        # 创建彩虹测试图案
        test_matrix = []
        
        for y in range(MATRIX_HEIGHT):
            row = []
            for x in range(MATRIX_WIDTH):
                # 创建彩虹效果
                hue = (x + y) % 7
                if hue == 0:
                    color = [255, 0, 0]    # 红
                elif hue == 1:
                    color = [255, 165, 0]  # 橙
                elif hue == 2:
                    color = [255, 255, 0]  # 黄
                elif hue == 3:
                    color = [0, 255, 0]    # 绿
                elif hue == 4:
                    color = [0, 255, 255]  # 青
                elif hue == 5:
                    color = [0, 0, 255]    # 蓝
                else:
                    color = [128, 0, 128]  # 紫
                
                row.append(color)
            test_matrix.append(row)
        
        return self.send_matrix_data(test_matrix)
    
    def change_port(self, new_port):
        """更改串口"""
        self.disconnect()
        self.port = new_port
        self.connect()
    
    def change_baudrate(self, new_baudrate):
        """更改波特率"""
        self.disconnect()
        self.baudrate = new_baudrate
        self.connect()
    
    def is_port_available(self, port):
        """检查串口是否可用"""
        try:
            test_serial = serial.Serial(port, self.baudrate, timeout=1)
            test_serial.close()
            return True
        except:
            return False
    
    @staticmethod
    def list_available_ports():
        """列出可用的串口"""
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def get_connection_status(self):
        """获取连接状态"""
        return {
            'connected': self.is_connected,
            'port': self.port,
            'baudrate': self.baudrate
        } 