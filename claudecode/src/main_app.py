"""
Main Application for Matrix Mario Game
Coordinates all modules and runs the main game loop
"""
import time
import sys
import threading
from typing import Optional

from .controller.ps5_controller import PS5ControllerHandler
from .game_logic.world import GameWorld
from .renderer.matrix_renderer import MatrixRenderer
from .serial_comm.serial_transmitter import SerialTransmitter, MockSerialTransmitter
from .config.settings import GAME_FPS, SERIAL_PORT, BAUD_RATE

class MatrixMarioApp:
    """Main application class that coordinates all game systems"""
    
    def __init__(self, use_mock_serial: bool = False, serial_port: str = SERIAL_PORT):
        # Initialize all subsystems
        self.controller = PS5ControllerHandler()
        self.world = GameWorld()
        self.renderer = MatrixRenderer()
        
        # Serial transmitter (real or mock)
        if use_mock_serial:
            self.serial = MockSerialTransmitter()
        else:
            self.serial = SerialTransmitter(serial_port, BAUD_RATE)
        
        # Game loop control
        self.running = False
        self.paused = False
        self.target_fps = GAME_FPS
        self.frame_time = 1.0 / self.target_fps
        
        # Statistics
        self.frame_count = 0
        self.start_time = 0
        self.last_fps_update = 0
        self.current_fps = 0
        
        # Threading
        self.game_thread: Optional[threading.Thread] = None
        
        # Setup callbacks
        self._setup_serial_callbacks()
        
        print("Matrix Mario initialized")
        print(f"Target FPS: {self.target_fps}")
        print(f"Serial port: {serial_port}")
        print(f"Mock serial: {use_mock_serial}")
    
    def _setup_serial_callbacks(self) -> None:
        """Setup serial communication callbacks"""
        def on_connected():
            print("Serial connection established")
        
        def on_disconnected():
            print("Serial connection lost")
        
        def on_error(error_msg: str):
            print(f"Serial error: {error_msg}")
        
        self.serial.on_connected = on_connected
        self.serial.on_disconnected = on_disconnected
        self.serial.on_error = on_error
    
    def initialize(self) -> bool:
        """Initialize all subsystems"""
        print("Initializing Matrix Mario...")
        
        # Initialize controller
        if not self.controller.is_connected():
            print("Warning: No PS5 controller detected")
            print("Please connect a PS5 controller and restart")
        
        # Initialize serial connection
        if not self.serial.connect():
            print("Warning: Failed to connect to serial port")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return False
        
        # Send test pattern to verify connection
        if self.serial.connected:
            print("Sending test pattern...")
            self.serial.send_test_pattern("checkerboard")
            time.sleep(1)
            self.serial.clear_display()
        
        print("Initialization complete!")
        return True
    
    def start(self) -> None:
        """Start the game"""
        if not self.initialize():
            print("Failed to initialize. Exiting.")
            return
        
        print("Starting Matrix Mario game...")
        self.running = True
        self.start_time = time.time()
        self.last_fps_update = self.start_time
        
        # Start game in separate thread to allow for input handling
        self.game_thread = threading.Thread(target=self._game_loop, daemon=True)
        self.game_thread.start()
        
        # Run main thread for input handling
        self._input_loop()
    
    def stop(self) -> None:
        """Stop the game"""
        print("Stopping Matrix Mario...")
        self.running = False
        
        if self.game_thread and self.game_thread.is_alive():
            self.game_thread.join(timeout=2.0)
        
        # Cleanup
        self._cleanup()
        print("Game stopped")
    
    def _game_loop(self) -> None:
        """Main game loop running in separate thread"""
        frame_start_time = time.time()
        
        while self.running:
            loop_start = time.time()
            
            if not self.paused:
                # Calculate delta time
                dt = loop_start - frame_start_time
                frame_start_time = loop_start
                
                # Update game systems
                self._update(dt)
                
                # Render frame
                self._render()
                
                # Update statistics
                self._update_statistics()
            
            # Sleep to maintain target FPS
            elapsed = time.time() - loop_start
            sleep_time = max(0, self.frame_time - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def _update(self, dt: float) -> None:
        """Update all game systems"""
        # Update controller input
        self.controller.update()
        
        # Handle input
        self.world.handle_input(self.controller)
        
        # Update game world
        self.world.update(dt)
        
        # Check for game over or level complete
        if self.world.game_over:
            self._handle_game_over()
        elif self.world.level_complete:
            self._handle_level_complete()
    
    def _render(self) -> None:
        """Render and transmit frame"""
        # Render game world to matrix
        matrix = self.renderer.render_frame(self.world)
        
        # Send to hardware
        if self.serial.connected:
            self.serial.send_frame(matrix)
    
    def _update_statistics(self) -> None:
        """Update FPS and other statistics"""
        self.frame_count += 1
        current_time = time.time()
        
        # Update FPS every second
        if current_time - self.last_fps_update >= 1.0:
            elapsed = current_time - self.last_fps_update
            self.current_fps = self.frame_count / (current_time - self.start_time)
            self.last_fps_update = current_time
    
    def _input_loop(self) -> None:
        """Handle console input in main thread"""
        print("\\nGame Controls:")
        print("  PS5 Controller: Left stick/D-pad = move, X/Circle = jump, Square = attack")
        print("\\nConsole Commands:")
        print("  'p' = pause/unpause")
        print("  'r' = restart game")
        print("  's' = show status")
        print("  't' = send test pattern")
        print("  'q' = quit")
        print("  'h' = show help")
        print()
        
        while self.running:
            try:
                command = input().strip().lower()
                self._handle_console_command(command)
            except (EOFError, KeyboardInterrupt):
                break
        
        self.stop()
    
    def _handle_console_command(self, command: str) -> None:
        """Handle console commands"""
        if command == 'q' or command == 'quit':
            self.running = False
        elif command == 'p' or command == 'pause':
            self.paused = not self.paused
            print(f"Game {'paused' if self.paused else 'unpaused'}")
        elif command == 'r' or command == 'restart':
            self.restart_game()
        elif command == 's' or command == 'status':
            self.show_status()
        elif command == 't' or command == 'test':
            self.send_test_pattern()
        elif command == 'h' or command == 'help':
            self.show_help()
        elif command.startswith('fps '):
            try:
                new_fps = int(command.split()[1])
                self.set_fps(new_fps)
            except (ValueError, IndexError):
                print("Invalid FPS value. Usage: fps <number>")
        elif command == 'clear':
            if self.serial.connected:
                self.serial.clear_display()
                print("Display cleared")
        else:
            print(f"Unknown command: {command}. Type 'h' for help.")
    
    def restart_game(self) -> None:
        """Restart the game"""
        print("Restarting game...")
        self.world.reset()
        self.frame_count = 0
        self.start_time = time.time()
        print("Game restarted")
    
    def show_status(self) -> None:
        """Show current game status"""
        print("\\n=== Matrix Mario Status ===")
        print(f"Running: {self.running}")
        print(f"Paused: {self.paused}")
        print(f"FPS: {self.current_fps:.1f}")
        print(f"Frames: {self.frame_count}")
        
        # Controller status
        if self.controller.is_connected():
            controller_info = self.controller.get_controller_info()
            print(f"Controller: {controller_info['name']}")
        else:
            print("Controller: Not connected")
        
        # Serial status
        serial_status = self.serial.get_status()
        print(f"Serial: {'Connected' if serial_status['connected'] else 'Disconnected'}")
        print(f"Serial Port: {serial_status['port']}")
        print(f"Frames Sent: {serial_status['frames_sent']}")
        print(f"Serial FPS: {serial_status['fps']:.1f}")
        
        # Game status
        game_status = self.world.get_status()
        print(f"Level: {game_status['level']}")
        print(f"Score: {game_status['score']}")
        if game_status['mario_status']:
            mario = game_status['mario_status']
            print(f"Mario Lives: {mario['lives']}")
            print(f"Mario State: {mario['state']}")
            print(f"Mario Position: {mario['position']}")
        
        print("========================\\n")
    
    def send_test_pattern(self) -> None:
        """Send test pattern to display"""
        if not self.serial.connected:
            print("Serial not connected")
            return
        
        patterns = ["checkerboard", "rainbow", "solid_red", "solid_green", "solid_blue"]
        
        for pattern in patterns:
            print(f"Sending {pattern} pattern...")
            self.serial.send_test_pattern(pattern)
            time.sleep(1)
        
        print("Test patterns complete")
        self.serial.clear_display()
    
    def set_fps(self, fps: int) -> None:
        """Set target FPS"""
        if 1 <= fps <= 60:
            self.target_fps = fps
            self.frame_time = 1.0 / fps
            print(f"FPS set to {fps}")
        else:
            print("FPS must be between 1 and 60")
    
    def show_help(self) -> None:
        """Show help information"""
        print("\\n=== Matrix Mario Help ===")
        print("Game Controls (PS5 Controller):")
        print("  Left stick/D-pad: Move Mario left/right")
        print("  X or Circle button: Jump")
        print("  Square button: Attack (when Mario has fire power)")
        print()
        print("Console Commands:")
        print("  p, pause    - Pause/unpause the game")
        print("  r, restart  - Restart the current game")
        print("  s, status   - Show detailed status information")
        print("  t, test     - Send test patterns to display")
        print("  fps <num>   - Set target FPS (1-60)")
        print("  clear       - Clear the display")
        print("  h, help     - Show this help")
        print("  q, quit     - Quit the game")
        print("========================\\n")
    
    def _handle_game_over(self) -> None:
        """Handle game over state"""
        print("\\nGAME OVER!")
        print(f"Final Score: {self.world.score}")
        print("Press 'r' to restart or 'q' to quit")
        
        # Show game over pattern on display
        if self.serial.connected:
            # Flash red a few times
            for _ in range(3):
                self.serial.send_test_pattern("solid_red")
                time.sleep(0.3)
                self.serial.clear_display()
                time.sleep(0.3)
    
    def _handle_level_complete(self) -> None:
        """Handle level completion"""
        print("\\nLEVEL COMPLETE!")
        print(f"Score: {self.world.score}")
        
        # Show celebration pattern
        if self.serial.connected:
            self.serial.send_test_pattern("rainbow")
            time.sleep(2)
        
        # For now, just restart (could load next level)
        self.restart_game()
    
    def _cleanup(self) -> None:
        """Clean up resources"""
        if self.serial.connected:
            self.serial.clear_display()
            self.serial.disconnect()
        
        self.controller.disconnect()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Matrix Mario - 36x28 RGB Matrix Game')
    parser.add_argument('--mock-serial', action='store_true', 
                       help='Use mock serial (for testing without hardware)')
    parser.add_argument('--serial-port', default=SERIAL_PORT,
                       help='Serial port for matrix communication')
    parser.add_argument('--fps', type=int, default=GAME_FPS,
                       help='Target FPS (1-60)')
    
    args = parser.parse_args()
    
    # Create and start the application
    app = MatrixMarioApp(
        use_mock_serial=args.mock_serial,
        serial_port=args.serial_port
    )
    
    if args.fps != GAME_FPS:
        app.set_fps(args.fps)
    
    try:
        app.start()
    except KeyboardInterrupt:
        print("\\nReceived interrupt signal")
    finally:
        app.stop()

if __name__ == '__main__':
    main()