#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/unistd.h>
#include <sys/stat.h>
#include <assert.h>

#include "esp_err.h"
#include "esp_log.h"
#include "esp_spiffs.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"

#include "esp_vfs_fat.h"
#include "GDEP133C02.h"
#include "comm.h"
#include "pindefine.h"
#include "status.h"
#include "networking.h"
#include "touchscreen.h"
#include "image_buffer.h"

volatile bool touch_detected = false;

void touch_callback(uint16_t x, uint16_t y) {
    ESP_LOGI("MAIN", "Touch detected at x=%d, y=%d", x, y);
    touch_detected = true;
    // initEPD();
    // epdDisplayColor(BLACK);
    // delayms(1000);
}

void app_main(void) {
    // =================== E-Ink Display Setup ====================
    initialGpio();
    initialSpi();
    setGpioLevel(LOAD_SW, GPIO_HIGH);
    epdHardwareReset();
    setPinCsAll(GPIO_HIGH);

    // initEPD();
    // epdDisplayColor(WHITE);
    // delayms(1000);

    init_image_partition_with_network_error_image();

    // ======================== Wifi Setup ========================
    initialize_networking();

    bool connected = connect_to_network();
    if (!connected) {
        initEPD();
        epdDisplayImage();
        delayms(1000);
    }
    while (!connected) {
        connected = connect_to_network();
        delayms(10000);
    }

    // ===================== Wifi Server Setup ====================
    bool server_started = start_image_server();
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
        if (get_volatile_image_updated()) {
            ESP_LOGI("MAIN", "Updating the image using the image_data partition");
            set_volatile_image_updated(false);

            initEPD();
            epdDisplayImage();
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
