from typing import Dict

# UnityのOrthographic前提
DEFAULT_CAMERA_SIZE = 15
SCREEN_W = 2560
SCREEN_H = 1440

def calc_ppu(camera_size = DEFAULT_CAMERA_SIZE, screen_h = SCREEN_H) -> float:
    """Calculate Pixel Per Unit (PPU)"""
    return screen_h / (camera_size * 2)

def to_pixel(pos_x, pos_y, camera_size = DEFAULT_CAMERA_SIZE, screen_w = SCREEN_W, screen_h = SCREEN_H):    
    # calc world size
    camera_h = camera_size * 2
    camera_w = camera_h * (screen_w / screen_h)

    # convertion
    x_norm = (pos_x + (camera_w / 2)) / camera_w
    pixel_x = int(screen_w * x_norm)
    
    y_norm = (pos_y + (camera_h / 2)) / camera_h
    pixel_y = int(screen_h * (1 - y_norm))  # 左上原点
    
    return {"x": pixel_x, "y": pixel_y}