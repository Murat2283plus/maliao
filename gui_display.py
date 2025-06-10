import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
from config import *

class MatrixWidget(QWidget):
    """点阵显示小部件"""
    
    def __init__(self, width=MATRIX_WIDTH, height=MATRIX_HEIGHT, parent=None):
        super().__init__(parent)
        self.matrix_width = width
        self.matrix_height = height
        self.pixel_size = 15  # 每个像素的显示大小
        
        # 设置小部件大小
        self.setFixedSize(
            self.matrix_width * self.pixel_size,
            self.matrix_height * self.pixel_size
        )
        
        # 初始化矩阵数据
        self.matrix_data = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]
    
    def update_matrix(self, matrix_data):
        """更新矩阵数据"""
        self.matrix_data = matrix_data
        self.update()  # 触发重绘
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        
        for y in range(self.matrix_height):
            for x in range(self.matrix_width):
                # 获取像素颜色
                r, g, b = self.matrix_data[y][x]
                color = QColor(r, g, b)
                
                # 绘制像素
                rect = QRect(
                    x * self.pixel_size,
                    y * self.pixel_size,
                    self.pixel_size,
                    self.pixel_size
                )
                painter.fillRect(rect, color)
                
                # 绘制网格线（可选）
                if self.pixel_size > 5:
                    painter.setPen(QColor(64, 64, 64))
                    painter.drawRect(rect)

class ControlPanel(QWidget):
    """控制面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        
        # 串口设置组
        serial_group = QGroupBox("串口设置")
        serial_layout = QFormLayout()
        
        # 串口选择
        self.port_combo = QComboBox()
        self.refresh_ports()
        serial_layout.addRow("串口:", self.port_combo)
        
        # 波特率选择
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(['9600', '19200', '38400', '57600', '115200', '230400'])
        self.baudrate_combo.setCurrentText('115200')
        serial_layout.addRow("波特率:", self.baudrate_combo)
        
        # 连接按钮
        self.connect_btn = QPushButton("连接")
        self.connect_btn.clicked.connect(self.toggle_connection)
        serial_layout.addRow("", self.connect_btn)
        
        # 测试按钮
        self.test_btn = QPushButton("发送测试图案")
        self.test_btn.clicked.connect(self.send_test_pattern)
        serial_layout.addRow("", self.test_btn)
        
        serial_group.setLayout(serial_layout)
        layout.addWidget(serial_group)
        
        # 游戏状态组
        game_group = QGroupBox("游戏状态")
        game_layout = QFormLayout()
        
        self.score_label = QLabel("0")
        game_layout.addRow("分数:", self.score_label)
        
        self.lives_label = QLabel("3")
        game_layout.addRow("生命:", self.lives_label)
        
        self.controller_label = QLabel("未连接")
        game_layout.addRow("手柄:", self.controller_label)
        
        game_group.setLayout(game_layout)
        layout.addWidget(game_group)
        
        # 控制按钮组
        control_group = QGroupBox("游戏控制")
        control_layout = QVBoxLayout()
        
        self.start_btn = QPushButton("开始游戏")
        self.start_btn.clicked.connect(self.start_game)
        control_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("暂停游戏")
        self.pause_btn.clicked.connect(self.pause_game)
        control_layout.addWidget(self.pause_btn)
        
        self.reset_btn = QPushButton("重置游戏")
        self.reset_btn.clicked.connect(self.reset_game)
        control_layout.addWidget(self.reset_btn)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # 添加伸缩空间
        layout.addStretch()
        
        self.setLayout(layout)
        
        # 连接状态
        self.is_connected = False
    
    def refresh_ports(self):
        """刷新串口列表"""
        from serial_transmitter import SerialTransmitter
        ports = SerialTransmitter.list_available_ports()
        self.port_combo.clear()
        self.port_combo.addItems(ports)
    
    def toggle_connection(self):
        """切换连接状态"""
        if self.is_connected:
            self.disconnect_serial()
        else:
            self.connect_serial()
    
    def connect_serial(self):
        """连接串口"""
        self.is_connected = True
        self.connect_btn.setText("断开")
        self.connect_btn.setStyleSheet("background-color: #ff6b6b;")
    
    def disconnect_serial(self):
        """断开串口"""
        self.is_connected = False
        self.connect_btn.setText("连接")
        self.connect_btn.setStyleSheet("")
    
    def send_test_pattern(self):
        """发送测试图案信号"""
        pass  # 由主窗口处理
    
    def start_game(self):
        """开始游戏信号"""
        pass  # 由主窗口处理
    
    def pause_game(self):
        """暂停游戏信号"""
        pass  # 由主窗口处理
    
    def reset_game(self):
        """重置游戏信号"""
        pass  # 由主窗口处理
    
    def update_game_status(self, score, lives, controller_connected):
        """更新游戏状态"""
        self.score_label.setText(str(score))
        self.lives_label.setText(str(lives))
        self.controller_label.setText("已连接" if controller_connected else "未连接")
        self.controller_label.setStyleSheet(
            "color: green;" if controller_connected else "color: red;"
        )

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # 定时器用于刷新显示
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        
        # 游戏数据
        self.current_matrix_data = None
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("超级马里奥点阵屏游戏")
        self.setFixedSize(800, 600)
        
        # 创建中央小部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout()
        
        # 左侧：点阵显示
        left_layout = QVBoxLayout()
        
        # 点阵显示标题
        matrix_label = QLabel("游戏画面 (36x28)")
        matrix_label.setAlignment(Qt.AlignCenter)
        matrix_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        left_layout.addWidget(matrix_label)
        
        # 点阵显示
        self.matrix_widget = MatrixWidget()
        left_layout.addWidget(self.matrix_widget, alignment=Qt.AlignCenter)
        
        # 状态栏
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        left_layout.addWidget(self.status_label)
        
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        main_layout.addWidget(left_widget, 2)
        
        # 右侧：控制面板
        self.control_panel = ControlPanel()
        main_layout.addWidget(self.control_panel, 1)
        
        central_widget.setLayout(main_layout)
        
        # 创建菜单栏
        self.create_menus()
        
        # 状态栏
        self.statusBar().showMessage("准备就绪")
    
    def create_menus(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 设置菜单
        settings_menu = menubar.addMenu('设置')
        
        refresh_ports_action = QAction('刷新串口', self)
        refresh_ports_action.triggered.connect(self.control_panel.refresh_ports)
        settings_menu.addAction(refresh_ports_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", 
                         "超级马里奥点阵屏游戏\n\n"
                         "一个为36x28 RGB点阵屏设计的\n"
                         "可通过PS5手柄控制的超级马里奥游戏\n\n"
                         "支持实时串口数据传输")
    
    def update_matrix_display(self, matrix_data):
        """更新点阵显示"""
        self.current_matrix_data = matrix_data
        self.matrix_widget.update_matrix(matrix_data)
    
    def update_game_status(self, score, lives, controller_connected):
        """更新游戏状态"""
        self.control_panel.update_game_status(score, lives, controller_connected)
    
    def update_status(self, message):
        """更新状态消息"""
        self.status_label.setText(message)
        self.statusBar().showMessage(message)
    
    def update_display(self):
        """定期更新显示"""
        pass  # 由主应用控制
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        reply = QMessageBox.question(self, '确认退出', 
                                   '确定要退出游戏吗？',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

def create_gui_application():
    """创建GUI应用程序"""
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 设置暗色主题（可选）
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    
    # app.setPalette(palette)  # 取消注释以启用暗色主题
    
    window = MainWindow()
    window.show()
    
    return app, window 