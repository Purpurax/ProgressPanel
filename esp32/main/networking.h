#ifndef __NETWORKING_H__
#define __NETWORKING_H__

#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_netif.h"
#include "esp_event.h"
#include "esp_wifi.h"
#include "esp_http_server.h"
#include "lwip/ip4_addr.h"
#include "esp_err.h"
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <stdbool.h>

#include "image_buffer.h"

static bool wifi_connected = false;
static httpd_handle_t server = NULL;

static volatile bool image_updated = false;
static volatile int image_id = 0;

bool get_volatile_image_updated(void);
void set_volatile_image_updated(bool value);
int get_volatile_image_id(void);

void initialize_networking(void);
bool connect_to_network(void);

esp_err_t image_upload_handler(httpd_req_t *req);
bool start_image_server();
void stop_image_server(void);

#endif // __NETWORKING_VARS_H__
