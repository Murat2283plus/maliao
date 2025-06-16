"""
Base sprite classes for Matrix Mario Game
"""
from typing import List, Tuple
from ..config.settings import MATRIX_WIDTH, MATRIX_HEIGHT

class Sprite:
    """Base sprite class"""
    
    def __init__(self, x: int, y: int, width: int, height: int, color: List[int]):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.active = True
        self.visible = True
    
    def get_rect(self) -> Tuple[int, int, int, int]:
        """Get sprite rectangle (x, y, width, height)"""
        return (self.x, self.y, self.width, self.height)
    
    def is_collision(self, other: 'Sprite') -> bool:
        """Check collision with another sprite"""
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)
    
    def is_in_bounds(self) -> bool:
        """Check if sprite is within matrix bounds"""
        return (0 <= self.x < MATRIX_WIDTH and 0 <= self.y < MATRIX_HEIGHT)
    
    def update(self, dt: float) -> None:
        """Update sprite state"""
        pass
    
    def destroy(self) -> None:
        """Mark sprite for destruction"""
        self.active = False

class DynamicSprite(Sprite):
    """Sprite with physics (movement, gravity)"""
    
    def __init__(self, x: int, y: int, width: int, height: int, color: List[int]):
        super().__init__(x, y, width, height, color)
        self.vx = 0.0  # Velocity X
        self.vy = 0.0  # Velocity Y
        self.on_ground = False
        self.gravity_enabled = True
    
    def update(self, dt: float) -> None:
        """Update physics"""
        if not self.active:
            return
        
        # Apply velocity
        self.x += int(self.vx)
        self.y += int(self.vy)
        
        # Keep within bounds
        self.x = max(0, min(self.x, MATRIX_WIDTH - self.width))
        self.y = max(0, min(self.y, MATRIX_HEIGHT - self.height))

class StaticSprite(Sprite):
    """Static sprite (platforms, bricks, etc.)"""
    
    def __init__(self, x: int, y: int, width: int, height: int, color: List[int]):
        super().__init__(x, y, width, height, color)
        self.solid = True  # Can other sprites collide with this?