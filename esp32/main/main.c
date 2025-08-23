#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/unistd.h>
#include <sys/stat.h>
#include <assert.h>

#include "esp_partition.h"
#include "esp_err.h"
#include "esp_log.h"
#include "esp_spiffs.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"

// #include "usbcdc.h"
#include "esp_vfs_fat.h"
#include "GDEP133C02.h"
#include "comm.h"
#include "pindefine.h"
#include "status.h"
#include "image_network_error.h"
#include "networking.h"
#include "touchscreen.h"

volatile bool touch_detected = false;
const esp_partition_t* image_partition;
unsigned char* image_buffer;

void touch_callback(uint16_t x, uint16_t y) {
    ESP_LOGI("TOUCH", "Touch detected at x=%d, y=%d", x, y);
    touch_detected = true;
    // initEPD();
    // epdDisplayColor(BLACK);
    // delayms(1000);
}

static void load_image_from_flash(void) {
    if (image_partition && image_buffer) {
        esp_partition_read(image_partition, 0, image_buffer, 960000);
    }
}

static void save_image_to_flash(void) {
    if (image_partition && image_buffer) {
        esp_partition_erase_range(image_partition, 0, 960000);
        esp_partition_write(image_partition, 0, image_buffer, 960000);
    }
}

static void init_image_partition(void) {
    image_partition = esp_partition_find_first(ESP_PARTITION_TYPE_DATA, ESP_PARTITION_SUBTYPE_ANY, "image_data");
    image_buffer = (unsigned char*)malloc(960000);
    if (image_buffer) {
        memset(image_buffer, 0x11, 960000);
    }
}

void app_main(void) {
    // =================== E-Ink Display Setup ====================
    initialGpio();
    initialSpi();
    setGpioLevel(LOAD_SW, GPIO_HIGH);
    epdHardwareReset();
    setPinCsAll(GPIO_HIGH);

    initEPD();
    epdDisplayColor(WHITE);
    delayms(1000);

    init_image_partition();

    // ======================== Wifi Setup ========================
    initialize_networking();

    bool connected = connect_to_network();
    if (!connected) {
        initEPD();
        epdDisplayImage(network_error_image);
        delayms(1000);
    }
    while (!connected) {
        connected = connect_to_network();
        delayms(10000);
    }

    // ===================== Wifi Server Setup ====================
    bool server_started = start_image_server(image_buffer);
    if (!server_started) {
        return;
    }

    // ==================== Touch Screen Setup ====================
    initialize_touchscreen(touch_callback);

    initEPD();
    epdDisplayColor(GREEN);
    delayms(1000);

    
    // ================== Change Image on Demand ==================
    bool color_is_black = false;
    while (1) {
        if (image_updated) {
            image_updated = false;

            initEPD();
            epdDisplayImage(image_buffer);
            delayms(1000);
        }

        if (touch_detected) {
            touch_detected = false;

            if (color_is_black) {
                initEPD();
                epdDisplayColor(YELLOW);
                delayms(1000);
            } else {
                initEPD();
                epdDisplayColor(BLACK);
                delayms(1000);
            }
            color_is_black = !color_is_black;
        }
        delayms(100);
    }
}
