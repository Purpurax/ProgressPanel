const COLOR_PALETTE = [
    // Base colors (6)
    '#000000', // Black
    '#ffffff', // White  
    '#e6e600', // Yellow
    '#cc0000', // Red
    '#0033cc', // Blue
    '#00cc00', // Green
    
    // 1/2 mixes with white (lighter variants) (6)
    '#737300', // Yellow + Black (1/2)
    '#660000', // Red + Black (1/2)
    '#001966', // Blue + Black (1/2)
    '#006600', // Green + Black (1/2)
    '#f3f300', // Yellow + White (1/2)
    '#e60066', // Red + White (1/2)
    
    // 1/4 mixes creating darker tones (4)
    '#808080', // Black + White (1/2)
    '#f9f980', // Yellow + White (1/4 yellow)
    '#ff8080', // Red + White (1/4 red)
    '#8099ff', // Blue + White (1/4 blue)
    
    // Creative color combinations (4)
    '#666600', // Yellow + Green (1/2 each)
    '#800080', // Red + Blue (1/2 each)
    '#339900', // Green + Blue (1/4 blue, 3/4 green)
    '#cc6600'  // Red + Yellow (1/2 each)
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
        calendarIframe.contentWindow.scrollTo(0, 0);
    });
}

function configure_active_project(active_project) {
    // Total progress bar
    const fg = document.querySelector('.foreground');
    const title = document.querySelector('.progress-label');
    fg.style.width = active_project.total_progress * 100 + '%';
    fg.style.backgroundColor = COLOR_PALETTE[active_project.general_color_index];
    title.textContent = active_project.full_name + " Progress";
    title.style.fontSize = '30px';

    // Category progress bars
    const circleList = document.getElementById('circle-progress-list');
    const progressbar = createProgressByCategory(
        active_project.categories.map(category =>
            [
                category.name,
                category.todos.length,
                COLOR_PALETTE[category.color_index]
            ]
        )
    );
    circleList.appendChild(progressbar);

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
        const circular_progress = createProgressMiddlePanel(
            project.total_progress * 100,
            project.icon_image,
            project.short_name,
            COLOR_PALETTE[project.general_color_index],
            idx
        );
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
        const unavailableColor = COLOR_PALETTE[12];

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



function createProgressByCategory(category_values) {
    const sorted = [...category_values].sort((a, b) => b[1] - a[1]);
    const total = sorted.reduce((sum, [, count]) => sum + count, 0);

    const wrapper = document.createElement('div');
    wrapper.style.display = 'flex';
    wrapper.style.alignItems = 'center';
    wrapper.style.width = '100%';
    wrapper.style.height = '10%';
    wrapper.style.margin = '16px 0';

    const bar = document.createElement('div');
    bar.style.display = 'flex';
    bar.style.height = '28px';
    bar.style.width = '100%';
    bar.style.borderRadius = '8px';
    bar.style.border = 'solid';
    bar.style.borderWidth = '2px';
    bar.style.borderColor = '#000000';
    bar.style.overflow = 'hidden';
    bar.style.position = 'relative';

    sorted.forEach(([name, count, color]) => {
        const percent = total === 0 ? 0 : (count / total) * 100;
        const segment = document.createElement('div');
        segment.style.flex = percent + ' 0 0';
        segment.style.background = color;
        segment.style.height = '100%';
        segment.style.position = 'relative';
        segment.title = `${name}: ${count} (${percent.toFixed(1)}%)`;

        // If segment is big enough, show label inside
        if (percent > 25) {
            const label = document.createElement('span');
            label.textContent = name;
            label.style.position = 'absolute';
            label.style.left = '50%';
            label.style.top = '50%';
            label.style.transform = 'translate(-50%, -50%)';
            label.style.fontWeight = 'bold';
            label.style.fontSize = '0.95em';
            label.style.textWrap = 'nowrap';
            // Choose readable color
            label.style.color = getContrastYIQ(color);
            segment.appendChild(label);
        }

        bar.appendChild(segment);
    });

    wrapper.appendChild(bar);

    return wrapper;

    function getContrastYIQ(hexcolor) {
        hexcolor = hexcolor.replace('#', '');
        if (hexcolor.length === 3) {
            hexcolor = hexcolor.split('').map(x => x + x).join('');
        }
        const r = parseInt(hexcolor.substr(0,2),16);
        const g = parseInt(hexcolor.substr(2,2),16);
        const b = parseInt(hexcolor.substr(4,2),16);
        const yiq = ((r*299)+(g*587)+(b*114))/1000;
        return (yiq >= 128) ? '#222' : '#fff';
    }
}

function createProgressMiddlePanel(percent, icon, text, color, index) {
    const wrapper = document.createElement('button');
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
    wrapper.style.borderColor = '#000000';
    wrapper.style.borderStyle = 'solid';
    wrapper.style.borderWidth = '2px';
    wrapper.style.overflow = 'hidden';

    const iconImg = `<img src="${icon}" style="width:100%;height:100%;object-fit:contain;display:block;">`;

    const percentValue = Math.round(percent);
    const textHtml = `
        <div style="width:100%;padding:12px 0 0 0;position:absolute;bottom:0;left:0;background:rgba(256,256,256,0.93);border-width:2px 0 0 0;border-color:#000000;border-style:solid;">
            <div style="text-align:center;font-size:18px;font-weight:600;color:#222;">${text}</div>
            <div style="margin:8px 12px 0 12px;">
                <div style="height:8px;width:100%;border-width:2px;border-color:#000000;border-style:solid;background:#e0e0e0;border-radius:4px;overflow:hidden;margin-bottom:15px;">
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
