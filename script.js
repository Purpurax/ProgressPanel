const COLOR_PALETTE = [
    '#be4a2f', '#d77643', '#ead4aa', '#e4a672', '#b86f50', '#733e39', '#3e2731', '#a22633',
    '#e43b44', '#f77622', '#feae34', '#fee761', '#63c74d', '#3e8948', '#265c42', '#193c3e',
    '#124e89', '#0099db', '#2ce8f5', '#ffffff', '#c0cbdc', '#8b9bb4', '#5a6988', '#3a4466',
    '#262b44', '#181425', '#ff0044', '#68386c', '#b55088', '#f6757a', '#e8b796', '#c28569'
];

fetch('data/data.json')
    .then(res => res.json())
    .then(data => {
        if (data.showing_project >= data.projects.length) {
            console.error("The showing_project in the json is out of bounds");
            return
        }
        if (data.iot_devices.length != 4) {
            console.error("Exactly 4 IoT devices are allowed, not more, not less");
            return
        }

        configure_active_project(data.projects[data.showing_project]);
        configure_other_projects(data);
        configure_iot_devices(data.iot_devices);
    });

const calendarIframe = document.querySelector("iframe[src*='calendar.google.com']");
if (calendarIframe) {
    calendarIframe.addEventListener("load", function () {
        console.log("CALENDAR_IFRAME_LOADED");
    });
}

function configure_active_project(active_project) {
    // Total progress bar
    const fg = document.querySelector('.foreground');
    const title = document.querySelector('.progress-label');
    fg.style.width = active_project.total_progress * 100 + '%';
    fg.style.backgroundColor = COLOR_PALETTE[active_project.general_color_index];
    title.textContent = active_project.full_name + " Progress";

    // Category progress bars
    const circleList = document.getElementById('circle-progress-list');
    const total_todos = active_project.categories.map(category => category.todos.length).reduce((a, b) => a + b, 0);
    active_project.categories.forEach(category => {
        const color = COLOR_PALETTE[category.color_index];
        const total_todos_of_category = category.todos.length;

        const circular_progress = createProgressLeftPanel(
            total_todos_of_category * 100 / total_todos,
            category.name,
            color
        );
        circleList.appendChild(circular_progress);
    });

    // Full Todo list
    const todoList = document.getElementById('todo-list');
    todoList.innerHTML = '';
    active_project.categories
        .flatMap((category, _) => 
            category.todos.map(todo => ({
                ...todo,
                color_index: category.color_index
            }))
        )
        .sort((a, b) => {
            if (a.done !== b.done) return a.done - b.done;
            return a.deadline - b.deadline;
        })
        .forEach(todo => {
            const wrapper = document.createElement('li');
            if (todo.done) wrapper.classList.add('completed');
            
            const color = COLOR_PALETTE[todo.color_index];
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'todo-checkbox';
            checkbox.checked = todo.done;
            checkbox.style.borderColor = color;
            checkbox.style.background = checkbox.checked ? color : '#ffffff';

            const btn = document.createElement('button');
            btn.className = 'todo-btn';
            btn.style.position = 'absolute';
            btn.style.top = 0;
            btn.style.left = 0;
            btn.style.width = '100%';
            btn.style.height = '100%';
            btn.style.opacity = 0;
            btn.style.cursor = 'pointer';
            btn.style.border = 'none';
            btn.style.background = 'transparent';
            btn.tabIndex = -1;

            wrapper.style.position = 'relative';
            wrapper.appendChild(btn);

            const hiddenDiv = document.createElement('div');
            hiddenDiv.style.display = 'none';
            hiddenDiv.textContent = "TODO_CLICK=" + todo.progress_cell_id;
            hiddenDiv.setAttribute('tag', 'function');
            btn.appendChild(hiddenDiv);

            btn.onclick = () => {
                console.log(hiddenDiv.textContent)
                checkbox.checked = !checkbox.checked;
                wrapper.classList.toggle('completed', checkbox.checked);
                checkbox.style.background = checkbox.checked ? color : '#ffffff';
            };

            const span = document.createElement('span');
            span.className = 'todo-text';
            span.textContent = todo.text;

            wrapper.style.background = '';
            wrapper.style.color = '';
            wrapper.style.opacity = todo.done ? 0.6 : 1;

            wrapper.appendChild(checkbox);
            wrapper.appendChild(span);
            todoList.appendChild(wrapper);
    });
}

function configure_other_projects(data) {
    const not_active_projects = data.projects
        .map((project, idx) => ({ project, idx }))
        .filter(({ idx }) => idx !== data.showing_project);
    const project_progresses = document.getElementById('middle-panel');
    
    not_active_projects.forEach(({ project, idx }) => {
        const color = COLOR_PALETTE[project.general_color_index];
        const total_todos = project.categories.map(category => category.todos.length).reduce((a, b) => a + b, 0);
        const finished_todos = project.categories.map(category => category.todos.filter((todo, _) => todo.done).length).reduce((a, b) => a + b, 0);

        const circular_progress = createProgressMiddlePanel(finished_todos * 100 / total_todos, project.icon_image, project.short_name, color, idx);
        project_progresses.appendChild(circular_progress);
    });
}

function configure_iot_devices(iot_devices) {
    const iotGrid = document.getElementById('iot-grid');
    iotGrid.innerHTML = '';
    iot_devices.forEach(device => {
        const btn = document.createElement('button');
        btn.className = 'iot-btn' + (device.state == 'on' ? ' on' : '');
        btn.innerHTML = `<img src="${device.icon}" width="48" height="48">`;

        const hiddenDiv = document.createElement('div');
        hiddenDiv.style.display = 'none';
        hiddenDiv.textContent = "IOT_CLICK=" + device.entity_id;
        hiddenDiv.setAttribute('tag', 'function');
        btn.appendChild(hiddenDiv);
        
        const onColor = COLOR_PALETTE[device.color_index];
        const unavailableColor = COLOR_PALETTE[6];

        if (device.state == 'on') {
            btn.style.backgroundColor = onColor;
        } else if (device.state == 'off') {
            btn.style.backgroundColor = '';
        } else {
            btn.style.backgroundColor = unavailableColor;
        }

        btn.onclick = () => {
            console.log(hiddenDiv.textContent)
            device.on = !device.on;
            btn.classList.toggle('on', device.on == 'on');
            
            if (device.state == 'on') {
                btn.style.backgroundColor = onColor;
            } else if (device.state == 'off') {
                btn.style.backgroundColor = '';
            } else {
                btn.style.backgroundColor = unavailableColor;
            }
        };
        iotGrid.appendChild(btn);
    });
}



function createProgressLeftPanel(percent, text, color = '#2ecc40') {
    const wrapper = document.createElement('div');
    const size = 65;
    wrapper.style.position = 'relative';
    wrapper.style.width = wrapper.style.height = size + 'px';
    const fontSize = size / 4;
    // Use a span with inline style and set max-width to fit the box, use CSS clamp for font-size
    const circleSvg = `
        <svg width="${size}" height="${size}">
            <circle cx="${size/2}" cy="${size/2}" r="${(size/2)-8}" stroke="#e0e0e0" stroke-width="8" fill="none"/>
            <circle cx="${size/2}" cy="${size/2}" r="${(size/2)-8}" stroke="${color}" stroke-width="8" fill="none"
                stroke-dasharray="${2 * Math.PI * ((size/2)-8)}"
                stroke-dashoffset="${2 * Math.PI * ((size/2)-8) * (1 - percent/100)}"
                style="transition: stroke-dashoffset 0.5s;"/>
        </svg>
        <span style="
            position:absolute;
            top:50%;
            left:50%;
            transform:translate(-50%,-50%);
            font-size:clamp(10px, ${fontSize}px, ${fontSize}px);
            font-weight:bold;
            color:#333;
            pointer-events:none;
            max-width:${size - 16}px;
            text-align:center;
            display:inline-block;
        ">${text}</span>
    `;
    // const iconImg = icon ? `<img src="${icon}" style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:${size/2}px;height:${size/2}px;">` : '';
    wrapper.innerHTML = circleSvg;
    return wrapper;
}

function createProgressMiddlePanel(percent, icon, text, color, index) {
    const wrapper = document.createElement('button');
    wrapper.style.border = 'none';
    wrapper.style.outline = 'none';
    wrapper.style.cursor = 'pointer';
    wrapper.style.padding = '0';
    wrapper.style.margin = '0';
    wrapper.style.position = 'relative';
    wrapper.style.display = 'flex';
    wrapper.style.flexDirection = 'column';
    wrapper.style.alignItems = 'center';
    wrapper.style.justifyContent = 'flex-end';
    wrapper.style.background = '#fff';
    wrapper.style.borderRadius = '16px';
    wrapper.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
    wrapper.style.overflow = 'hidden';

    const iconImg = `<img src="${icon}" style="width:100%;height:100%;object-fit:contain;display:block;">`;

    const percentValue = Math.round(percent);
    const textHtml = `
        <div style="width:100%;padding:12px 0 0 0;box-sizing:border-box;position:absolute;bottom:0;left:0;background:rgba(240,240,240,0.95);border-top:1px solid #eee;">
            <div style="text-align:center;font-size:1.1em;font-weight:600;color:#222;">${text}</div>
            <div style="margin:8px 12px 0 12px;">
                <div style="height:8px;width:100%;background:#e0e0e0;border-radius:4px;overflow:hidden;margin-bottom:15px;">
                    <div style="width:${percentValue}%;height:100%;background:${color};transition:width 0.5s;"></div>
                </div>
            </div>
        </div>
    `;
    wrapper.innerHTML = iconImg + textHtml;

    const hiddenDiv = document.createElement('div');
    hiddenDiv.style.display = 'none';
    hiddenDiv.textContent = "MIDDLE_PANEL=" + index;
    hiddenDiv.setAttribute('tag', 'function');
    wrapper.appendChild(hiddenDiv);

    wrapper.onclick = () => {
        console.log(hiddenDiv.textContent)
    };

    return wrapper;
}
