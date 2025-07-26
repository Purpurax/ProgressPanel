from playwright.sync_api import sync_playwright
import http.server
import socketserver
import threading
import sys
import os
import time
import json
import yaml

CONFIG_PATH = "data/config.yaml"

config = None
with open(CONFIG_PATH, "r") as file:
    config = yaml.safe_load(file)

if config is None:
    print("The config path does not lead to any config.yaml file")


def start_server(port):
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    return httpd, thread

def login_and_save_state(web_state_path):
    browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://accounts.google.com/signin")
    input("Log in to Google in the opened browser, then press Enter here...")
    context.storage_state(path=web_state_path)
    browser.close()

def load_page_headless(p, port, viewport, web_state_path):
    browser = p.chromium.launch()
    context = browser.new_context(storage_state=web_state_path)

    page = context.new_page()
    page.set_viewport_size(viewport)
    page.goto("http://localhost:" + str(port))

    return browser, page

def capture_screenshot(page, output_path):
    time.sleep(5)
    page.screenshot(path=output_path, full_page=True)
    
def capture_button_mapping(page, touch_map_path):
    button_data = page.evaluate("""
        () => {
            const results = [];
            const buttons = Array.from(document.querySelectorAll('button'));
            for (const btn of buttons) {
                const rect = btn.getBoundingClientRect();
                // Find child divs with tag "function"
                const functionDivs = Array.from(btn.querySelectorAll('div[tag="function"]'));
                if (functionDivs.length == 1) {
                    for (const div of functionDivs) {
                        results.push({
                            text: div.innerText,
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height
                        });
                    }
                }
            }
            return results;
        }
    """)
    with open(touch_map_path, "w", encoding="utf-8") as f:
        json.dump(button_data, f, ensure_ascii=False, indent=2)

def stop_server(httpd):
    httpd.shutdown()
    httpd.server_close()


port = config["port"]
image_output_path = config["image_output_path"]
web_state_path = config["web_state_path"]
touch_map_path = config["touch_map_path"]
viewport = {"width": config["viewport_width"], "height": config["viewport_height"]}


httpd, _thread = start_server(port)

with sync_playwright() as p:
    if "--sign-in" in sys.argv or not os.path.exists(web_state_path):
        login_and_save_state(web_state_path)
    
    browser, page = load_page_headless(p, port, viewport, web_state_path)
    capture_button_mapping(page, touch_map_path)
    capture_screenshot(page, image_output_path)
    browser.close()

stop_server(httpd)


