from src.data_scraper import scrap_data
from src.image_render import render_web_page
from src.image_processor import dither_image
from src.networker import send_to_esp32
import yaml, time, os, datetime

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

def scrap():
    # print(f"--- Scraping data --- {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    scrap_data(config)

def update_image_on_esp():
    print("=== UPDATING IMAGE ===")
    with open(os.path.expanduser(config["todo_data_path"]), "rb") as src, \
         open(os.path.expanduser(config["todo_data_path_uploaded"]), "wb") as dst:
        dst.write(src.read())

    print("--- Rendering Webpage ---")
    image_path, button_map = render_web_page(config)
    # image_path = config["image_output_path"]

    print("--- Dithering Image ---")
    payload = dither_image(config, image_path)

    print("--- Sending to ESP32 ---")
    send_to_esp32(config, payload)

def should_run_now(last_run_hour):
    now = datetime.datetime.now()
    if last_run_hour != now.hour and now.hour in [3, 13, 20]:
        return True
    
    with open(os.path.expanduser(config["todo_data_path"]), "rb") as f1, \
         open(os.path.expanduser(config["todo_data_path_uploaded"]), "rb") as f2:
        if f1.read() != f2.read():
            return True

    return False

last_run_hour = -1

print("Starting Script, please make sure the first upload is successful")
scrap()
update_image_on_esp()
while True:
    try:
        scrap()
        if should_run_now(last_run_hour):
            update_image_on_esp()
            now = datetime.datetime.now()
            last_run_hour = now.hour
    except Exception as e:
        print("Error in main loop: " + str(e))
    time.sleep(60)
