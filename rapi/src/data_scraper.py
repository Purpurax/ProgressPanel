import yaml, json, os

PROJECT_COLOR_INDEX_CYCLE = [2, 3, 4, 5]

def _get_iot_device_data(homeassistant_url: str, homeassistant_token: str) -> dict:
    state_top_lamp = "unavailable"
    state_night_light = "unavailable"
    state_ai = "unavailable"
    state_computer = "unavailable"

    try:
        from homeassistant_api import Client

        client = Client(homeassistant_url, homeassistant_token)

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
        
        print("Successfully found IoT devices")
    except Exception as e:
        print(f"Couldn't set up the IoT devices because {e}")

    return [
        {
            "name": "Top Lamp",
            "state": state_top_lamp,
            "entity_id": "input_boolean.main_light",
            "icon": "images/top_lamp.png",
            "color_index": 2
        },
        {
            "name": "Night Light",
            "state": state_night_light,
            "entity_id": "light.light_night",
            "icon": "images/night_light.png",
            "color_index": 2},
        {
            "name": "AI",
            "state": state_ai,
            "entity_id": "",
            "icon": "images/voice_assistant.png",
            "color_index": 4},
        {
            "name": "Computer",
            "state": state_computer,
            "entity_id": "light.computer",
            "icon": "images/computer.png",
            "color_index": 5}
    ]

def _get_project_data(todo_data_path: str) -> dict:
    def __load_todo_data(path):
        todo_data = None

        with open(os.path.expanduser(path), "r") as file:
            todo_data = json.load(file)

        if todo_data is None:
            print("Cannot load in the todo data")
            exit()
        
        print("Loaded in todo data.json")
        return todo_data

    ## Find progress panel widget
    ## 1. Get the Progress Panel
    ## 2. Go through each entry in that Panel
    ## 3. For each task widget get their columns
    ## 4. Use the columns to add actual entries
    def __get_widget_by_id(data, id):
        for widget in data["widgets"]:
            if widget["id"] == id:
                return widget

    def __get_cell_by_id(data, id):
        for cell in data["cells"]:
            if cell["id"] == id:
                return cell

    todo_data = __load_todo_data(todo_data_path)

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

            tasks_widget_id = __get_cell_by_id(todo_data, cell_ids[0])["cell_type"]["ReferenceWidget"]
            full_name = __get_cell_by_id(todo_data, cell_ids[1])["content"]
            short_name = __get_cell_by_id(todo_data, cell_ids[2])["content"]
            total_progress = float(int(__get_cell_by_id(todo_data, cell_ids[3])["content"])) / 100.0
            color_index = int(__get_cell_by_id(todo_data, cell_ids[4])["content"])
            icon_path = __get_cell_by_id(todo_data, cell_ids[5])["content"]

            if tasks_widget_id is None or not os.path.isfile(icon_path):
                print(str(icon_path) + " is not a valid icon path")
                continue

            projects_tasks.append({
                "full_name": full_name.strip(),
                "short_name": short_name.strip(),
                "icon_image": icon_path.strip(),
                "total_progress": total_progress,
                "general_color_index": color_index,
                "categories": []
            })

            tasks_widget = __get_widget_by_id(todo_data, tasks_widget_id)
            if tasks_widget is None or len(tasks_widget["matrix_cell_ids"]) < 2:
                continue

            #3
            header_ids = tasks_widget["matrix_cell_ids"][1]
            progress_column = None
            task_name_column = None
            category_column = None
            for (i, header_id) in enumerate(header_ids):
                cell = __get_cell_by_id(todo_data, header_id)
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
                progress_cell = __get_cell_by_id(todo_data, task_ids[progress_column])
                task_name_cell = __get_cell_by_id(todo_data, task_ids[task_name_column])
                category_cell = __get_cell_by_id(todo_data, task_ids[category_column])

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
                    color_index = PROJECT_COLOR_INDEX_CYCLE[len(projects_tasks[-1]["categories"]) % len(PROJECT_COLOR_INDEX_CYCLE)]
                    projects_tasks[-1]["categories"].append({
                        "name": category.strip(),
                        "color_index": color_index,
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
    
    return projects_tasks

def scrap_data(config: dict) -> str:
    data = {
        "iot_devices": _get_iot_device_data(config["homeassistant_url"], config["homeassistant_token"]),
        "showing_project": 0, # Internal state (resetting at 3am)
        "projects": _get_project_data(config["todo_data_path"])
    }

    with open(config["data_path"], "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
