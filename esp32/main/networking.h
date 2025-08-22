#ifndef __NETWORKING_H__
#define __NETWORKING_H__

#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_netif.h"
#include "esp_event.h"
#include "esp_wifi.h"
#include "sdkconfig.h"
#include <stdbool.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static bool wifi_connected = false;

void initialize_networking(void);
bool connect_to_network(void);

#endif // __NETWORKING_VARS_H__
