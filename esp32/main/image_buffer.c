#include "image_buffer.h"

unsigned char* load_image_from_partition(void) {
    const esp_partition_t* image_partition = get_image_partition();
    if (!image_partition) {
        ESP_LOGE("IMAGE_BUFFER", "Failed to find the correct image partition");
        return NULL;
    }
    
    unsigned char* image_buffer = (unsigned char*)malloc(960000);
    if (!image_buffer) {
        ESP_LOGE("IMAGE_BUFFER", "Failed to allocate the image buffer");
        return NULL;
    }

    size_t bytes_read = 0;
    esp_err_t ret;

    while (bytes_read < 960000) {
        int chunk_size = (960000 - bytes_read > 4096) ? 4096 : (960000 - bytes_read);

        ESP_LOGI("IMAGE_BUFFER", "Partition name: %s, bytes_read: %d, image_buffer: %p, image_buffer + bytes_read: %p, chunk_size: %d",
                 image_partition->label, bytes_read, (void*)image_buffer, (void*)(image_buffer + bytes_read), chunk_size);

        ret = esp_partition_read(image_partition, bytes_read, image_buffer + bytes_read, chunk_size);
        if (ret != ESP_OK) {
            ESP_LOGE("IMAGE_BUFFER", "Failed to read chunk at offset %d: %s", bytes_read, esp_err_to_name(ret));
            free(image_buffer);
            return NULL;
        }

        bytes_read += chunk_size;
        ESP_LOGE("IMAGE_BUFFER", "Success one");
    }

    return image_buffer;
}

const esp_partition_t* get_image_partition(void) {
    return esp_partition_find_first(ESP_PARTITION_TYPE_DATA, 0x40, "image_data");
}

void init_image_partition_with_network_error_image(void) {
    const esp_partition_t* image_partition = get_image_partition();
    if (!image_partition) {
        ESP_LOGE("IMAGE_BUFFER", "Failed to find the correct image partition");
        return;
    }

    size_t bytes_written = 0;
    esp_err_t ret;

    // Erase the partition before writing
    ret = esp_partition_erase_range(image_partition, 0, image_partition->size);
    if (ret != ESP_OK) {
        ESP_LOGE("IMAGE_BUFFER", "Failed to erase partition: %s", esp_err_to_name(ret));
        return;
    }

    while (bytes_written < 960000) {
        int chunk_size = (960000 - bytes_written > 4096) ? 4096 : (960000 - bytes_written);

        ret = esp_partition_write(image_partition, bytes_written, network_error_image + bytes_written, chunk_size);
        if (ret != ESP_OK) {
            ESP_LOGE("IMAGE_BUFFER", "Failed to write chunk at offset %d: %s", bytes_written, esp_err_to_name(ret));
            return;
        }

        bytes_written += chunk_size;
    }
    ESP_LOGI("IMAGE_BUFFER", "Network error image written to partition successfully");
}
