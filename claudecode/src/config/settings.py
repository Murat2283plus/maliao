"""
Configuration settings for Matrix Mario Game
"""

# Display settings
MATRIX_WIDTH = 36
MATRIX_HEIGHT = 28
TOTAL_PIXELS = MATRIX_WIDTH * MATRIX_HEIGHT

# Game settings
GAME_FPS = 30
MARIO_SPEED = 2
JUMP_POWER = 6
GRAVITY = 0.3

# Serial settings
SERIAL_PORT = "COM3"  # Default, can be changed via config
BAUD_RATE = 115200
TIMEOUT = 1

# Controller settings
CONTROLLER_DEADZONE = 0.3

# Color definitions (RGB values 0-255)
COLORS = {
    'BLACK': [0, 0, 0],
    'WHITE': [255, 255, 255],
    'RED': [255, 0, 0],
    'GREEN': [0, 255, 0],
    'BLUE': [0, 0, 255],
    'YELLOW': [255, 255, 0],
    'PURPLE': [255, 0, 255],
    'CYAN': [0, 255, 255],
    'ORANGE': [255, 165, 0],
    'BROWN': [139, 69, 19],
    'MARIO_SKIN': [255, 220, 177],
    'MARIO_HAT': [255, 0, 0],
    'MARIO_SHIRT': [0, 0, 255],
    'BRICK': [205, 133, 63],
    'COIN': [255, 215, 0],
}

# Game elements size (in pixels)
MARIO_WIDTH = 2
MARIO_HEIGHT = 3
BRICK_SIZE = 2
COIN_SIZE = 1

# Level design
GROUND_HEIGHT = 5  # pixels from bottom