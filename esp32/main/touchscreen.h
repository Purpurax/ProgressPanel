#ifndef __TOUCHSCREEN_H__
#define __TOUCHSCREEN_H__

#include "tusb_descriptors.h"

#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "tinyusb.h"
#include "class/hid/hid.h"
#include <stdint.h>

typedef void (*touch_callback_t)(uint16_t x, uint16_t y);
typedef struct {
    uint8_t report_id;
    uint8_t contact_count;
    struct {
        uint8_t contact_id;
        uint8_t tip_switch;
        uint16_t x;
        uint16_t y;
    } contacts[10];
} __attribute__((packed)) multitouch_report_t;


void initialize_touchscreen(touch_callback_t callback);

#endif // __TOUCHSCREEN_H__
