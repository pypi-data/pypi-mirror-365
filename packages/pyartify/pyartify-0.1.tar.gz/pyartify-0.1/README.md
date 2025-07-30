
# Pixelify

🎨 Convert images into retro-style pixel art using palettes like NES, GameBoy, Minecraft, and PICO-8. Also supports dithering and transparent backgrounds.

## Installation

```bash
pip install pixelify
```

## Usage (Python)

```python
from pixelify import pixelify_to_nes
img = pixelify_to_nes("image.jpg", pixel_size=8)
img.save("output.png")
```

## Features

- NES, GameBoy, Minecraft, PICO-8 palettes
- Transparent PNG output
- Dithering (Floyd–Steinberg, Ordered, Jarvis–Judice–Ninke)

## License

MIT
