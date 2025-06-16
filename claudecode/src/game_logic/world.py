"""
Game world and level management for Matrix Mario Game
"""
from typing import List, Tuple, Optional
from .sprite import Sprite, StaticSprite, DynamicSprite
from .mario import Mario
from ..config.settings import (
    COLORS, MATRIX_WIDTH, MATRIX_HEIGHT, GROUND_HEIGHT, 
    BRICK_SIZE, COIN_SIZE
)

class Brick(StaticSprite):
    """Destructible brick block"""
    
    def __init__(self, x: int, y: int):
        super().__init__(x, y, BRICK_SIZE, BRICK_SIZE, COLORS['BRICK'])
        self.destructible = True
        self.hit_count = 0
    
    def hit(self) -> bool:
        """Hit the brick (returns True if destroyed)"""
        self.hit_count += 1
        if self.hit_count >= 1:  # Single hit destroys
            self.destroy()
            return True
        return False

class Platform(StaticSprite):
    """Solid platform"""
    
    def __init__(self, x: int, y: int, width: int):
        super().__init__(x, y, width, 1, COLORS['GREEN'])
        self.solid = True

class Coin(DynamicSprite):
    """Collectible coin"""
    
    def __init__(self, x: int, y: int):
        super().__init__(x, y, COIN_SIZE, COIN_SIZE, COLORS['COIN'])
        self.points = 100
        self.animation_timer = 0
    
    def update(self, dt: float) -> None:
        """Animate coin"""
        self.animation_timer += dt
        if self.animation_timer >= 0.5:
            # Simple color animation
            if self.color == COLORS['COIN']:
                self.color = COLORS['YELLOW']
            else:
                self.color = COLORS['COIN']
            self.animation_timer = 0

class Enemy(DynamicSprite):
    """Simple enemy (goomba-like)"""
    
    def __init__(self, x: int, y: int):
        super().__init__(x, y, 2, 2, COLORS['BROWN'])
        self.speed = 1
        self.direction = -1  # Start moving left
        self.vx = self.speed * self.direction
        self.points = 200
    
    def update(self, dt: float) -> None:
        """Update enemy movement"""
        super().update(dt)
        
        # Simple AI: change direction at edges or walls
        if self.x <= 0 or self.x >= MATRIX_WIDTH - self.width:
            self.direction *= -1
            self.vx = self.speed * self.direction
        
        # Apply gravity (simple ground check)
        ground_y = MATRIX_HEIGHT - GROUND_HEIGHT
        if self.y + self.height >= ground_y:
            self.y = ground_y - self.height
            self.vy = 0
        else:
            self.vy += 0.3  # Gravity
    
    def stomp(self) -> int:
        """Enemy gets stomped (returns points)"""
        self.destroy()
        return self.points

class GameWorld:
    """Manages the game world, sprites, and physics"""
    
    def __init__(self):
        self.mario: Optional[Mario] = None
        self.static_sprites: List[StaticSprite] = []
        self.dynamic_sprites: List[DynamicSprite] = []
        self.camera_x = 0  # Simple camera following Mario
        
        # Game state
        self.level = 1
        self.game_over = False
        self.level_complete = False
        self.score = 0
        
        self._create_level_1()
    
    def _create_level_1(self) -> None:
        """Create level 1 layout"""
        # Create Mario
        self.mario = Mario(3, 0)  # Start position
        
        # Create ground (not visible, just for collision)
        ground_y = MATRIX_HEIGHT - GROUND_HEIGHT
        
        # Create some platforms
        self.static_sprites.append(Platform(8, ground_y - 3, 4))
        self.static_sprites.append(Platform(15, ground_y - 6, 3))
        self.static_sprites.append(Platform(25, ground_y - 4, 5))
        
        # Create some bricks
        self.static_sprites.append(Brick(12, ground_y - 3))
        self.static_sprites.append(Brick(13, ground_y - 3))
        self.static_sprites.append(Brick(20, ground_y - 3))
        self.static_sprites.append(Brick(21, ground_y - 3))
        self.static_sprites.append(Brick(22, ground_y - 3))
        
        # Create coins
        self.dynamic_sprites.append(Coin(10, ground_y - 5))
        self.dynamic_sprites.append(Coin(16, ground_y - 8))
        self.dynamic_sprites.append(Coin(27, ground_y - 6))
        
        # Create enemies
        self.dynamic_sprites.append(Enemy(18, ground_y - 2))
        self.dynamic_sprites.append(Enemy(30, ground_y - 2))
    
    def update(self, dt: float) -> None:
        """Update all game objects"""
        if self.game_over or not self.mario or not self.mario.active:
            return
        
        # Update Mario
        self.mario.update(dt)
        
        # Update dynamic sprites
        for sprite in self.dynamic_sprites[:]:  # Copy list to avoid modification issues
            if sprite.active:
                sprite.update(dt)
            else:
                self.dynamic_sprites.remove(sprite)
        
        # Check collisions
        self._check_collisions()
        
        # Update camera to follow Mario
        self._update_camera()
        
        # Check game state
        self._check_game_state()
    
    def _check_collisions(self) -> None:
        """Check all collision detection"""
        if not self.mario or not self.mario.active:
            return
        
        # Mario vs Static Sprites
        for sprite in self.static_sprites:
            if sprite.active and self.mario.is_collision(sprite):
                self._handle_mario_static_collision(sprite)
        
        # Mario vs Dynamic Sprites
        for sprite in self.dynamic_sprites[:]:
            if sprite.active and self.mario.is_collision(sprite):
                self._handle_mario_dynamic_collision(sprite)
    
    def _handle_mario_static_collision(self, sprite: StaticSprite) -> None:
        """Handle collision between Mario and static sprite"""
        if isinstance(sprite, Brick):
            # Mario hits brick from below
            if self.mario.y > sprite.y and self.mario.vy < 0:
                if sprite.hit():
                    self.score += 50
                self.mario.vy = 0
        elif isinstance(sprite, Platform):
            # Platform collision
            if self.mario.y < sprite.y and self.mario.vy > 0:
                # Landing on platform
                self.mario.y = sprite.y - self.mario.height
                self.mario.vy = 0
                self.mario.on_ground = True
    
    def _handle_mario_dynamic_collision(self, sprite: DynamicSprite) -> None:
        """Handle collision between Mario and dynamic sprite"""
        if isinstance(sprite, Coin):
            # Collect coin
            sprite.destroy()
            self.dynamic_sprites.remove(sprite)
            self.mario.add_score(sprite.points)
            self.score += sprite.points
        elif isinstance(sprite, Enemy):
            # Check if Mario is above enemy (stomping)
            if (self.mario.y + self.mario.height <= sprite.y + 2 and 
                self.mario.vy > 0):
                # Stomp enemy
                points = sprite.stomp()
                self.dynamic_sprites.remove(sprite)
                self.mario.add_score(points)
                self.score += points
                self.mario.vy = -3  # Bounce
            else:
                # Mario takes damage
                if self.mario.take_damage():
                    self.game_over = True
    
    def _update_camera(self) -> None:
        """Update camera to follow Mario"""
        if not self.mario:
            return
        
        # Simple camera that follows Mario
        target_x = self.mario.x - MATRIX_WIDTH // 2
        self.camera_x = max(0, target_x)
    
    def _check_game_state(self) -> None:
        """Check for game over or level complete conditions"""
        if not self.mario or not self.mario.active:
            self.game_over = True
            return
        
        # Check for level completion (Mario reaches right edge)
        if self.mario.x >= MATRIX_WIDTH - 3:
            self.level_complete = True
        
        # Check if Mario falls off the world
        if self.mario.y > MATRIX_HEIGHT:
            if self.mario.take_damage():
                self.game_over = True
    
    def handle_input(self, controller) -> None:
        """Handle input from controller"""
        if not self.mario or not self.mario.active:
            return
        
        # Movement
        if controller.is_pressed('left'):
            self.mario.move_left()
        elif controller.is_pressed('right'):
            self.mario.move_right()
        
        # Jumping
        if controller.is_just_pressed('jump'):
            self.mario.jump()
    
    def get_visible_sprites(self) -> List[Sprite]:
        """Get all sprites that should be visible on screen"""
        visible = []
        
        # Add Mario
        if self.mario and self.mario.active:
            visible.append(self.mario)
        
        # Add static sprites in view
        for sprite in self.static_sprites:
            if sprite.active and self._is_sprite_visible(sprite):
                visible.append(sprite)
        
        # Add dynamic sprites in view
        for sprite in self.dynamic_sprites:
            if sprite.active and self._is_sprite_visible(sprite):
                visible.append(sprite)
        
        return visible
    
    def _is_sprite_visible(self, sprite: Sprite) -> bool:
        """Check if sprite is visible in current camera view"""
        return (sprite.x + sprite.width > self.camera_x and 
                sprite.x < self.camera_x + MATRIX_WIDTH)
    
    def reset(self) -> None:
        """Reset the game world"""
        self.static_sprites.clear()
        self.dynamic_sprites.clear()
        self.mario = None
        self.camera_x = 0
        self.level = 1
        self.game_over = False
        self.level_complete = False
        self.score = 0
        self._create_level_1()
    
    def get_status(self) -> dict:
        """Get current game status"""
        return {
            'level': self.level,
            'score': self.score,
            'game_over': self.game_over,
            'level_complete': self.level_complete,
            'mario_status': self.mario.get_status() if self.mario else None,
            'camera_x': self.camera_x,
            'sprites_count': {
                'static': len(self.static_sprites),
                'dynamic': len(self.dynamic_sprites)
            }
        }