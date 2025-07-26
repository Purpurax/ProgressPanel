import json, yaml


class TouchInteract:
    def __init__(self):
        CONFIG_PATH = "data/config.yaml"

        self.load_config(CONFIG_PATH)
        self.load_touch_map()

    def load_config(self, config_path):
        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)

        if self.config is None:
            print("The config path does not lead to any config.yaml file")

    def load_touch_map(self):
        with open(self.config["touch_map_path"], "r") as json_file:
            self.touch_map = json.load(json_file)
        
        if self.touch_map is None:
            print("Failed to load in the touch map as it doesnt exist or is not a json")

    def get_touched_button(self, x, y):
        for entry in self.touch_map:
            if x >= entry["x"] and x <= entry["x"] + entry["width"] and \
            y >= entry["y"] and y <= entry["y"] + entry["height"]:
                return entry["text"]
        return None

    def mark_todo(self, location):
        print("todo instruction")

    def toggle_iot_device(self, entity_id):
        try:
            from homeassistant_api import Client

            client = Client(self.config["homeassistant_url"], self.config["homeassistant_token"])

            entity = client.get_domain(entity_id.split(".")[0])
            entity.toggle(entity_id=entity_id)
        except Exception as e:
            print(f"Couldn't toggle IoT device because {e}")

    def change_data_json_state(self, new_index_str):
        try:
            new_index = int(new_index_str)

            json_data = None
            with open(self.config["data_path"], "r") as f:
                json_data = json.load(f)

            if json_data is not None and \
            0 <= new_index < len(json_data.get("projects", [])):
                json_data["showing_project"] = new_index
                with open(self.config["data_path"], "w") as f:
                    json.dump(json_data, f, indent=4)
        except:
            print("Unable to parse to an index to change the data.json state")

    def apply_instruction(self, instruction):
        instruction_type, location = instruction.split("=", 1)
        if instruction_type == "TODO_CLICK":
            self.mark_todo(location)
        elif instruction_type == "IOT_CLICK":
            self.toggle_iot_device(location)
        elif instruction_type == "MIDDLE_PANEL":
            self.change_data_json_state(int(location))
        else:
            print("Unclear Instruction: " + str(instruction_type))

    def apply_touch(self, x, y):
        clicked_instruction = self.get_touched_button(x, y)
        if clicked_instruction is not None:
            self.apply_instruction(clicked_instruction)

if __name__ == "__main__":
    touch_interact = TouchInteract()
    touch_interact.apply_touch(420.0, 130.0)