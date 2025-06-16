"""
PS5 Controller Handler for Matrix Mario Game
"""
import pygame
from typing import Optional, Dict, Any
from ..config.settings import CONTROLLER_DEADZONE

class PS5ControllerHandler:
    """Handle PS5 controller input for Mario game"""
    
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        
        self.controller: Optional[pygame.joystick.Joystick] = None
        self.connected = False
        
        # Button states
        self.button_states = {
            'left': False,
            'right': False,
            'jump': False,  # X button (cross)
            'attack': False,  # Square button
            'start': False,  # Options button
        }
        
        # Previous button states for edge detection
        self.prev_button_states = self.button_states.copy()
        
        # PS5 controller button mappings
        self.button_mapping = {
            0: 'attack',    # X button (cross) -> attack
            1: 'jump',      # Circle button -> jump  
            2: 'attack',    # Square button -> attack
            3: 'jump',      # Triangle button -> jump
            6: 'start',     # Share button
            9: 'start',     # Options button
        }
        
        self._connect_controller()
    
    def _connect_controller(self) -> bool:
        """Try to connect to a PS5 controller"""
        try:
            if pygame.joystick.get_count() > 0:
                self.controller = pygame.joystick.Joystick(0)
                self.controller.init()
                self.connected = True
                print(f"Connected to controller: {self.controller.get_name()}")
                return True
            else:
                print("No controller detected")
                return False
        except Exception as e:
            print(f"Error connecting controller: {e}")
            return False
    
    def update(self) -> None:
        """Update controller state"""
        if not self.connected:
            # Try to reconnect
            self._connect_controller()
            return
        
        # Store previous states
        self.prev_button_states = self.button_states.copy()
        
        # Process pygame events
        pygame.event.pump()
        
        try:
            # Read analog stick for left/right movement
            left_stick_x = self.controller.get_axis(0)  # Left stick horizontal
            
            # Apply deadzone
            if abs(left_stick_x) < CONTROLLER_DEADZONE:
                left_stick_x = 0
            
            # Update movement states
            self.button_states['left'] = left_stick_x < -CONTROLLER_DEADZONE
            self.button_states['right'] = left_stick_x > CONTROLLER_DEADZONE
            
            # Read D-pad for movement (alternative to analog stick)
            hat = self.controller.get_hat(0)
            if hat[0] != 0:  # D-pad horizontal
                self.button_states['left'] = hat[0] < 0
                self.button_states['right'] = hat[0] > 0
            
            # Read buttons
            for button_id, action in self.button_mapping.items():
                if button_id < self.controller.get_numbuttons():
                    self.button_states[action] = self.controller.get_button(button_id)
        
        except Exception as e:
            print(f"Error reading controller: {e}")
            self.connected = False
            self.controller = None
    
    def is_pressed(self, action: str) -> bool:
        """Check if a button/action is currently pressed"""
        return self.button_states.get(action, False)
    
    def is_just_pressed(self, action: str) -> bool:
        """Check if a button/action was just pressed (edge detection)"""
        return (self.button_states.get(action, False) and 
                not self.prev_button_states.get(action, False))
    
    def is_just_released(self, action: str) -> bool:
        """Check if a button/action was just released (edge detection)"""
        return (not self.button_states.get(action, False) and 
                self.prev_button_states.get(action, False))
    
    def get_movement_vector(self) -> tuple:
        """Get normalized movement vector (-1 to 1)"""
        x = 0
        if self.is_pressed('left'):
            x = -1
        elif self.is_pressed('right'):
            x = 1
        
        return x, 0  # No Y movement from controller for this game
    
    def is_connected(self) -> bool:
        """Check if controller is connected"""
        return self.connected
    
    def get_controller_info(self) -> Dict[str, Any]:
        """Get controller information"""
        if not self.connected or not self.controller:
            return {"connected": False}
        
        return {
            "connected": True,
            "name": self.controller.get_name(),
            "num_buttons": self.controller.get_numbuttons(),
            "num_axes": self.controller.get_numaxes(),
            "num_hats": self.controller.get_numhats(),
        }
    
    def disconnect(self) -> None:
        """Disconnect and cleanup controller"""
        if self.controller:
            self.controller.quit()
        self.connected = False
        self.controller = None
        pygame.joystick.quit()
        pygame.quit()