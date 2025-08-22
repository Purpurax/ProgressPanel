# ProgressPanel
## Description
The Project requires will run on a raspberry pi and will display a control panel with which the user can interact. It allows for IoT device control, project progress display, and lastly has a calendar view. The displayed images will update every night at 3 am and sometimes during the day after significant changes appear - therefore it is made for energy efficient but slowly refreshing e ink displays (that also have colors).

## Requirements
Hardware:
- Raspberry Pi or any other computer
- E Ink with colors and a resolution of 1600x1200 with controlling unit (ESP32s3)
- Touch panel with a controlling unit

Software:
- [Todo](https://github.com/Purpurax/Todo)
- Homeassistant on docker
- Calendar iframe link from google

ch340 drivers (Might be preinstalled)

## System explained
The esp32 from the e ink panel will only listen for an update request and make the image update while recieving the full image over network.

## Installation
For the esp32-burning (make sure the submodules are initialized and python is installed):
```
sudo apt-get install git wget flex bison gperf python3 python3-pip python3-venv cmake ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0
cd esp-idf
./install.sh esp32s3
. ./export.sh # Loads in the environment variables
cd ../
cd esp32
idf.py build
idf.py menuconfig # Go to Component config -> TinyUSB stack -> CDC -> enable this feature
idf.py menuconfig # Go to App Configuration and set SSID and Password
idf.py build
```

The rapi requires:
```
sudo apt-get install -y libicu66 libwebp6 libffi7
python -m venv .env
source .env/bin/activate
pip install playwright
python -m playwright install
```
Go through the config.yaml in the data folder and make sure the token works for the homeassistant api

## Execution
When the google calendar requires a new sign in, please use: \
`python image_render.py --sign-in`

```
source .env/bin/activate
python data_scraper.py
python image_render.py
```

## Next Features (developer only)
