#include "networking.h"

static void wifi_event_handler(
    void* arg,
    esp_event_base_t event_base,
    int32_t event_id,
    void* event_data
) {
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        wifi_connected = false;
        esp_wifi_connect();
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t* event = (ip_event_got_ip_t*) event_data;
        wifi_connected = true;
    }
}

void initialize_networking(void) {
    // Initialize NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ESP_ERROR_CHECK(nvs_flash_init());
    }
    
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    
    // Create default Wi-Fi station interface
    esp_netif_create_default_wifi_sta();
    
    // Initialize Wi-Fi
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    
    // Register event handlers
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &wifi_event_handler, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &wifi_event_handler, NULL));
}

bool connect_to_network(void) {
    wifi_config_t wifi_config = {
        .sta = {
            .ssid = CONFIG_WIFI_SSID,
            .password = CONFIG_WIFI_PASSWORD,
        },
    };
    
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(ESP_IF_WIFI_STA, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());
    
    // Wait for connection (simple blocking approach)
    int retry_count = 0;
    const int max_retries = 20; // 10 seconds
    
    while (!wifi_connected && retry_count < max_retries) {
        vTaskDelay(500 / portTICK_PERIOD_MS);
        retry_count++;
    }
    
    if (wifi_connected) {
        return true;
    } else {
        return false;
    }
}

esp_err_t image_upload_handler(httpd_req_t *req) {
    unsigned char* image = (unsigned char*)req->user_ctx;
    
    if (req->content_len != 960000) {
        httpd_resp_set_status(req, "400 Bad Request");
        httpd_resp_send(req, "Invalid image size", HTTPD_RESP_USE_STRLEN);
        return ESP_FAIL;
    }
    
    size_t received = 0;
    while (received < 960000) {
        int ret = httpd_req_recv(req, (char*)(image + received), 960000 - received);
        if (ret <= 0) {
            if (ret == HTTPD_SOCK_ERR_TIMEOUT) {
                continue;
            }
            httpd_resp_set_status(req, "400 Bad Request");
            httpd_resp_send(req, "Upload failed", HTTPD_RESP_USE_STRLEN);
            return ESP_FAIL;
        }
        received += ret;
    }

    image_updated = true;
    image_id += 1;
    
    char resp[32];
    snprintf(resp, sizeof(resp), "OK:%d", image_id);
    httpd_resp_set_status(req, "200 OK");
    httpd_resp_send(req, resp, HTTPD_RESP_USE_STRLEN);
    return ESP_OK;
}

bool start_image_server(unsigned char* image) {
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 5000;
    
    if (httpd_start(&server, &config) != ESP_OK) {
        return false;
    }
    
    httpd_uri_t upload_uri = {
        .uri = "/upload",
        .method = HTTP_POST,
        .handler = image_upload_handler,
        .user_ctx = image
    };
    
    httpd_register_uri_handler(server, &upload_uri);
    return true;
}

void stop_image_server(void) {
    if (server) {
        httpd_stop(server);
        server = NULL;
    }
}
