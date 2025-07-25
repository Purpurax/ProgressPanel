# ProgressPanel
## Description
The Project requires will run on a raspberry pi and will display a control panel with which the user can interact. It allows for IoT device control, project progress display, and lastly has a calendar view. The displayed images will update every night at 3 am and sometimes during the day after significant changes appear - therefore it is made for energy efficient but slowly refreshing e ink displays (that also have colors).

## Requirements
Hardware:
- Raspberry Pi or any other computer
- E Ink with colors and a resolution of 1600x1200 with controlling unit (possibly an ESP32)
- Touch panel with a controlling unit

Software:
- [Todo](https://github.com/Purpurax/Todo)
- Homeassistant on docker
- Calendar iframe link from google

## Installation


## Execution


## Next Features (developer only)
- Scrape the data from the todo list
    - Sync the todo with each device including the rapi
    - Get IoT device information
- Add the touch_calculator to determine what was clicked
