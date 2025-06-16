"""
Utility functions for Matrix Mario Game
"""
import numpy as np
from typing import List, Tuple

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max"""
    return max(min_val, min(value, max_val))

def create_empty_matrix(width: int, height: int) -> List[List[List[int]]]:
    """Create an empty RGB matrix filled with black pixels"""
    return [[[0, 0, 0] for _ in range(width)] for _ in range(height)]

def is_collision(x1: int, y1: int, w1: int, h1: int, 
                x2: int, y2: int, w2: int, h2: int) -> bool:
    """Check if two rectangles collide"""
    return (x1 < x2 + w2 and x1 + w1 > x2 and 
            y1 < y2 + h2 and y1 + h1 > y2)

def draw_pixel(matrix: List[List[List[int]]], x: int, y: int, 
               color: List[int], width: int, height: int) -> None:
    """Draw a single pixel to the matrix if within bounds"""
    if 0 <= x < width and 0 <= y < height:
        matrix[y][x] = color.copy()

def draw_rect(matrix: List[List[List[int]]], x: int, y: int, 
              w: int, h: int, color: List[int], 
              width: int, height: int) -> None:
    """Draw a filled rectangle to the matrix"""
    for dy in range(h):
        for dx in range(w):
            draw_pixel(matrix, x + dx, y + dy, color, width, height)

def matrix_to_serial_data(matrix: List[List[List[int]]]) -> bytes:
    """Convert RGB matrix to serial data format"""
    data = bytearray()
    # Add frame header (optional, depends on hardware protocol)
    data.extend(b'\xFF\xFE')  # Frame start marker
    
    # Flatten matrix to linear RGB data
    for row in matrix:
        for pixel in row:
            data.extend(pixel)  # R, G, B bytes
    
    # Add frame footer (optional)
    data.extend(b'\xFD\xFC')  # Frame end marker
    
    return bytes(data)

def serial_data_to_matrix(data: bytes, width: int, height: int) -> List[List[List[int]]]:
    """Convert serial data back to RGB matrix (for testing)"""
    # Skip header and footer if present
    rgb_data = data[2:-2] if len(data) > 4 else data
    
    matrix = []
    idx = 0
    for y in range(height):
        row = []
        for x in range(width):
            if idx + 2 < len(rgb_data):
                pixel = [rgb_data[idx], rgb_data[idx+1], rgb_data[idx+2]]
                row.append(pixel)
                idx += 3
            else:
                row.append([0, 0, 0])
        matrix.append(row)
    
    return matrix