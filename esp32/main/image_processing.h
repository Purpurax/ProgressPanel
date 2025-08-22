#ifndef __IMAGE_PROCESSING_H__
#define __IMAGE_PROCESSING_H__

#include <stdint.h>

void apply_dithering(
    uint8_t *rgb_data,
    uint8_t *output_data,
    int width,
    int height
);

#endif
