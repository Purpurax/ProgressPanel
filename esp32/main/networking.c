#include "networking.h"

static const char *TAG = "HTTP_SERVER";

bool get_volatile_image_updated(void) {
    bool value = image_updated;
    return value;
}

void set_volatile_image_updated(bool value) {
    image_updated = value;
}

int get_volatile_image_id(void) {
    int value = image_id;
    return value;
}

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
            .password = CONFIG_WIFI_PASSWORD
        },
    };

    esp_netif_t *netif = esp_netif_get_handle_from_ifkey("WIFI_STA_DEF");
    esp_netif_ip_info_t ip_info;

    IP4_ADDR(&ip_info.ip, 192, 168, 0, 206);      // 192.168.0.160
    IP4_ADDR(&ip_info.gw, 192, 168, 0, 1);        // 192.168.0.1
    IP4_ADDR(&ip_info.netmask, 255, 255, 255, 0); // 255.255.255.0

    ESP_ERROR_CHECK(esp_netif_dhcpc_stop(netif));
    ESP_ERROR_CHECK(esp_netif_set_ip_info(netif, &ip_info));
    
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
    ESP_LOGI(TAG, "=== Upload Handler Called ===");
    
    if (req->content_len != 960000) {
        ESP_LOGE(TAG, "Invalid image size: %d, expected 960000", req->content_len);
        httpd_resp_set_status(req, "400 Bad Request");
        httpd_resp_send(req, "Invalid image size", HTTPD_RESP_USE_STRLEN);
        return ESP_FAIL;
    }
    
    ESP_LOGI(TAG, "Starting to receive data...");
    unsigned char* chunk_buffer = (unsigned char*)malloc(4096);
    size_t received = 0;
    
    // First, erase the entire partition
    const esp_partition_t* image_partition = get_image_partition();
    ESP_LOGI(TAG, "Erasing flash partition...");
    esp_err_t erase_ret = esp_partition_erase_range(image_partition, 0, image_partition->size);
    if (erase_ret != ESP_OK) {
        ESP_LOGE(TAG, "Flash erase failed: %s", esp_err_to_name(erase_ret));
        httpd_resp_set_status(req, "500 Internal Server Error");
        httpd_resp_send(req, "Flash erase failed", HTTPD_RESP_USE_STRLEN);
        return ESP_FAIL;
    }
    ESP_LOGI(TAG, "Erased partition successfully");

    while (received < 960000) {
        int chunk_size = (960000 - received > 4096) ? 4096 : (960000 - received);
        int ret = httpd_req_recv(req, (char*)chunk_buffer, chunk_size);
        
        if (ret <= 0) {
            if (ret == HTTPD_SOCK_ERR_TIMEOUT) {
                continue;
            }
            ESP_LOGE(TAG, "Receive failed: %d", ret);
            httpd_resp_set_status(req, "400 Bad Request");
            httpd_resp_send(req, "Upload failed", HTTPD_RESP_USE_STRLEN);
            return ESP_FAIL;
        }
        
        // Write chunk directly to flash
        if (esp_partition_write(image_partition, received, chunk_buffer, ret) != ESP_OK) {
            ESP_LOGE(TAG, "Flash write failed at offset %d", received);
            httpd_resp_set_status(req, "500 Internal Server Error");
            httpd_resp_send(req, "Flash write failed", HTTPD_RESP_USE_STRLEN);
            return ESP_FAIL;
        }
        
        received += ret;
    }

    ESP_LOGI(TAG, "Upload completed successfully: %d bytes", received);
    image_updated = true;
    image_id += 1;
    
    char resp[32];
    snprintf(resp, sizeof(resp), "OK:%d", image_id);
    httpd_resp_set_status(req, "200 OK");
    httpd_resp_send(req, resp, HTTPD_RESP_USE_STRLEN);
    return ESP_OK;
}

esp_err_t test_handler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Test Http request answered with an OK");
    httpd_resp_send(req, "OK", HTTPD_RESP_USE_STRLEN);
    return ESP_OK;
}

bool start_image_server() {
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 5000;
    config.lru_purge_enable = true;
    if (httpd_start(&server, &config) != ESP_OK) {
        ESP_LOGI(TAG, "Server failed to start");
        return false;
    }
    
    httpd_uri_t upload_uri = {
        .uri = "/upload_image",
        .method = HTTP_POST,
        .handler = image_upload_handler,
        .user_ctx = NULL
    };
    
    httpd_uri_t test_uri = {
        .uri = "/test",
        .method = HTTP_GET,
        .handler = test_handler,
        .user_ctx = NULL
    };
    
    httpd_register_uri_handler(server, &upload_uri);
    httpd_register_uri_handler(server, &test_uri);

    ESP_LOGI(TAG, "Server started at port %d", config.server_port);
    return true;
}

void stop_image_server(void) {
    if (server) {
        httpd_stop(server);
        server = NULL;
    }
}
