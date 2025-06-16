"""
PyQt5 GUI for Matrix Mario Game
Provides visual display and control interface
"""
import sys
from typing import List, Optional
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                            QGroupBox, QGridLayout, QComboBox, QSpinBox,
                            QProgressBar, QCheckBox)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont

from ..main_app import MatrixMarioApp
from ..config.settings import MATRIX_WIDTH, MATRIX_HEIGHT

class MatrixWidget(QWidget):
    """Custom widget to display the RGB matrix"""
    
    def __init__(self, width: int = MATRIX_WIDTH, height: int = MATRIX_HEIGHT):
        super().__init__()
        self.matrix_width = width
        self.matrix_height = height
        self.pixel_size = 15  # Size of each pixel in the display
        self.matrix_data: List[List[List[int]]] = []
        
        # Initialize with black matrix
        self.clear_matrix()
        
        # Set widget size
        self.setFixedSize(
            self.matrix_width * self.pixel_size + 2,
            self.matrix_height * self.pixel_size + 2
        )
    
    def clear_matrix(self) -> None:
        """Clear the matrix to all black"""
        self.matrix_data = [[[0, 0, 0] for _ in range(self.matrix_width)] 
                           for _ in range(self.matrix_height)]
        self.update()
    
    def set_matrix(self, matrix: List[List[List[int]]]) -> None:
        """Set the matrix data and update display"""
        self.matrix_data = matrix
        self.update()
    
    def paintEvent(self, event):
        """Paint the matrix display"""
        painter = QPainter(self)
        
        # Draw border
        painter.setPen(QColor(128, 128, 128))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
        
        # Draw pixels
        for y in range(self.matrix_height):
            for x in range(self.matrix_width):
                if y < len(self.matrix_data) and x < len(self.matrix_data[y]):
                    r, g, b = self.matrix_data[y][x]
                    color = QColor(r, g, b)
                else:
                    color = QColor(0, 0, 0)
                
                painter.fillRect(
                    x * self.pixel_size + 1,
                    y * self.pixel_size + 1,
                    self.pixel_size,
                    self.pixel_size,
                    color
                )

class GameThread(QThread):
    """Thread to run the game without blocking GUI"""
    
    status_updated = pyqtSignal(dict)
    matrix_updated = pyqtSignal(list)
    
    def __init__(self, use_mock_serial: bool = True, serial_port: str = "COM3"):
        super().__init__()
        self.use_mock_serial = use_mock_serial
        self.serial_port = serial_port
        self.app: Optional[MatrixMarioApp] = None
        self.running = False
    
    def run(self) -> None:
        """Run the game in separate thread"""
        self.app = MatrixMarioApp(
            use_mock_serial=self.use_mock_serial,
            serial_port=self.serial_port
        )
        
        # Override the render method to emit matrix data
        original_render = self.app._render
        
        def render_with_signal():
            original_render()
            # Get the last rendered matrix and emit signal
            if hasattr(self.app.renderer, 'frame_buffer'):
                self.matrix_updated.emit(self.app.renderer.frame_buffer)
        
        self.app._render = render_with_signal
        
        # Initialize and start
        if self.app.initialize():
            self.running = True
            self.app.start()
    
    def stop_game(self) -> None:
        """Stop the game"""
        self.running = False
        if self.app:
            self.app.stop()

class MatrixMarioGUI(QMainWindow):
    """Main GUI window for Matrix Mario"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Matrix Mario - 36x28 RGB Game")
        self.setFixedSize(900, 700)
        
        # Game thread
        self.game_thread: Optional[GameThread] = None
        
        # Timer for status updates
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(500)  # Update every 500ms
        
        self.init_ui()
    
    def init_ui(self) -> None:
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Matrix display
        left_panel = self.create_display_panel()
        main_layout.addWidget(left_panel, 2)
        
        # Right panel - Controls and status
        right_panel = self.create_control_panel()
        main_layout.addWidget(right_panel, 1)
    
    def create_display_panel(self) -> QWidget:
        """Create the matrix display panel"""
        panel = QGroupBox("Matrix Display (36x28)")
        layout = QVBoxLayout(panel)
        
        # Matrix widget
        self.matrix_widget = MatrixWidget()
        layout.addWidget(self.matrix_widget, alignment=Qt.AlignCenter)
        
        # Display controls
        display_controls = QHBoxLayout()
        
        self.test_pattern_combo = QComboBox()
        self.test_pattern_combo.addItems([
            "checkerboard", "rainbow", "solid_red", 
            "solid_green", "solid_blue", "black"
        ])
        display_controls.addWidget(QLabel("Test Pattern:"))
        display_controls.addWidget(self.test_pattern_combo)
        
        test_button = QPushButton("Send Test")
        test_button.clicked.connect(self.send_test_pattern)
        display_controls.addWidget(test_button)
        
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_display)
        display_controls.addWidget(clear_button)
        
        layout.addLayout(display_controls)
        
        return panel
    
    def create_control_panel(self) -> QWidget:
        """Create the control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Game controls
        game_group = self.create_game_controls()
        layout.addWidget(game_group)
        
        # Serial settings
        serial_group = self.create_serial_settings()
        layout.addWidget(serial_group)
        
        # Status display
        status_group = self.create_status_display()
        layout.addWidget(status_group)
        
        # Log display
        log_group = self.create_log_display()
        layout.addWidget(log_group)
        
        return panel
    
    def create_game_controls(self) -> QGroupBox:
        """Create game control widgets"""
        group = QGroupBox("Game Controls")
        layout = QVBoxLayout(group)
        
        # Game buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Game")
        self.start_button.clicked.connect(self.start_game)
        button_layout.addWidget(self.start_button)
        
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_game)
        self.pause_button.setEnabled(False)
        button_layout.addWidget(self.pause_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_game)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        # FPS control
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("FPS:"))
        
        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(1, 60)
        self.fps_spinbox.setValue(30)
        self.fps_spinbox.valueChanged.connect(self.fps_changed)
        fps_layout.addWidget(self.fps_spinbox)
        
        layout.addLayout(fps_layout)
        
        # Mock serial checkbox
        self.mock_serial_checkbox = QCheckBox("Use Mock Serial")
        self.mock_serial_checkbox.setChecked(True)
        layout.addWidget(self.mock_serial_checkbox)
        
        return group
    
    def create_serial_settings(self) -> QGroupBox:
        """Create serial settings widgets"""
        group = QGroupBox("Serial Settings")
        layout = QVBoxLayout(group)
        
        # Port selection
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        
        self.port_combo = QComboBox()
        self.port_combo.setEditable(True)
        self.port_combo.addItems(["COM3", "COM4", "/dev/ttyUSB0", "/dev/ttyACM0"])
        port_layout.addWidget(self.port_combo)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_serial_ports)
        port_layout.addWidget(refresh_button)
        
        layout.addLayout(port_layout)
        
        # Connection status
        self.connection_status = QLabel("Disconnected")
        self.connection_status.setStyleSheet("color: red")
        layout.addWidget(self.connection_status)
        
        return group
    
    def create_status_display(self) -> QGroupBox:
        """Create status display widgets"""
        group = QGroupBox("Status")
        layout = QVBoxLayout(group)
        
        # FPS display
        self.fps_label = QLabel("FPS: 0.0")
        layout.addWidget(self.fps_label)
        
        # Game status
        self.game_status_label = QLabel("Game: Not started")
        layout.addWidget(self.game_status_label)
        
        # Controller status
        self.controller_label = QLabel("Controller: Not connected")
        layout.addWidget(self.controller_label)
        
        # Serial stats
        self.serial_stats_label = QLabel("Serial: No data")
        layout.addWidget(self.serial_stats_label)
        
        return group
    
    def create_log_display(self) -> QGroupBox:
        """Create log display widget"""
        group = QGroupBox("Log")
        layout = QVBoxLayout(group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        font = QFont("Consolas", 8)
        self.log_text.setFont(font)
        layout.addWidget(self.log_text)
        
        return group
    
    def start_game(self) -> None:
        """Start the game"""
        if self.game_thread and self.game_thread.isRunning():
            return
        
        self.log("Starting game...")
        
        # Create and start game thread
        self.game_thread = GameThread(
            use_mock_serial=self.mock_serial_checkbox.isChecked(),
            serial_port=self.port_combo.currentText()
        )
        
        self.game_thread.matrix_updated.connect(self.update_matrix_display)
        self.game_thread.start()
        
        # Update button states
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        
        self.log("Game started")
    
    def pause_game(self) -> None:
        """Pause/unpause the game"""
        if self.game_thread and self.game_thread.app:
            self.game_thread.app.paused = not self.game_thread.app.paused
            status = "paused" if self.game_thread.app.paused else "unpaused"
            self.log(f"Game {status}")
    
    def stop_game(self) -> None:
        """Stop the game"""
        if self.game_thread:
            self.log("Stopping game...")
            self.game_thread.stop_game()
            self.game_thread.wait(3000)  # Wait up to 3 seconds
            
            if self.game_thread.isRunning():
                self.game_thread.terminate()
                self.log("Game thread terminated forcefully")
            else:
                self.log("Game stopped")
        
        # Update button states
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        # Clear display
        self.matrix_widget.clear_matrix()
    
    def fps_changed(self, value: int) -> None:
        """Handle FPS change"""
        if self.game_thread and self.game_thread.app:
            self.game_thread.app.set_fps(value)
            self.log(f"FPS set to {value}")
    
    def send_test_pattern(self) -> None:
        """Send test pattern to display"""
        if self.game_thread and self.game_thread.app and self.game_thread.app.serial.connected:
            pattern = self.test_pattern_combo.currentText()
            self.game_thread.app.serial.send_test_pattern(pattern)
            self.log(f"Sent test pattern: {pattern}")
        else:
            self.log("Cannot send test pattern: game not running or serial not connected")
    
    def clear_display(self) -> None:
        """Clear the display"""
        if self.game_thread and self.game_thread.app and self.game_thread.app.serial.connected:
            self.game_thread.app.serial.clear_display()
            self.log("Display cleared")
        else:
            self.matrix_widget.clear_matrix()
    
    def refresh_serial_ports(self) -> None:
        """Refresh available serial ports"""
        # This would normally scan for available ports
        # For now, just add some common ones
        self.port_combo.clear()
        self.port_combo.addItems([
            "COM1", "COM2", "COM3", "COM4", "COM5",
            "/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0", "/dev/ttyACM1"
        ])
        self.log("Serial ports refreshed")
    
    def update_matrix_display(self, matrix: List[List[List[int]]]) -> None:
        """Update the matrix display widget"""
        self.matrix_widget.set_matrix(matrix)
    
    def update_status(self) -> None:
        """Update status displays"""
        if not self.game_thread or not self.game_thread.app:
            return
        
        app = self.game_thread.app
        
        # Update FPS
        self.fps_label.setText(f"FPS: {app.current_fps:.1f}")
        
        # Update game status
        world_status = app.world.get_status()
        game_text = f"Level: {world_status['level']}, Score: {world_status['score']}"
        if world_status['game_over']:
            game_text += " [GAME OVER]"
        elif world_status['level_complete']:
            game_text += " [LEVEL COMPLETE]"
        self.game_status_label.setText(game_text)
        
        # Update controller status
        if app.controller.is_connected():
            controller_info = app.controller.get_controller_info()
            self.controller_label.setText(f"Controller: {controller_info['name']}")
        else:
            self.controller_label.setText("Controller: Not connected")
        
        # Update serial status
        serial_status = app.serial.get_status()
        if serial_status['connected']:
            self.connection_status.setText("Connected")
            self.connection_status.setStyleSheet("color: green")
            stats_text = f"Frames: {serial_status['frames_sent']}, FPS: {serial_status['fps']:.1f}"
            self.serial_stats_label.setText(stats_text)
        else:
            self.connection_status.setText("Disconnected")
            self.connection_status.setStyleSheet("color: red")
            self.serial_stats_label.setText("Serial: Disconnected")
    
    def log(self, message: str) -> None:
        """Add message to log"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.End)
        self.log_text.setTextCursor(cursor)
    
    def closeEvent(self, event) -> None:
        """Handle window close"""
        self.stop_game()
        event.accept()

def run_gui():
    """Run the GUI application"""
    app = QApplication(sys.argv)
    window = MatrixMarioGUI()
    window.show()
    sys.exit(app.exec_())