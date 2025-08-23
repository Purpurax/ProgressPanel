#include "touchscreen.h"

static const char *TAG = "TOUCHSCREEN";
static touch_callback_t touch_callback = NULL;

uint8_t const* tud_hid_descriptor_report_cb(uint8_t instance) {
    ESP_LOGI(TAG, "Host is requesting HID Report Descriptor for instance %d", instance);
    if (instance == ITF_NUM_HID_TOUCH) {
        return touch_report_desc;
    } else if (instance == ITF_NUM_HID_OTHER) {
        return other_hid_report_desc;
    }
    
    return NULL;
}

uint16_t tud_hid_get_report_cb(uint8_t instance, uint8_t report_id, hid_report_type_t report_type, uint8_t* buffer, uint16_t reqlen) {
    return 0;
}

void tud_hid_set_report_cb(uint8_t instance, uint8_t report_id, hid_report_type_t report_type, uint8_t const* buffer, uint16_t bufsize) {
    ESP_LOGI(TAG, "HID report received: instance=%d, report_id=%d, bufsize=%d", instance, report_id, bufsize);
    for (int i = 0; i < bufsize; i++) {
        ESP_LOGI(TAG, "buffer[%d]=0x%02X", i, buffer[i]);
    }
    if (bufsize >= sizeof(multitouch_report_t) && touch_callback) {
        multitouch_report_t* report = (multitouch_report_t*)buffer;
        ESP_LOGI(TAG, "contact_count=%d", report->contact_count);
        for (int i = 0; i < report->contact_count && i < 10; i++) {
            ESP_LOGI(TAG, "Contact %d: tip_switch=%d, x=%d, y=%d", i, report->contacts[i].tip_switch, report->contacts[i].x, report->contacts[i].y);
            if (report->contacts[i].tip_switch) {
                touch_callback(report->contacts[i].x, report->contacts[i].y);
            }
        }
    }
}

static void usb_task(void* param) {
    ESP_LOGI(TAG, "usb_task started");
    while (1) {
        ESP_LOGI(TAG, "Before tud_task()");
        tud_task();
        if (tud_mounted()) {
            ESP_LOGI(TAG, "USB device mounted");
        } else {
            ESP_LOGW(TAG, "USB device NOT mounted");
        }
        vTaskDelay(1);
    }
}

void initialize_touchscreen(touch_callback_t callback) {
    touch_callback = callback;
    
    tinyusb_config_t config = {
        .device_descriptor = &desc_device,
        .string_descriptor = desc_string,
        .configuration_descriptor = desc_configuration,
    };
    tinyusb_driver_install(&config);
    
    xTaskCreate(usb_task, "usb", 2048, NULL, 5, NULL);
}