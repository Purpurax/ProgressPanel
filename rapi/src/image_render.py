from playwright.sync_api import sync_playwright
import http.server
import socketserver
import threading
import sys
import os
import time
import json
from io import BytesIO
from PIL import Image

def _start_server(port):
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    return httpd, thread

def _login_and_save_state(p, web_state_path):
    browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://accounts.google.com/signin")
    input("Log in to Google in the opened browser, then press Enter here...")
    context.storage_state(path=web_state_path)
    browser.close()

def _load_page_headless(p, port, viewport, web_state_path):
    browser = p.chromium.launch()
    context = browser.new_context(storage_state=web_state_path)

    page = context.new_page()
    page.set_viewport_size(viewport)
    page.goto("http://localhost:" + str(port))

    return browser, page

def _capture_screenshot(page, output_path: str):
    time.sleep(5)
    page.screenshot(path=output_path, full_page=True)

    img = Image.open(output_path)
    img = img.transpose(Image.TRANSPOSE)
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(output_path, format="PNG")
    
def _capture_button_mapping(page, touch_map_path: str):
    button_map_data = page.evaluate("""
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
        json.dump(button_map_data, f, ensure_ascii=False, indent=2)

def _stop_server(httpd):
    httpd.shutdown()
    httpd.server_close()

def render_web_page(config: dict) -> tuple[bytes, bytes]:
    port = config["port"]
    image_output_path = config["image_output_path"]
    web_state_path = config["web_state_path"]
    touch_map_path = config["touch_map_path"]
    viewport = {"width": config["viewport_width"], "height": config["viewport_height"]}

    server_started = False
    while not server_started:
        try:
            httpd, _thread = _start_server(port)
            server_started = True
        except:
            port += 1

    with sync_playwright() as p:
        if "--sign-in" in sys.argv or not os.path.exists(web_state_path):
            _login_and_save_state(p, web_state_path)
        
        browser, page = _load_page_headless(p, port, viewport, web_state_path)
        _capture_button_mapping(page, touch_map_path)
        _capture_screenshot(page, image_output_path)
        browser.close()

    _stop_server(httpd)

    return (image_output_path, touch_map_path)
