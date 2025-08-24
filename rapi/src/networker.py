import requests

def send_to_esp32(config: dict, payload: bytes):
    ip = config["esp32_ip"]
    port = config["esp32_port"]

    url = f"http://{ip}:{port}/upload_image"

    print("Trying to send a payload of size: " + str(len(payload)))
    try:
        response = requests.post(
            url,
            data=payload,
            headers={
                'Content-Type': 'application/octet-stream',
                'Content-Length': str(len(payload))
            },
            timeout=30
        )
        
        response.raise_for_status()
        
        print(f"Response from ESP32: {response.text}")
        print(f"Successfully sent {len(payload)} bytes to ESP32 at {ip}:{port}")
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"Failed to connect to ESP32 at {ip}:{port}")
        return False
    except requests.exceptions.Timeout:
        print(f"Request to ESP32 timed out after 30 seconds")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to ESP32: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
