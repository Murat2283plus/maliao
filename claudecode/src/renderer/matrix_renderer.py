"""
Matrix Renderer for converting game world to 36x28 RGB matrix
"""
from typing import List, Tuple
from ..game_logic.sprite import Sprite
from ..game_logic.world import GameWorld
from ..config.settings import MATRIX_WIDTH, MATRIX_HEIGHT, COLORS, GROUND_HEIGHT
from ..utils.helpers import create_empty_matrix, draw_rect, draw_pixel

class MatrixRenderer:
    """Renders game world to RGB matrix format"""
    
    def __init__(self):
        self.width = MATRIX_WIDTH
        self.height = MATRIX_HEIGHT
        self.background_color = COLORS['BLACK']
        self.ground_color = COLORS['GREEN']
        
        # Frame buffer
        self.frame_buffer = create_empty_matrix(self.width, self.height)
        
        # Debug mode for rendering sprite bounds
        self.debug_mode = False
    
    def render_frame(self, world: GameWorld) -> List[List[List[int]]]:
        """Render a complete frame from the game world"""
        # Clear frame buffer
        self._clear_frame()
        
        # Draw background elements
        self._draw_background()
        
        # Get visible sprites from world
        sprites = world.get_visible_sprites()
        
        # Sort sprites by layer (background to foreground)
        sprites.sort(key=lambda s: self._get_sprite_layer(s))
        
        # Render each sprite
        for sprite in sprites:
            self._render_sprite(sprite, world.camera_x)
        
        # Draw UI elements
        self._draw_ui(world)
        
        return self.frame_buffer
    
    def _clear_frame(self) -> None:
        """Clear the frame buffer"""
        for y in range(self.height):
            for x in range(self.width):
                self.frame_buffer[y][x] = self.background_color.copy()
    
    def _draw_background(self) -> None:
        """Draw background elements like ground"""
        # Draw ground line
        ground_y = self.height - GROUND_HEIGHT
        for x in range(self.width):
            draw_pixel(self.frame_buffer, x, ground_y, 
                      self.ground_color, self.width, self.height)
    
    def _get_sprite_layer(self, sprite: Sprite) -> int:
        """Get rendering layer for sprite (lower numbers render first)"""
        from ..game_logic.mario import Mario
        from ..game_logic.world import Coin, Enemy, Brick, Platform
        
        if isinstance(sprite, Platform):
            return 1
        elif isinstance(sprite, Brick):
            return 2
        elif isinstance(sprite, Coin):
            return 3
        elif isinstance(sprite, Enemy):
            return 4
        elif isinstance(sprite, Mario):
            return 5  # Mario renders on top
        else:
            return 0
    
    def _render_sprite(self, sprite: Sprite, camera_x: int) -> None:
        """Render a single sprite to the frame buffer"""
        if not sprite.visible or not sprite.active:
            return
        
        # Apply camera offset
        screen_x = sprite.x - camera_x
        screen_y = sprite.y
        
        # Skip if sprite is outside screen bounds
        if (screen_x + sprite.width < 0 or screen_x >= self.width or
            screen_y + sprite.height < 0 or screen_y >= self.height):
            return
        
        # Get sprite color (might be animated)
        color = self._get_sprite_color(sprite)
        
        # Render sprite as filled rectangle
        draw_rect(self.frame_buffer, screen_x, screen_y, 
                 sprite.width, sprite.height, color, 
                 self.width, self.height)
        
        # Draw debug bounds if enabled
        if self.debug_mode:
            self._draw_sprite_bounds(screen_x, screen_y, 
                                   sprite.width, sprite.height)
    
    def _get_sprite_color(self, sprite: Sprite) -> List[int]:
        """Get the current color for a sprite (handles animation)"""
        from ..game_logic.mario import Mario
        from ..game_logic.world import Coin
        
        if isinstance(sprite, Mario):
            return sprite.get_animation_color()
        elif isinstance(sprite, Coin):
            # Coin might have animated color
            return sprite.color
        else:
            return sprite.color
    
    def _draw_sprite_bounds(self, x: int, y: int, width: int, height: int) -> None:
        """Draw sprite bounds for debugging"""
        # Draw border pixels
        for i in range(width):
            draw_pixel(self.frame_buffer, x + i, y, COLORS['WHITE'], 
                      self.width, self.height)
            draw_pixel(self.frame_buffer, x + i, y + height - 1, COLORS['WHITE'], 
                      self.width, self.height)
        
        for i in range(height):
            draw_pixel(self.frame_buffer, x, y + i, COLORS['WHITE'], 
                      self.width, self.height)
            draw_pixel(self.frame_buffer, x + width - 1, y + i, COLORS['WHITE'], 
                      self.width, self.height)
    
    def _draw_ui(self, world: GameWorld) -> None:
        """Draw UI elements like score, lives"""
        if not world.mario:
            return
        
        # Draw lives indicator (small pixels in top-left)
        lives = world.mario.lives
        for i in range(min(lives, 5)):  # Max 5 life indicators
            draw_pixel(self.frame_buffer, i * 2, 0, COLORS['RED'], 
                      self.width, self.height)
        
        # Draw score as simple pixel patterns (optional, simplified)
        # This is very basic - in a real implementation you might want
        # a bitmap font or more sophisticated score display
        if world.score > 0:
            # Simple score indicator - more pixels = higher score
            score_level = min(world.score // 100, self.width - 1)
            for i in range(score_level):
                draw_pixel(self.frame_buffer, i, 1, COLORS['YELLOW'], 
                          self.width, self.height)
    
    def render_test_pattern(self) -> List[List[List[int]]]:
        """Render a test pattern for debugging"""
        self._clear_frame()
        
        # Draw border
        for x in range(self.width):
            draw_pixel(self.frame_buffer, x, 0, COLORS['WHITE'], 
                      self.width, self.height)
            draw_pixel(self.frame_buffer, x, self.height - 1, COLORS['WHITE'], 
                      self.width, self.height)
        
        for y in range(self.height):
            draw_pixel(self.frame_buffer, 0, y, COLORS['WHITE'], 
                      self.width, self.height)
            draw_pixel(self.frame_buffer, self.width - 1, y, COLORS['WHITE'], 
                      self.width, self.height)
        
        # Draw center cross
        center_x, center_y = self.width // 2, self.height // 2
        for i in range(5):
            draw_pixel(self.frame_buffer, center_x - 2 + i, center_y, 
                      COLORS['RED'], self.width, self.height)
            draw_pixel(self.frame_buffer, center_x, center_y - 2 + i, 
                      COLORS['RED'], self.width, self.height)
        
        # Draw corner markers
        colors = [COLORS['RED'], COLORS['GREEN'], COLORS['BLUE'], COLORS['YELLOW']]
        positions = [(1, 1), (self.width-2, 1), (1, self.height-2), (self.width-2, self.height-2)]
        
        for i, (x, y) in enumerate(positions):
            draw_pixel(self.frame_buffer, x, y, colors[i], 
                      self.width, self.height)
        
        return self.frame_buffer
    
    def render_text(self, text: str, x: int, y: int, color: List[int]) -> None:
        """Render simple text (very basic bitmap)"""
        # This is a very simplified text rendering
        # In a real implementation, you'd want proper bitmap fonts
        char_width = 3
        for i, char in enumerate(text[:10]):  # Limit to 10 chars
            char_x = x + i * char_width
            if char_x >= self.width:
                break
            
            # Very simple character patterns
            self._draw_character(char, char_x, y, color)
    
    def _draw_character(self, char: str, x: int, y: int, color: List[int]) -> None:
        """Draw a single character (very basic)"""
        # Simple 3x3 patterns for some characters
        patterns = {
            '0': [[1,1,1],[1,0,1],[1,1,1]],
            '1': [[0,1,0],[1,1,0],[0,1,0]],
            '2': [[1,1,1],[0,1,1],[1,1,1]],
            '3': [[1,1,1],[0,1,1],[1,1,1]],
            '4': [[1,0,1],[1,1,1],[0,0,1]],
            '5': [[1,1,1],[1,1,0],[1,1,1]],
            'G': [[1,1,1],[1,0,0],[1,1,1]],
            'O': [[1,1,1],[1,0,1],[1,1,1]],
            ' ': [[0,0,0],[0,0,0],[0,0,0]],
        }
        
        if char.upper() in patterns:
            pattern = patterns[char.upper()]
            for py, row in enumerate(pattern):
                for px, pixel in enumerate(row):
                    if pixel and y + py < self.height:
                        draw_pixel(self.frame_buffer, x + px, y + py, 
                                  color, self.width, self.height)
    
    def set_debug_mode(self, enabled: bool) -> None:
        """Enable/disable debug rendering"""
        self.debug_mode = enabled
    
    def get_frame_stats(self) -> dict:
        """Get statistics about the current frame"""
        pixel_count = {'black': 0, 'colored': 0}
        
        for row in self.frame_buffer:
            for pixel in row:
                if pixel == [0, 0, 0]:
                    pixel_count['black'] += 1
                else:
                    pixel_count['colored'] += 1
        
        return {
            'width': self.width,
            'height': self.height,
            'total_pixels': self.width * self.height,
            'pixel_count': pixel_count,
            'debug_mode': self.debug_mode
        }