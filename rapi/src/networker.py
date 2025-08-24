

def send_to_esp32(config: dict, payload: bytes):
    ip = config["esp32_ip"]
    port = config["esp32_port"]
