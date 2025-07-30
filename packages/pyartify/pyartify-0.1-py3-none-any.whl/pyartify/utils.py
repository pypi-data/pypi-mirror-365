
def closest_color(rgb, palette):
    return min(palette, key=lambda c: sum((a - b) ** 2 for a, b in zip(rgb, c)))
