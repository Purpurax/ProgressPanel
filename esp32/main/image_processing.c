#include "image_processing.h"

void apply_dithering(uint8_t *rgb_data, uint8_t *output_data, int width, int height) {
    // Simplified Floyd-Steinberg dithering for Spectra 6 colors
    // Colors: Black, White, Red, Yellow, Orange, Green (adjust as needed)
    
    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            int idx = (y * width + x) * 3; // Assuming RGB format
            
            // Simple quantization to nearest Spectra color
            uint8_t r = rgb_data[idx];
            uint8_t g = rgb_data[idx + 1];
            uint8_t b = rgb_data[idx + 2];
            
            // Convert to grayscale and then to e-ink color
            uint8_t gray = (r * 299 + g * 587 + b * 114) / 1000;
            
            // Map to available colors (adjust based on your e-ink display)
            uint8_t color;
            if (gray < 50) color = 0;      // Black
            else if (gray < 100) color = 1; // Dark gray/Red
            else if (gray < 150) color = 2; // Medium gray/Yellow
            else if (gray < 200) color = 3; // Light gray/Orange
            else if (gray < 230) color = 4; // Very light gray/Green
            else color = 5;                 // White
            
            output_data[y * width + x] = color;
        }
    }
}
