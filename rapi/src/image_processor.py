from PIL import Image
import numpy as np
from io import BytesIO

PALETTE = {
    0x000000: 0, # Black
    0xffffff: 1, # White  
    0xe6e600: 2, # Yellow
    0xcc0000: 3, # Red
    0x0033cc: 4, # Blue
    0x00cc00: 5  # Green
}

def _turn_image_into_pixels(image: bytes) -> np.array:
    img = Image.open(BytesIO(image))
    img = img.resize((1200, 1600))
    img = img.convert('RGB')

    return np.array(img)

def _threshold_dither(pixels: np.array) -> np.array:
    height, width, _ = pixels.shape
    palette_colors = np.array([(k >> 16 & 0xFF, k >> 8 & 0xFF, k & 0xFF) for k in PALETTE.keys()])

    for y in range(height):
        for x in range(width):
            pixel = pixels[y, x]
            
            distances = np.linalg.norm(palette_colors - pixel, axis=1)
            best_idx = np.argmin(distances)
            
            pixels[y, x] = palette_colors[best_idx]

    return pixels

def _turn_pixel_array_to_payload(pixel_ary: np.array) -> bytes:
    payload = pixel_ary.astype(np.uint8).tobytes()

    packed_bytes = bytearray()

    for i in range(0, len(payload), 2):
        first = payload[i] & 0x0F
        second = payload[i+1] & 0x0F
        packed_bytes.append((first << 4) | second)

    payload = bytes(packed_bytes)

    if len(payload) < 960000:
        payload += b'\x00' * (960000 - len(payload))
    elif len(payload) > 960000:
        payload = payload[:960000]

    return payload

def dither_image(config: dict, image: bytes) -> bytes:
    pixel_ary = _turn_image_into_pixels(image)
    dithered_pixel_ary = _threshold_dither(pixel_ary)

    return _turn_pixel_array_to_payload(dithered_pixel_ary)
