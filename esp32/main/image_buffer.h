#ifndef __IMAGE_BUFFER_H__
#define __IMAGE_BUFFER_H__

#include "esp_partition.h"
#include "esp_log.h"
#include <string.h>

#include "image_network_error.h"

unsigned char* load_image_from_partition();
const esp_partition_t* get_image_partition(void);
void init_image_partition_with_network_error_image(void);

#endif // __IMAGE_BUFFER_H__
