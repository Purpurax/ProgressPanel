import yaml
import json

CONFIG_PATH = "config.yaml"

config = None
with open(CONFIG_PATH, "r") as file:
    config = yaml.safe_load(file)

data = {}

# IoT devices
state_top_lamp = "unavailable"
state_night_light = "unavailable"
state_ai = "unavailable"
state_computer = "unavailable"

try:
    from homeassistant_api import Client

    client = Client(config["homeassistant"]["url"], config["homeassistant"]["token"])

    night_light = client.get_entity(entity_id="light.light_night")
    state_night_light = night_light.get_state().state

    computer = client.get_entity(entity_id="light.computer")
    state_computer = computer.get_state().state

    main_light = client.get_entity(entity_id="input_boolean.main_light")
    state_top_lamp = main_light.get_state().state
except Exception as e:
    print(f"Couldn't set up the IoT devices because {e}")

data["iot_devices"] = [
    {"name": "Top Lamp", "state": state_top_lamp, "icon": "images/top_lamp.png", "color_index": 12},
    {"name": "Night Light", "state": state_night_light, "icon": "images/night_light.png", "color_index": 12},
    {"name": "AI", "state": state_ai, "icon": "images/voice_assistant.png", "color_index": 12},
    {"name": "Computer", "state": state_computer, "icon": "images/computer.png", "color_index": 12}
]

# Internal state (resetting at 3am)
data["showing_project"] = 0

# Projects
data["projects"] = [
    {
        "full_name": "University",
        "short_name": "Uni",
        "icon_image": "images/university.png",
        "total_progress": 0.2,
        "general_color_index": 17,
        "categories": [
            {
                "name": "ESE",
                "color_index": 13,
                "todos": [
                    { "text": "Finish ESE", "category": 0, "deadline": 0, "done": True }
                ]
            },
            {
                "name": "MCI",
                "color_index": 16,
                "todos": [
                    { "text": "Finish MCI", "category": 1, "deadline": 0, "done": True }
                ]
            }
        ]
    },
    {
        "full_name": "Chess AI",
        "short_name": "Chess",
        "total_progress": 0.5,
        "icon_image": "images/chess_ai.png",
        "general_color_index": 0,
        "categories": [
            {
                "name": "UI",
                "color_index": 2,
                "todos": [
                    { "text": "Finish UI", "category": 0, "deadline": 0, "done": True }
                ]
            },
            {
                "name": "Code",
                "color_index": 3,
                "todos": [
                    { "text": "Finish Code", "category": 1, "deadline": 0, "done": False }
                ]
            }
        ]
    }
]

# todo_list_file_location = "/home/master/.local/share/todo/data.json"

# todo_list_content = []
# try:
#     with open(todo_list_file_location, "r", encoding="utf-8") as f:
#         todo_list_content = f.read().split('\n')
# except Exception as e:
#     print(f"Couldn't read todo list file: {e}")

# print(todo_list_content)
# Is still missing the entries

# Uni

# Other

with open("data/data.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=4)
