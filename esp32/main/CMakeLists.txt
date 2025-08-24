idf_component_register(SRCS
   "GDEP133C02.c"
   "main.c"
   "comm.c"
   "networking.c"
   "touchscreen.c"
   "image_processing.c"
   "image_network_error.c"
   "image_buffer.c"
   REQUIRES nvs_flash
   PRIV_REQUIRES esp_wifi esp_http_server spiffs esp_partition
   INCLUDE_DIRS "."
)
