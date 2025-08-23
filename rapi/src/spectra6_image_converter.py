from PIL import Image
import numpy as np
import sys, os

def atkinson_dither(img_array, palette, error_diffusion=1.0, threshold_factor=1.0):
    """Apply Atkinson dithering to reduce colors to palette
    
    Args:
        img_array: Input image as numpy array
        palette: Color palette dictionary
        error_diffusion: Factor to control error diffusion strength (0.0-1.0)
                        0.0 = no dithering (nearest color), 1.0 = full dithering
        threshold_factor: Factor to control color distance threshold (0.5-2.0)
                         Lower values = more selective color matching
    """
    height, width, channels = img_array.shape
    
    # Create a copy to work with (convert to float for error diffusion)
    dithered = img_array.astype(np.float32)
    result = np.zeros((height, width), dtype=np.uint8)
    
    # Convert palette to numpy array for easier distance calculation
    palette_colors = np.array(list(palette.keys()))
    
    for y in range(height):
        for x in range(width):
            old_pixel = dithered[y, x]
            
            # Find closest color in palette
            distances = np.sum((palette_colors - old_pixel) ** 2, axis=1)
            closest_idx = np.argmin(distances)
            closest_color = palette_colors[closest_idx]
            
            # Apply threshold factor to make color matching more/less selective
            min_distance = distances[closest_idx]
            threshold = min_distance * threshold_factor
            
            # Check if there's a significantly better match
            if threshold_factor < 1.0:
                valid_matches = distances <= threshold
                if np.any(valid_matches):
                    valid_indices = np.where(valid_matches)[0]
                    closest_idx = valid_indices[0]  # Take first valid match
                    closest_color = palette_colors[closest_idx]
            
            color_index = palette[tuple(closest_color)]
            result[y, x] = color_index
            
            # Calculate quantization error
            error = old_pixel - closest_color
            
            # Apply error diffusion factor
            error *= error_diffusion
            
            # Distribute error using Atkinson dithering pattern
            # Atkinson pattern (spreads error to 6 neighbors):
            #     * 1 1
            #   1 1 1
            #     1
            # Each coefficient is 1/8 of the error
            
            if x + 1 < width:
                dithered[y, x + 1] += error * 1/8
            if x + 2 < width:
                dithered[y, x + 2] += error * 1/8
                
            if y + 1 < height:
                if x - 1 >= 0:
                    dithered[y + 1, x - 1] += error * 1/8
                dithered[y + 1, x] += error * 1/8
                if x + 1 < width:
                    dithered[y + 1, x + 1] += error * 1/8
                    
            if y + 2 < height:
                dithered[y + 2, x] += error * 1/8
    
    return result

def floyd_steinberg_dither(img_array, palette, error_diffusion=1.0, threshold_factor=1.0):
    """Apply Floyd-Steinberg dithering to reduce colors to palette
    
    Args:
        img_array: Input image as numpy array
        palette: Color palette dictionary
        error_diffusion: Factor to control error diffusion strength (0.0-1.0)
                        0.0 = no dithering (nearest color), 1.0 = full dithering
        threshold_factor: Factor to control color distance threshold (0.5-2.0)
                         Lower values = more selective color matching
    """
    height, width, channels = img_array.shape
    
    # Create a copy to work with (convert to float for error diffusion)
    dithered = img_array.astype(np.float32)
    result = np.zeros((height, width), dtype=np.uint8)
    
    # Convert palette to numpy array for easier distance calculation
    palette_colors = np.array(list(palette.keys()))
    
    for y in range(height):
        for x in range(width):
            old_pixel = dithered[y, x]
            
            # Find closest color in palette
            distances = np.sum((palette_colors - old_pixel) ** 2, axis=1)
            closest_idx = np.argmin(distances)
            closest_color = palette_colors[closest_idx]
            
            # Apply threshold factor to make color matching more/less selective
            min_distance = distances[closest_idx]
            threshold = min_distance * threshold_factor
            
            # Check if there's a significantly better match
            if threshold_factor < 1.0:
                valid_matches = distances <= threshold
                if np.any(valid_matches):
                    valid_indices = np.where(valid_matches)[0]
                    closest_idx = valid_indices[0]  # Take first valid match
                    closest_color = palette_colors[closest_idx]
            
            color_index = palette[tuple(closest_color)]
            result[y, x] = color_index
            
            # Calculate quantization error
            error = old_pixel - closest_color
            
            # Apply error diffusion factor
            error *= error_diffusion
            
            # Distribute error to neighboring pixels (Floyd-Steinberg)
            if x + 1 < width:
                dithered[y, x + 1] += error * 7/16
            if y + 1 < height:
                if x - 1 >= 0:
                    dithered[y + 1, x - 1] += error * 3/16
                dithered[y + 1, x] += error * 5/16
                if x + 1 < width:
                    dithered[y + 1, x + 1] += error * 1/16
    
    return result

def png_to_spectra6_array(png_path, output_path, error_diffusion=0.8, threshold_factor=1.0):
    """Convert PNG to Spectra 6 format with configurable dithering
    
    Args:
        png_path: Input PNG file path
        output_path: Output header file path
        error_diffusion: Dithering strength (0.0-1.0)
                        0.0 = no dithering, 1.0 = full dithering
        threshold_factor: Color matching threshold (0.5-2.0)
                         Lower = more selective, higher = more permissive
    """
    # Open and convert image to spectra6 6-color display
    img = Image.open(png_path)
    img = img.resize((1200, 1600))
    
    # Convert to RGB if not already
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Get image dimensions
    width, height = img.size
    
    # Convert image to numpy array
    img_array = np.array(img)
    
    # Define Spectra 6 color palette (6 colors, indices 0-5)
    palette = {
        (0, 0, 0): 0,        # Black
        (255, 255, 255): 1,  # White  
        (230, 230, 0): 2,    # Yellow (e6e600)
        (204, 0, 0): 3,      # Red (cc0000)
        (0, 51, 204): 4,     # Blue (0033cc)
        (0, 204, 0): 5       # Green (00cc00)
    }
    
    print(f"Applying Dithering (diffusion={error_diffusion}, threshold={threshold_factor})...")
    # Apply dithering to convert to palette colors
    # color_indices = floyd_steinberg_dither(img_array, palette, error_diffusion, threshold_factor)
    color_indices = atkinson_dither(img_array, palette, error_diffusion, threshold_factor)
    
    # Calculate packed image size (2 pixels per byte, 4 bits each)
    if width % 2 != 0:
        print(f"Warning: Width {width} is not even, padding with one column")
        # Pad width to even number
        padded_indices = np.zeros((height, width + 1), dtype=np.uint8)
        padded_indices[:, :width] = color_indices
        padded_indices[:, width] = 1  # Fill with white
        color_indices = padded_indices
        width += 1
    
    packed_width_bytes = width // 2  # 2 pixels per byte
    packed_size = packed_width_bytes * height
    
    # Create packed image array
    packed_image = np.zeros(packed_size, dtype=np.uint8)
    
    print("Packing pixels (2 pixels per byte)...")
    for y in range(height):
        for x in range(0, width, 2):  # Process 2 pixels at a time
            pixel1_index = color_indices[y, x]      # First pixel (upper 4 bits)
            pixel2_index = color_indices[y, x + 1]  # Second pixel (lower 4 bits)
            
            # Pack two 4-bit values into one byte
            # First pixel in upper 4 bits, second pixel in lower 4 bits
            packed_byte = (pixel1_index << 4) | (pixel2_index & 0x0F)
            
            # Calculate byte position in packed array
            byte_index = y * packed_width_bytes + x // 2
            packed_image[byte_index] = packed_byte
    
    # Generate C header file
    with open(output_path, 'w') as f:
        f.write(f"// Generated with error_diffusion={error_diffusion}, threshold_factor={threshold_factor}\n")
        f.write(f"const unsigned char gImage[{packed_size}] = {{\n")
        for i in range(0, len(packed_image), 16):
            line = "  "
            for j in range(i, min(i + 16, len(packed_image))):
                line += f"0x{packed_image[j]:02x}"
                if j < len(packed_image) - 1:
                    line += ", "
            f.write(line + "\n")
        f.write("};\n\n")
    
    print(f"Converted {png_path} to Spectra 6 packed format")
    print(f"Output written to {output_path}")
    print(f"Image size: {width}x{height}")
    print(f"Packed size: {packed_size} bytes ({packed_size/(1024*1024):.2f} MB)")
    print(f"Compression ratio: {(width*height*3)/packed_size:.1f}:1 vs 24-bit RGB")

if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
    print("Error: Please provide a valid PNG file path as the first argument.")
    print("Usage: python script.py <image.png> [error_diffusion] [threshold_factor]")
    print("  error_diffusion: 0.0-1.0 (default 0.8) - controls dithering strength")
    print("  threshold_factor: 0.5-2.0 (default 1.0) - controls color matching selectivity")
    print("Examples:")
    print("  python script.py image.png          # Default settings")
    print("  python script.py image.png 0.5      # Light dithering")
    print("  python script.py image.png 0.0      # No dithering (nearest color)")
    print("  python script.py image.png 0.8 0.7  # Custom dithering + selective matching")
    sys.exit(1)

# Parse command line arguments
error_diffusion = 0.5  # 0 sharp edges <-> 1 noisy but smoother transitions
threshold_factor = 2.0  # <1 more selective color matching <-> more distant colors for better mixing

if len(sys.argv) >= 3:
    try:
        error_diffusion = float(sys.argv[2])
        error_diffusion = max(0.0, min(1.0, error_diffusion))  # Clamp to valid range
    except ValueError:
        print("Warning: Invalid error_diffusion value, using default 0.8")

if len(sys.argv) >= 4:
    try:
        threshold_factor = float(sys.argv[3])
        threshold_factor = max(0.1, min(3.0, threshold_factor))  # Clamp to valid range
    except ValueError:
        print("Warning: Invalid threshold_factor value, using default 1.0")

png_to_spectra6_array(sys.argv[1], "image.h", error_diffusion, threshold_factor)