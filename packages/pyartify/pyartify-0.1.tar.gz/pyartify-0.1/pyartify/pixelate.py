
from PIL import Image
import numpy as np
from .utils import closest_color
from .palettes import *

def _pixelify_with_palette(image_path, palette, pixel_size=10, bg_threshold=250):
    img = Image.open(image_path).convert("RGBA")
    img = img.resize((img.width // pixel_size, img.height // pixel_size), Image.NEAREST)
    pixel_data = np.array(img)

    for y in range(pixel_data.shape[0]):
        for x in range(pixel_data.shape[1]):
            r, g, b, a = pixel_data[y, x]
            if a == 0 or (r > bg_threshold and g > bg_threshold and b > bg_threshold):
                pixel_data[y, x] = [0, 0, 0, 0]
            else:
                nearest = closest_color((r, g, b), palette)
                pixel_data[y, x] = [*nearest, 255]

    result = Image.fromarray(pixel_data, 'RGBA')
    result = result.resize((img.width * pixel_size, img.height * pixel_size), Image.NEAREST)
    return result

def pixelify_to_minecraft(image_path, pixel_size=10, bg_threshold=250):
    return _pixelify_with_palette(image_path, MINECRAFT_PALETTE, pixel_size, bg_threshold)

def pixelify_to_nes(image_path, pixel_size=10, bg_threshold=250):
    return _pixelify_with_palette(image_path, NES_PALETTE, pixel_size, bg_threshold)

def pixelify_to_gameboy(image_path, pixel_size=10, bg_threshold=250):
    return _pixelify_with_palette(image_path, GAMEBOY_PALETTE, pixel_size, bg_threshold)

def pixelify_to_pico8(image_path, pixel_size=10, bg_threshold=250):
    return _pixelify_with_palette(image_path, PICO8_PALETTE, pixel_size, bg_threshold)
