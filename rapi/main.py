from src.data_scraper import scrap_data
from src.image_render import render_web_page
from src.image_processor import dither_image
from src.networker import send_to_esp32
import yaml, time
import datetime

CONFIG_PATH = "data/config.yaml"

def load_configs():
    config = None
    with open(CONFIG_PATH, "r") as file:
        config = yaml.safe_load(file)

    if config is None:
        print("The config path does not lead to any config.yaml file")
        exit(0)
    return config

config = load_configs()

def update_image_on_esp():
    print("--- Scraping data ---")
    scrap_data(config)

    print("--- Rendering Webpage ---")
    image_path, button_map = render_web_page(config)
    # image_path = config["image_output_path"]

    print("--- Dithering Image ---")
    payload = dither_image(config, image_path)

    print("--- Sending to ESP32 ---")
    send_to_esp32(config, payload)

def should_run_now():
    now = datetime.datetime.now()
    return now.hour in [3, 13, 20]

last_run_hour = -1

update_image_on_esp()
while True:
    now = datetime.datetime.now()
    if should_run_now() and last_run_hour != now.hour:
        update_image_on_esp()
        last_run_hour = now.hour
    time.sleep(60)
