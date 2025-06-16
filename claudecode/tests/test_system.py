#!/usr/bin/env python3
"""
System integration tests for Matrix Mario
"""
import sys
import os
import time
import unittest

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.controller.ps5_controller import PS5ControllerHandler
from src.game_logic.world import GameWorld
from src.game_logic.mario import Mario
from src.renderer.matrix_renderer import MatrixRenderer
from src.serial_comm.serial_transmitter import MockSerialTransmitter
from src.utils.helpers import create_empty_matrix, matrix_to_serial_data
from src.config.settings import MATRIX_WIDTH, MATRIX_HEIGHT, COLORS

class TestSystemIntegration(unittest.TestCase):
    """Test system integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.renderer = MatrixRenderer()
        self.world = GameWorld()
        self.serial = MockSerialTransmitter()
        
    def test_matrix_creation(self):
        """Test basic matrix operations"""
        matrix = create_empty_matrix(MATRIX_WIDTH, MATRIX_HEIGHT)
        self.assertEqual(len(matrix), MATRIX_HEIGHT)
        self.assertEqual(len(matrix[0]), MATRIX_WIDTH)
        self.assertEqual(matrix[0][0], [0, 0, 0])
    
    def test_renderer(self):
        """Test matrix renderer"""
        # Test empty render
        matrix = self.renderer.render_frame(self.world)
        self.assertEqual(len(matrix), MATRIX_HEIGHT)
        self.assertEqual(len(matrix[0]), MATRIX_WIDTH)
        
        # Test test pattern
        test_matrix = self.renderer.render_test_pattern()
        self.assertEqual(len(test_matrix), MATRIX_HEIGHT)
        self.assertEqual(len(test_matrix[0]), MATRIX_WIDTH)
        
        # Check that test pattern has some non-black pixels
        has_colored_pixels = False
        for row in test_matrix:
            for pixel in row:
                if pixel != [0, 0, 0]:
                    has_colored_pixels = True
                    break
        self.assertTrue(has_colored_pixels, "Test pattern should have colored pixels")
    
    def test_mario(self):
        """Test Mario character"""
        mario = Mario(10, 10)
        
        # Test initial state
        self.assertEqual(mario.state, "small")
        self.assertEqual(mario.lives, 3)
        self.assertEqual(mario.score, 0)
        
        # Test movement
        initial_x = mario.x
        mario.move_right()
        mario.update(1.0)
        self.assertGreater(mario.vx, 0)
        
        # Test jumping
        initial_y = mario.y
        jump_success = mario.jump()
        self.assertTrue(jump_success)
        self.assertLess(mario.vy, 0)
        
        # Test power-up
        mario.grow()
        self.assertEqual(mario.state, "big")
        
        # Test damage
        died = mario.take_damage()
        self.assertFalse(died)  # Should not die from big state
        self.assertEqual(mario.state, "small")
    
    def test_world(self):
        """Test game world"""
        # Test initial state
        self.assertIsNotNone(self.world.mario)
        self.assertFalse(self.world.game_over)
        self.assertFalse(self.world.level_complete)
        
        # Test world update
        initial_frame_count = 0
        for _ in range(10):
            self.world.update(1.0/30.0)  # 30 FPS
            initial_frame_count += 1
        
        # Test reset
        self.world.reset()
        self.assertIsNotNone(self.world.mario)
        self.assertFalse(self.world.game_over)
    
    def test_mock_serial(self):
        """Test mock serial transmitter"""
        # Test connection
        self.assertTrue(self.serial.connect())
        self.assertTrue(self.serial.connected)
        
        # Test frame sending
        matrix = create_empty_matrix(MATRIX_WIDTH, MATRIX_HEIGHT)
        # Make some pixels colored
        matrix[0][0] = COLORS['RED']
        matrix[1][1] = COLORS['GREEN']
        matrix[2][2] = COLORS['BLUE']
        
        success = self.serial.send_frame_blocking(matrix)
        self.assertTrue(success)
        
        # Check that frame was stored
        frames = self.serial.get_mock_frames()
        self.assertEqual(len(frames), 1)
        
        # Test frame data format
        frame_data = frames[0]
        self.assertGreater(len(frame_data), MATRIX_WIDTH * MATRIX_HEIGHT * 3)
        
        # Test disconnection
        self.serial.disconnect()
        self.assertFalse(self.serial.connected)
    
    def test_serial_data_format(self):
        """Test serial data format"""
        matrix = create_empty_matrix(MATRIX_WIDTH, MATRIX_HEIGHT)
        matrix[0][0] = [255, 0, 0]  # Red pixel
        matrix[1][1] = [0, 255, 0]  # Green pixel
        
        data = matrix_to_serial_data(matrix)
        
        # Check frame markers
        self.assertEqual(data[:2], b'\\xFF\\xFE')  # Start marker
        self.assertEqual(data[-2:], b'\\xFD\\xFC')  # End marker
        
        # Check data length
        expected_length = 2 + (MATRIX_WIDTH * MATRIX_HEIGHT * 3) + 2
        self.assertEqual(len(data), expected_length)
        
        # Check specific pixel data
        rgb_data = data[2:-2]  # Remove markers
        # First pixel should be red
        self.assertEqual(rgb_data[0], 255)  # R
        self.assertEqual(rgb_data[1], 0)    # G
        self.assertEqual(rgb_data[2], 0)    # B
    
    def test_full_integration(self):
        """Test full system integration"""
        # Connect mock serial
        self.serial.connect()
        
        # Simulate game loop
        for frame in range(30):  # 1 second at 30 FPS
            # Update world
            self.world.update(1.0/30.0)
            
            # Render frame
            matrix = self.renderer.render_frame(self.world)
            
            # Send to "hardware"
            success = self.serial.send_frame_blocking(matrix)
            self.assertTrue(success)
        
        # Check that frames were sent
        frames = self.serial.get_mock_frames()
        self.assertEqual(len(frames), 30)
        
        # Disconnect
        self.serial.disconnect()

def run_performance_test():
    """Run performance test"""
    print("\\nRunning performance test...")
    
    renderer = MatrixRenderer()
    world = GameWorld()
    serial = MockSerialTransmitter()
    serial.connect()
    
    # Measure rendering performance
    start_time = time.time()
    frame_count = 300  # 10 seconds at 30 FPS
    
    for frame in range(frame_count):
        world.update(1.0/30.0)
        matrix = renderer.render_frame(world)
        serial.send_frame_blocking(matrix)
    
    end_time = time.time()
    elapsed = end_time - start_time
    avg_fps = frame_count / elapsed
    
    print(f"Rendered {frame_count} frames in {elapsed:.2f} seconds")
    print(f"Average FPS: {avg_fps:.1f}")
    print(f"Target FPS: 30")
    
    if avg_fps >= 30:
        print("✓ Performance test PASSED")
    else:
        print("⚠ Performance test WARNING: Below target FPS")
    
    serial.disconnect()

def run_controller_test():
    """Test controller (if available)"""
    print("\\nTesting controller...")
    
    try:
        controller = PS5ControllerHandler()
        
        if controller.is_connected():
            info = controller.get_controller_info()
            print(f"✓ Controller detected: {info['name']}")
            
            # Test input for 3 seconds
            print("Testing controller input for 3 seconds...")
            print("Try moving the left stick and pressing buttons...")
            
            start_time = time.time()
            while time.time() - start_time < 3:
                controller.update()
                
                if controller.is_pressed('left'):
                    print("Left detected")
                if controller.is_pressed('right'):
                    print("Right detected")
                if controller.is_just_pressed('jump'):
                    print("Jump pressed")
                if controller.is_just_pressed('attack'):
                    print("Attack pressed")
                
                time.sleep(0.1)
            
            print("✓ Controller test completed")
        else:
            print("⚠ No controller detected")
            print("  Connect a PS5 controller for full testing")
        
        controller.disconnect()
        
    except Exception as e:
        print(f"⚠ Controller test failed: {e}")

if __name__ == '__main__':
    print("Matrix Mario System Tests")
    print("=" * 40)
    
    # Run unit tests
    print("Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance test
    run_performance_test()
    
    # Run controller test
    run_controller_test()
    
    print("\\n" + "=" * 40)
    print("All tests completed!")
    print("\\nTo run the actual game:")
    print("  python run_console.py --mock-serial")
    print("  python run_gui.py")