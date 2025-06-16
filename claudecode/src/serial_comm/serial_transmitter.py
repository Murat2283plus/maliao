"""
Serial communication module for transmitting RGB matrix data to hardware
"""
import serial
import time
import threading
from typing import List, Optional, Callable
from queue import Queue, Empty
from ..config.settings import SERIAL_PORT, BAUD_RATE, TIMEOUT, MATRIX_WIDTH, MATRIX_HEIGHT
from ..utils.helpers import matrix_to_serial_data

class SerialTransmitter:
    """Handles serial communication with RGB matrix hardware"""
    
    def __init__(self, port: str = SERIAL_PORT, baud_rate: int = BAUD_RATE):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = TIMEOUT
        
        # Serial connection
        self.serial_connection: Optional[serial.Serial] = None
        self.connected = False
        
        # Threading for non-blocking transmission
        self.transmit_thread: Optional[threading.Thread] = None
        self.frame_queue = Queue(maxsize=10)  # Buffer for frames
        self.running = False
        
        # Statistics
        self.frames_sent = 0
        self.bytes_sent = 0
        self.transmission_errors = 0
        self.last_frame_time = 0
        
        # Callbacks
        self.on_connected: Optional[Callable] = None
        self.on_disconnected: Optional[Callable] = None
        self.on_error: Optional[Callable[[str], None]] = None
    
    def connect(self) -> bool:
        """Connect to serial port"""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=self.timeout,
                write_timeout=self.timeout
            )
            
            # Test connection with a ping
            if self._test_connection():
                self.connected = True
                print(f"Connected to serial port: {self.port} at {self.baud_rate} baud")
                
                # Start transmission thread
                self._start_transmission_thread()
                
                if self.on_connected:
                    self.on_connected()
                
                return True
            else:
                self.serial_connection.close()
                self.serial_connection = None
                return False
                
        except Exception as e:
            error_msg = f"Failed to connect to {self.port}: {e}"
            print(error_msg)
            if self.on_error:
                self.on_error(error_msg)
            return False
    
    def disconnect(self) -> None:
        """Disconnect from serial port"""
        self.running = False
        
        # Wait for transmission thread to finish
        if self.transmit_thread and self.transmit_thread.is_alive():
            self.transmit_thread.join(timeout=1.0)
        
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.serial_connection = None
        
        self.connected = False
        print("Disconnected from serial port")
        
        if self.on_disconnected:
            self.on_disconnected()
    
    def _test_connection(self) -> bool:
        """Test serial connection with a simple ping"""
        if not self.serial_connection:
            return False
        
        try:
            # Send a simple test pattern
            test_data = b'\\xFF\\xFE\\x00\\x00\\x00\\xFD\\xFC'  # Simple test frame
            self.serial_connection.write(test_data)
            self.serial_connection.flush()
            
            # Wait a bit for any response (optional)
            time.sleep(0.1)
            
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def _start_transmission_thread(self) -> None:
        """Start the transmission thread"""
        self.running = True
        self.transmit_thread = threading.Thread(
            target=self._transmission_worker,
            daemon=True
        )
        self.transmit_thread.start()
    
    def _transmission_worker(self) -> None:
        """Worker thread for transmitting frames"""
        while self.running and self.connected:
            try:
                # Get frame from queue (blocking with timeout)
                frame_data = self.frame_queue.get(timeout=0.1)
                
                if frame_data and self.serial_connection:
                    success = self._send_frame_data(frame_data)
                    if success:
                        self.frames_sent += 1
                        self.last_frame_time = time.time()
                    else:
                        self.transmission_errors += 1
                
                self.frame_queue.task_done()
                
            except Empty:
                # No frame in queue, continue
                continue
            except Exception as e:
                print(f"Transmission error: {e}")
                self.transmission_errors += 1
                if self.on_error:
                    self.on_error(f"Transmission error: {e}")
    
    def _send_frame_data(self, frame_data: bytes) -> bool:
        """Send frame data to serial port"""
        try:
            if not self.serial_connection or not self.serial_connection.is_open:
                return False
            
            self.serial_connection.write(frame_data)
            self.serial_connection.flush()
            self.bytes_sent += len(frame_data)
            
            return True
            
        except Exception as e:
            print(f"Failed to send frame: {e}")
            if self.on_error:
                self.on_error(f"Failed to send frame: {e}")
            return False
    
    def send_frame(self, matrix: List[List[List[int]]]) -> bool:
        """Send RGB matrix frame to hardware (non-blocking)"""
        if not self.connected:
            return False
        
        # Convert matrix to serial data format
        frame_data = matrix_to_serial_data(matrix)
        
        try:
            # Add frame to queue (non-blocking)
            self.frame_queue.put_nowait(frame_data)
            return True
        except:
            # Queue is full, drop frame
            print("Frame queue full, dropping frame")
            return False
    
    def send_frame_blocking(self, matrix: List[List[List[int]]]) -> bool:
        """Send RGB matrix frame to hardware (blocking)"""
        if not self.connected or not self.serial_connection:
            return False
        
        # Convert matrix to serial data format
        frame_data = matrix_to_serial_data(matrix)
        
        return self._send_frame_data(frame_data)
    
    def send_test_pattern(self, pattern_type: str = "checkerboard") -> bool:
        """Send a test pattern to the matrix"""
        from ..config.settings import COLORS
        
        # Create test pattern
        matrix = []
        for y in range(MATRIX_HEIGHT):
            row = []
            for x in range(MATRIX_WIDTH):
                if pattern_type == "checkerboard":
                    if (x + y) % 2 == 0:
                        color = COLORS['WHITE']
                    else:
                        color = COLORS['BLACK']
                elif pattern_type == "rainbow":
                    hue = (x + y) % 7
                    colors = [COLORS['RED'], COLORS['ORANGE'], COLORS['YELLOW'], 
                             COLORS['GREEN'], COLORS['CYAN'], COLORS['BLUE'], COLORS['PURPLE']]
                    color = colors[hue]
                elif pattern_type == "solid_red":
                    color = COLORS['RED']
                elif pattern_type == "solid_green":
                    color = COLORS['GREEN']
                elif pattern_type == "solid_blue":
                    color = COLORS['BLUE']
                else:  # black
                    color = COLORS['BLACK']
                
                row.append(color)
            matrix.append(row)
        
        return self.send_frame_blocking(matrix)
    
    def clear_display(self) -> bool:
        """Clear the display (send all black)"""
        return self.send_test_pattern("black")
    
    def get_available_ports(self) -> List[str]:
        """Get list of available serial ports"""
        import serial.tools.list_ports
        
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.device)
        
        return ports
    
    def set_port(self, port: str) -> None:
        """Set serial port (requires reconnection)"""
        if self.connected:
            print("Must disconnect before changing port")
            return
        
        self.port = port
    
    def set_baud_rate(self, baud_rate: int) -> None:
        """Set baud rate (requires reconnection)"""
        if self.connected:
            print("Must disconnect before changing baud rate")
            return
        
        self.baud_rate = baud_rate
    
    def get_status(self) -> dict:
        """Get transmitter status"""
        return {
            'connected': self.connected,
            'port': self.port,
            'baud_rate': self.baud_rate,
            'frames_sent': self.frames_sent,
            'bytes_sent': self.bytes_sent,
            'transmission_errors': self.transmission_errors,
            'queue_size': self.frame_queue.qsize(),
            'last_frame_time': self.last_frame_time,
            'fps': self._calculate_fps()
        }
    
    def _calculate_fps(self) -> float:
        """Calculate approximate FPS"""
        if self.frames_sent < 2:
            return 0.0
        
        current_time = time.time()
        if hasattr(self, '_start_time'):
            elapsed = current_time - self._start_time
            if elapsed > 0:
                return self.frames_sent / elapsed
        else:
            self._start_time = current_time
        
        return 0.0
    
    def reset_statistics(self) -> None:
        """Reset transmission statistics"""
        self.frames_sent = 0
        self.bytes_sent = 0
        self.transmission_errors = 0
        self.last_frame_time = 0
        self._start_time = time.time()

class MockSerialTransmitter(SerialTransmitter):
    """Mock serial transmitter for testing without hardware"""
    
    def __init__(self, port: str = "MOCK", baud_rate: int = BAUD_RATE):
        super().__init__(port, baud_rate)
        self.mock_connected = False
        self.mock_frames = []  # Store sent frames for testing
    
    def connect(self) -> bool:
        """Mock connection"""
        self.mock_connected = True
        self.connected = True
        print(f"Mock connected to {self.port}")
        
        # Start mock transmission thread
        self._start_transmission_thread()
        
        if self.on_connected:
            self.on_connected()
        
        return True
    
    def disconnect(self) -> None:
        """Mock disconnection"""
        self.running = False
        self.mock_connected = False
        self.connected = False
        print("Mock disconnected")
        
        if self.on_disconnected:
            self.on_disconnected()
    
    def _send_frame_data(self, frame_data: bytes) -> bool:
        """Mock frame sending"""
        # Just store the frame for testing
        self.mock_frames.append(frame_data)
        self.bytes_sent += len(frame_data)
        
        # Simulate some transmission time
        time.sleep(0.001)
        
        return True
    
    def get_mock_frames(self) -> List[bytes]:
        """Get stored mock frames for testing"""
        return self.mock_frames.copy()
    
    def clear_mock_frames(self) -> None:
        """Clear stored mock frames"""
        self.mock_frames.clear()