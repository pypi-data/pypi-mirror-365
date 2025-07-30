
from PIL import Image
import numpy as np
from .utils import closest_color

def ordered_dither(image, palette, matrix=np.array([[0, 2], [3, 1]]) / 4.0):
    img = image.convert("RGB")
    pixels = np.array(img)
    h, w = pixels.shape[:2]

    for y in range(h):
        for x in range(w):
            old_color = pixels[y, x]
            threshold = matrix[y % matrix.shape[0], x % matrix.shape[1]] * 255
            avg = sum(old_color) / 3
            if avg > threshold:
                pixels[y, x] = closest_color(old_color, palette)
            else:
                pixels[y, x] = closest_color((0, 0, 0), palette)

    return Image.fromarray(pixels.astype(np.uint8))

def floyd_steinberg_dither(image, palette):
    img = image.convert("RGB")
    pixels = np.array(img, dtype=np.float32)
    h, w = pixels.shape[:2]

    for y in range(h):
        for x in range(w):
            old_pixel = pixels[y, x]
            new_pixel = np.array(closest_color(old_pixel, palette))
            pixels[y, x] = new_pixel
            error = old_pixel - new_pixel

            if x + 1 < w:
                pixels[y, x+1] += error * 7 / 16
            if x > 0 and y + 1 < h:
                pixels[y+1, x-1] += error * 3 / 16
            if y + 1 < h:
                pixels[y+1, x] += error * 5 / 16
            if x + 1 < w and y + 1 < h:
                pixels[y+1, x+1] += error * 1 / 16

    pixels = np.clip(pixels, 0, 255)
    return Image.fromarray(pixels.astype(np.uint8))

def jarvis_judice_ninke_dither(image, palette):
    img = image.convert("RGB")
    pixels = np.array(img, dtype=np.float32)
    h, w = pixels.shape[:2]
    diffusion = [
        (1, 0, 7), (2, 0, 5),
        (-2, 1, 3), (-1, 1, 5), (0, 1, 7), (1, 1, 5), (2, 1, 3),
        (-2, 2, 1), (-1, 2, 3), (0, 2, 5), (1, 2, 3), (2, 2, 1)
    ]

    for y in range(h):
        for x in range(w):
            old_pixel = pixels[y, x]
            new_pixel = np.array(closest_color(old_pixel, palette))
            error = old_pixel - new_pixel
            pixels[y, x] = new_pixel

            for dx, dy, weight in diffusion:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    pixels[ny, nx] += error * weight / 48

    pixels = np.clip(pixels, 0, 255)
    return Image.fromarray(pixels.astype(np.uint8))
