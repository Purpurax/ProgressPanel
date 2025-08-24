from PIL import Image
import numpy as np

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

            color = (red << 16) | (green << 8) | blue

            pixels[y, x] = int(color)

    return pixels

def _add_error_to_pixel(pixel_value, error_r, error_g, error_b, factor):
    """Helper function to add error to a pixel while preventing overflow"""
    pixel = int(pixel_value)
    r = ((pixel >> 16) & 0xFF) + int(error_r * factor)
    g = ((pixel >> 8) & 0xFF) + int(error_g * factor)
    b = (pixel & 0xFF) + int(error_b * factor)
    
    # Clamp values to valid range
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    
    return (r << 16) | (g << 8) | b

def _floyd_steinberg_dither(pixels: np.array) -> np.array:
    height, width = pixels.shape
    pixel_palette_indices = np.zeros((height, width), dtype=np.uint8)
    
    # Convert to float for error calculation
    working_pixels = pixels.astype(np.float64)
    
    # Extract RGB components from palette for better color matching
    palette_rgb = []
    palette_keys = list(PALETTE.keys())
    for color in palette_keys:
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        palette_rgb.append([r, g, b])
    palette_rgb = np.array(palette_rgb)

    for y in range(height):
        for x in range(width):
            old_pixel = int(working_pixels[y, x])
            
            # Extract RGB components
            old_r = (old_pixel >> 16) & 0xFF
            old_g = (old_pixel >> 8) & 0xFF
            old_b = old_pixel & 0xFF
            old_rgb = np.array([old_r, old_g, old_b])
            
            # Find closest palette color using Euclidean distance in RGB space
            distances = np.sqrt(np.sum((palette_rgb - old_rgb) ** 2, axis=1))
            best_idx = np.argmin(distances)
            new_pixel = palette_keys[best_idx]
            
            pixel_palette_indices[y, x] = best_idx
            
            # Calculate error in RGB space
            new_r = (new_pixel >> 16) & 0xFF
            new_g = (new_pixel >> 8) & 0xFF
            new_b = new_pixel & 0xFF
            
            error_r = old_r - new_r
            error_g = old_g - new_g
            error_b = old_b - new_b
            
            # Distribute error to neighboring pixels
            if x + 1 < width:
                working_pixels[y, x + 1] = _add_error_to_pixel(
                    working_pixels[y, x + 1], error_r, error_g, error_b, 7/16
                )
            if y + 1 < height:
                if x - 1 >= 0:
                    working_pixels[y + 1, x - 1] = _add_error_to_pixel(
                        working_pixels[y + 1, x - 1], error_r, error_g, error_b, 3/16
                    )
                working_pixels[y + 1, x] = _add_error_to_pixel(
                    working_pixels[y + 1, x], error_r, error_g, error_b, 5/16
                )
                if x + 1 < width:
                    working_pixels[y + 1, x + 1] = _add_error_to_pixel(
                        working_pixels[y + 1, x + 1], error_r, error_g, error_b, 1/16
                    )
    
    return pixel_palette_indices

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
    payload = pixel_ary.tobytes()

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
    dithered_pixel_ary = _floyd_steinberg_dither(pixel_ary)

    res = _turn_pixel_array_to_payload(dithered_pixel_ary)
    
    # print("First 1000 pixels (hex):", [hex(x) for x in dithered_pixel_ary.flatten()[:1000]])
    # print("Last 1000 pixels (hex):", [hex(x) for x in dithered_pixel_ary.flatten()[-1000:]])

    return res
