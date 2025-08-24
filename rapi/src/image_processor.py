from PIL import Image
from PIL import ImageOps
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

def _turn_image_into_pixels(image_path: str) -> np.array:
    img = Image.open(image_path)
    pixels_three_byte = np.asarray(img)

    height, width, _ = pixels_three_byte.shape
    pixels = np.zeros((height, width), dtype=np.uint32)
    for y in range(height):
        for x in range(width):
            red = int(pixels_three_byte[y, x, 0])
            green = int(pixels_three_byte[y, x, 1])
            blue = int(pixels_three_byte[y, x, 2])

            color = 0xFFFFFF
            color = (red << 16) | (green << 8) | blue

            pixels[y, x] = int(color)

    return pixels

def _threshold_dither(pixels: np.array) -> np.array:
    height, width = pixels.shape
    palette_keys = np.array(list(PALETTE.keys()))
    for y in range(height):
        for x in range(width):
            pixel = pixels[y, x]
            distances = np.abs(palette_keys - pixel)
            best_idx = np.argmin(distances)
            pixels[y, x] = PALETTE[palette_keys[best_idx]]
    return pixels

def _turn_pixel_array_to_payload(pixel_ary: np.array) -> bytes:
    payload = pixel_ary.astype(np.uint8).tobytes()

    print("Payload size before compressing: " + str(len(payload)))

    packed_bytes = bytearray()

    for i in range(0, len(payload), 2):
        first = payload[i] & 0x0F
        second = payload[i+1] & 0x0F
        packed_bytes.append((first << 4) | second)

    payload = bytes(packed_bytes)

    print("Payload size after compressing: " + str(len(payload)))

    if len(payload) < 960000:
        print("Pixels are not enough (" + str(len(payload)) + ") and cannot be used as payload")
        exit(0)
    elif len(payload) > 960000:
        print("Pixels are more (" + str(len(payload)) + ") and cannot be used as payload")
        exit(0)

    return payload

def dither_image(config: dict, image_path: str) -> bytes:
    pixel_ary = _turn_image_into_pixels(image_path)
    dithered_pixel_ary = _threshold_dither(pixel_ary)

    res = _turn_pixel_array_to_payload(dithered_pixel_ary)
    
    # print("First 1000 pixels (hex):", [hex(x) for x in dithered_pixel_ary.flatten()[:1000]])
    # print("Last 1000 pixels (hex):", [hex(x) for x in dithered_pixel_ary.flatten()[-1000:]])

    return res
