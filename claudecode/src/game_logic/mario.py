"""
Mario character class for Matrix Mario Game
"""
from typing import List
from .sprite import DynamicSprite
from ..config.settings import (
    COLORS, MARIO_WIDTH, MARIO_HEIGHT, MARIO_SPEED, 
    JUMP_POWER, GRAVITY, MATRIX_HEIGHT, GROUND_HEIGHT
)

class Mario(DynamicSprite):
    """Mario character with all game mechanics"""
    
    def __init__(self, x: int, y: int):
        super().__init__(x, y, MARIO_WIDTH, MARIO_HEIGHT, COLORS['MARIO_HAT'])
        
        # Mario states
        self.state = "small"  # small, big, fire
        self.direction = 1  # 1 for right, -1 for left
        self.on_ground = True
        self.jump_timer = 0
        self.invincible = False
        self.invincible_timer = 0
        self.lives = 3
        self.score = 0
        
        # Movement properties
        self.max_speed = MARIO_SPEED
        self.jump_power = JUMP_POWER
        self.acceleration = 0.5
        self.friction = 0.8
        
        # Animation
        self.animation_frame = 0
        self.animation_timer = 0
        
        # Start Mario at ground level
        self.y = MATRIX_HEIGHT - GROUND_HEIGHT - self.height
    
    def update(self, dt: float) -> None:
        """Update Mario's state and physics"""
        if not self.active:
            return
        
        # Handle invincibility
        if self.invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # Apply gravity
        if not self.on_ground and self.gravity_enabled:
            self.vy += GRAVITY
            self.vy = min(self.vy, 10)  # Terminal velocity
        
        # Apply friction
        self.vx *= self.friction
        if abs(self.vx) < 0.1:
            self.vx = 0
        
        # Update jump timer
        if self.jump_timer > 0:
            self.jump_timer -= dt
        
        # Update animation
        self.animation_timer += dt
        if self.animation_timer >= 0.2:  # 5 FPS animation
            self.animation_frame = (self.animation_frame + 1) % 3
            self.animation_timer = 0
        
        # Check ground collision (simple ground at bottom)
        ground_y = MATRIX_HEIGHT - GROUND_HEIGHT
        if self.y + self.height >= ground_y:
            self.y = ground_y - self.height
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False
        
        # Update position
        super().update(dt)
    
    def move_left(self) -> None:
        """Move Mario left"""
        self.direction = -1
        self.vx = max(self.vx - self.acceleration, -self.max_speed)
    
    def move_right(self) -> None:
        """Move Mario right"""
        self.direction = 1
        self.vx = min(self.vx + self.acceleration, self.max_speed)
    
    def jump(self) -> bool:
        """Make Mario jump (returns True if jump was successful)"""
        if self.on_ground and self.jump_timer <= 0:
            self.vy = -self.jump_power
            self.on_ground = False
            self.jump_timer = 0.5  # Prevent multiple jumps
            return True
        return False
    
    def grow(self) -> None:
        """Grow Mario (power-up)"""
        if self.state == "small":
            self.state = "big"
            old_height = self.height
            self.height = MARIO_HEIGHT + 1
            self.y -= (self.height - old_height)  # Adjust position
            self.color = COLORS['MARIO_SHIRT']
    
    def get_fire_power(self) -> None:
        """Give Mario fire power"""
        if self.state != "fire":
            if self.state == "small":
                self.grow()
            self.state = "fire"
            self.color = COLORS['WHITE']
    
    def take_damage(self) -> bool:
        """Take damage (returns True if Mario dies)"""
        if self.invincible:
            return False
        
        if self.state == "fire":
            self.state = "big"
            self.color = COLORS['MARIO_SHIRT']
            self.make_invincible()
            return False
        elif self.state == "big":
            self.state = "small"
            self.height = MARIO_HEIGHT
            self.color = COLORS['MARIO_HAT']
            self.make_invincible()
            return False
        else:  # small Mario
            self.die()
            return True
    
    def make_invincible(self, duration: float = 2.0) -> None:
        """Make Mario invincible for a short time"""
        self.invincible = True
        self.invincible_timer = duration
    
    def die(self) -> None:
        """Mario dies"""
        self.lives -= 1
        self.vx = 0
        self.vy = -5  # Death animation
        self.gravity_enabled = False
        if self.lives <= 0:
            self.active = False
    
    def respawn(self, x: int, y: int) -> None:
        """Respawn Mario at given position"""
        if self.lives > 0:
            self.x = x
            self.y = y
            self.vx = 0
            self.vy = 0
            self.state = "small"
            self.height = MARIO_HEIGHT
            self.color = COLORS['MARIO_HAT']
            self.on_ground = False
            self.gravity_enabled = True
            self.invincible = False
            self.invincible_timer = 0
    
    def add_score(self, points: int) -> None:
        """Add points to Mario's score"""
        self.score += points
    
    def get_animation_color(self) -> List[int]:
        """Get Mario's current color for animation"""
        if self.invincible and int(self.invincible_timer * 10) % 2:
            return COLORS['WHITE']  # Flashing effect
        
        # Different colors based on movement and state
        if self.vx != 0:  # Moving
            if self.animation_frame == 1:
                return self.color
            else:
                # Slightly different shade for animation
                return [max(0, c - 30) for c in self.color]
        else:  # Standing still
            return self.color
    
    def get_status(self) -> dict:
        """Get Mario's current status"""
        return {
            'state': self.state,
            'position': (self.x, self.y),
            'velocity': (self.vx, self.vy),
            'on_ground': self.on_ground,
            'direction': self.direction,
            'lives': self.lives,
            'score': self.score,
            'invincible': self.invincible,
            'active': self.active
        }