const fs = require('fs');

let data = {};

// IoT devices
let state_top_lamp = true;
let state_night_light = true;
let state_ai = true;
let state_computer = true;

try {
    // Setup code for IoT devices would go here
} catch (e) {
    console.log("Couldn't set up the IoT devices because " + e);
}

data["iot_devices"] = [
    { name: "Top Lamp", on: state_top_lamp, icon: "images/top_lamp.png", color_index: 9 },
    { name: "Night Light", on: state_night_light, icon: "images/night_light.png", color_index: 10 },
    { name: "AI", on: state_ai, icon: "images/voice_assistant.png", color_index: 11 },
    { name: "Computer", on: state_computer, icon: "images/computer.png", color_index: 12 }
];

// Internal state (resetting at 3am)
data["showing_project"] = 0;

// Projects
const todo_list_file_location = "/home/master/.local/share/todo/data.json";

let todo_list_content = "";
try {
    todo_list_content = fs.readFileSync(todo_list_file_location, "utf-8").split('\n');
} catch (e) {
    console.log("Couldn't read todo list file: " + e);
}

// console.log(todo_list_content);
// Is still missing the entries

// Uni

// Other

