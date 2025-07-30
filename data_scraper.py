import yaml, json, os

CONFIG_PATH = "data/config.yaml"

config = None
with open(CONFIG_PATH, "r") as file:
    config = yaml.safe_load(file)

if config is None:
    print("The config path does not lead to any config.yaml file")
    exit()

data = {}

# IoT devices
state_top_lamp = "unavailable"
state_night_light = "unavailable"
state_ai = "unavailable"
state_computer = "unavailable"

try:
    from homeassistant_api import Client

    client = Client(config["homeassistant_url"], config["homeassistant_token"])

    night_light = client.get_entity(entity_id="light.light_night")
    state_night_light = night_light.get_state().state

    computer = client.get_entity(entity_id="light.computer")
    state_computer = computer.get_state().state

    main_light = client.get_entity(entity_id="input_boolean.main_light")
    state_top_lamp = main_light.get_state().state

    ai_listener = client.get_entity(entity_id="sensor.ai_listener_status")
    if ai_listener.get_state().state == "unavailable":
        state_ai = "unavailable"
    else:
        ai_listener = client.get_entity(entity_id="switch.ai_listener")
        state_ai = ai_listener.get_state().state
except Exception as e:
    print(f"Couldn't set up the IoT devices because {e}")

data["iot_devices"] = [
    {
        "name": "Top Lamp",
        "state": state_top_lamp,
        "entity_id": "input_boolean.main_light",
        "icon": "images/top_lamp.png",
        "color_index": 12
    },
    {
        "name": "Night Light",
        "state": state_night_light,
        "entity_id": "light.light_night",
        "icon": "images/night_light.png",
        "color_index": 12},
    {
        "name": "AI",
        "state": state_ai,
        "entity_id": "",
        "icon": "images/voice_assistant.png",
        "color_index": 12},
    {
        "name": "Computer",
        "state": state_computer,
        "entity_id": "light.computer",
        "icon": "images/computer.png",
        "color_index": 12}
]

# Internal state (resetting at 3am)
data["showing_project"] = 0

# Projects
todo_data = None

with open(os.path.expanduser(config["todo_data_path"]), "r") as file:
    todo_data = json.load(file)

if todo_data is None:
    print("Cannot load in the todo data")
    exit()

## Find progress panel widget
## 1. Get the Progress Panel
## 2. Go through each entry in that Panel
## 3. For each task widget get their columns
## 4. Use the columns to add actual entries
def get_widget_by_id(data, id):
    for widget in data["widgets"]:
        if widget["id"] == id:
            return widget

def get_cell_by_id(data, id):
    for cell in data["cells"]:
        if cell["id"] == id:
            return cell

projects_tasks = []

#1
progress_panel_widget = None
for widget in todo_data["widgets"]:
    if widget["name"] == "Progress Panel":
        progress_panel_widget = widget

if progress_panel_widget is not None and len(progress_panel_widget["matrix_cell_ids"]) >= 2:
    relevant_matrix_cell_ids = progress_panel_widget["matrix_cell_ids"][2:-1]
    for cell_ids in relevant_matrix_cell_ids: #2
        if len(cell_ids) != 7:
            continue

        tasks_widget_id = get_cell_by_id(todo_data, cell_ids[0])["cell_type"]["ReferenceWidget"]
        full_name = get_cell_by_id(todo_data, cell_ids[1])["content"]
        short_name = get_cell_by_id(todo_data, cell_ids[2])["content"]
        total_progress = float(int(get_cell_by_id(todo_data, cell_ids[3])["content"])) / 100.0
        color_index = int(get_cell_by_id(todo_data, cell_ids[4])["content"])
        icon_path = os.path.expanduser(get_cell_by_id(todo_data, cell_ids[5])["content"])

        if tasks_widget_id is None or not os.path.isfile(icon_path) \
        or not icon_path.startswith("/home/master/Project/Javascript/ProgressPanel/images/"):
            continue

        projects_tasks.append({
            "full_name": full_name.strip(),
            "short_name": short_name.strip(),
            "icon_image": str(icon_path.split("/home/master/Project/Javascript/ProgressPanel/")[1]).strip(),
            "total_progress": total_progress,
            "general_color_index": color_index,
            "categories": []
        })

        tasks_widget = get_widget_by_id(todo_data, tasks_widget_id)
        if tasks_widget is None or len(tasks_widget["matrix_cell_ids"]) < 2:
            continue

        #3
        header_ids = tasks_widget["matrix_cell_ids"][1]
        progress_column = None
        task_name_column = None
        category_column = None
        for (i, header_id) in enumerate(header_ids):
            cell = get_cell_by_id(todo_data, header_id)
            if cell is None:
                continue
            if cell["content"].lower() == "progress":
                progress_column = i
            elif cell["content"].lower() == "task":
                task_name_column = i
            elif cell["content"].lower() == "category" or cell["content"].lower() == "course":
                category_column = i
        if progress_column is None or task_name_column is None or category_column is None:
            print("warning: unable to find all columns for table: " + tasks_widget["name"])
            continue
        
        #4
        for task_ids in tasks_widget["matrix_cell_ids"][2:]:
            progress_cell = get_cell_by_id(todo_data, task_ids[progress_column])
            task_name_cell = get_cell_by_id(todo_data, task_ids[task_name_column])
            category_cell = get_cell_by_id(todo_data, task_ids[category_column])

            if progress_cell["cell_type"] != { "Toggle": True } \
            and progress_cell["cell_type"] != { "Toggle": False }:
                continue
            
            progress = progress_cell["cell_type"]["Toggle"]
            task_name = task_name_cell["content"]
            category = category_cell["content"]

            key_exists_at_index = None
            for (i, category_entry) in enumerate(projects_tasks[-1]["categories"]):
                if category_entry["name"].strip() == category.strip():
                    key_exists_at_index = i
                    break
            
            if key_exists_at_index is None:
                projects_tasks[-1]["categories"].append({
                    "name": category.strip(),
                    "color_index": 13,
                    "todos": [{
                        "text": task_name.strip(),
                        "progress_cell_id": progress_cell["id"],
                        "deadline": 0,
                        "done": progress
                    }]
                })
            else:
                projects_tasks[-1]["categories"][key_exists_at_index]["todos"].append({
                    "text": task_name.strip(),
                    "progress_cell_id": progress_cell["id"],
                    "deadline": 0,
                    "done": progress
                })

data["projects"] = projects_tasks

# data["projects"] = [
#     {
#         "full_name": "University",
#         "short_name": "Uni",
#         "icon_image": "images/university.png",
#         "total_progress": 0.2,
#         "general_color_index": 17,
#         "categories": [
#             {
#                 "name": "ESE",
#                 "color_index": 13,
#                 "todos": [
#                     {
#                         "text": "Finish ESE",
#                         "json_location": "Table,#(#,Uni,#/#,0",
#                         "category": 0,
#                         "deadline": 0,
#                         "done": True
#                     }
#                 ]
#             },
#             {
#                 "name": "MCI",
#                 "color_index": 16,
#                 "todos": [
#                     {
#                         "text": "Finish MCI",
#                         "json_location": "Table,#(#,Uni,#/#,1",
#                         "category": 1,
#                         "deadline": 0,
#                         "done": True
#                     }
#                 ]
#             }
#         ]
#     },
#     {
#         "full_name": "Chess AI",
#         "short_name": "Chess",
#         "total_progress": 0.5,
#         "icon_image": "images/chess_ai.png",
#         "general_color_index": 0,
#         "categories": [
#             {
#                 "name": "UI",
#                 "color_index": 2,
#                 "todos": [
#                     {
#                         "text": "Finish UI",
#                         "json_location": "Table,#(#,Chess,#/#,0",
#                         "category": 0,
#                         "deadline": 0,
#                         "done": True
#                     }
#                 ]
#             },
#             {
#                 "name": "Code",
#                 "color_index": 3,
#                 "todos": [
#                     {
#                         "text": "Finish Code",
#                         "json_location": "Table,#(#,Chess,#/#,1",
#                         "category": 1,
#                         "deadline": 0,
#                         "done": False
#                     }
#                 ]
#             }
#         ]
#     }
# ]

# Save Scraped Data
with open(config["data_path"], "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=4)
