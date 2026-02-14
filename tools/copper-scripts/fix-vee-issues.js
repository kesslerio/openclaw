#!/usr/bin/env node

const fs = require("fs");

let html = fs.readFileSync("index.html", "utf8");

// 1. Fix task number positioning - move it to bottom-right instead of top-left
html = html.replace(
  `.task-number {
            position: absolute;
            top: 8px;
            left: 8px;
            background: #2C7DA0;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: 600;
        }`,
  `.task-number {
            position: absolute;
            bottom: 8px;
            right: 8px;
            background: #2C7DA0;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: 600;
            opacity: 0.8;
        }`,
);

// 2. Add tabs CSS
const tabsCSS = `
        /* Task View Tabs */
        .task-tabs {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        
        .tab-btn {
            background: rgba(255,255,255,0.7);
            color: #2C7DA0;
            border: 2px solid transparent;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 1.1em;
            transition: all 0.2s;
        }
        
        .tab-btn:hover {
            background: rgba(255,255,255,0.9);
        }
        
        .tab-btn.active {
            background: white;
            border-color: #2C7DA0;
            box-shadow: 0 4px 12px rgba(44, 125, 160, 0.3);
        }
        
        .assignee-filter {
            display: none;
            justify-content: center;
            gap: 8px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        
        .assignee-filter.show {
            display: flex;
        }
        
        .assignee-btn {
            background: rgba(255,255,255,0.7);
            color: #2C7DA0;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.2s;
        }
        
        .assignee-btn:hover {
            background: rgba(255,255,255,0.9);
        }
        
        .assignee-btn.active {
            background: #2C7DA0;
            color: white;
        }
`;

html = html.replace("    </style>", tabsCSS + "    </style>");

// 3. Add tabs HTML before category filters
const tabsHTML = `
        <div class="task-tabs">
            <button class="tab-btn active" onclick="switchTab('my-tasks')">📌 My Tasks</button>
            <button class="tab-btn" onclick="switchTab('all-tasks')">📋 All Tasks</button>
        </div>
        
        <div class="assignee-filter" id="assignee-filter">
            <span style="color: white; font-weight: 600;">Filter by:</span>
            <button class="assignee-btn active" onclick="filterByAssignee('all')">All</button>
            <button class="assignee-btn" onclick="filterByAssignee('Arvind')">Arvind</button>
            <button class="assignee-btn" onclick="filterByAssignee('Nike')">Nike</button>
            <button class="assignee-btn" onclick="filterByAssignee('VEENA')">VEENA</button>
            <button class="assignee-btn" onclick="filterByAssignee('Megha')">Megha</button>
        </div>
`;

html = html.replace(
  '<div class="category-filters"',
  tabsHTML + '\n        <div class="category-filters"',
);

// 4. Add JavaScript for tabs and assignee filtering
const tabJS = `
        
        let currentTab = 'my-tasks';
        let currentAssignee = 'all';
        
        function switchTab(tab) {
            currentTab = tab;
            
            // Update tab button states
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Show/hide assignee filter
            const assigneeFilter = document.getElementById('assignee-filter');
            if (tab === 'all-tasks') {
                assigneeFilter.classList.add('show');
            } else {
                assigneeFilter.classList.remove('show');
            }
            
            // Re-render board with new filter
            renderBoard();
        }
        
        function filterByAssignee(assignee) {
            currentAssignee = assignee;
            
            // Update assignee button states
            document.querySelectorAll('.assignee-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            renderBoard();
        }
        
        // Override the renderBoard filter logic
        const _originalRenderBoard = renderBoard;
        renderBoard = function() {
            let filteredTasks = tasks;
            
            // Apply tab filter (My Tasks vs All Tasks)
            if (currentTab === 'my-tasks' && currentUser) {
                // Show only tasks assigned to current user
                filteredTasks = filteredTasks.filter(t => t.owner === currentUser.name);
            }
            
            // Apply assignee filter (only in All Tasks tab)
            if (currentTab === 'all-tasks' && currentAssignee !== 'all') {
                filteredTasks = filteredTasks.filter(t => t.owner === currentAssignee);
            }
            
            // Apply category filter
            if (currentFilter !== 'all') {
                filteredTasks = filteredTasks.filter(t => t.category === currentFilter);
            }
            
            const columns = {
                todo: document.getElementById('todo-cards'),
                doing: document.getElementById('doing-cards'),
                review: document.getElementById('review-cards'),
                done: document.getElementById('done-cards')
            };
            
            Object.values(columns).forEach(col => col.innerHTML = '');
            
            filteredTasks.forEach(task => {
                const card = createCard(task);
                columns[task.status].appendChild(card);
            });
            
            updateStats();
            setupDragAndDrop();
            updateFilterCounts();
        };
        
        function updateFilterCounts() {
            const counts = {
                all: tasks.length,
                copper: tasks.filter(t => t.category === 'copper').length,
                property: tasks.filter(t => t.category === 'property').length,
                personal: tasks.filter(t => t.category === 'personal').length,
                nike: tasks.filter(t => t.category === 'nike').length
            };
            
            document.getElementById('filter-all').textContent = \`All Tasks (\${counts.all})\`;
            document.getElementById('filter-copper').textContent = \`🟡 Copper AI (\${counts.copper})\`;
            document.getElementById('filter-property').textContent = \`🔵 Property (\${counts.property})\`;
            document.getElementById('filter-personal').textContent = \`🟣 Personal (\${counts.personal})\`;
            document.getElementById('filter-nike').textContent = \`🟪 Nike (\${counts.nike})\`;
        }
`;

const lastScriptTag = html.lastIndexOf("</script>");
html = html.substring(0, lastScriptTag) + tabJS + html.substring(lastScriptTag);

// 5. Update the user restore to set currentUser properly
html = html.replace(
  `if (sessionStorage.getItem('kanban_auth') === 'true') {
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
                fetchTasks();
            }`,
  `if (sessionStorage.getItem('kanban_auth') === 'true') {
                const savedUser = sessionStorage.getItem('kanban_user');
                if (savedUser) {
                    currentUser = JSON.parse(savedUser);
                    document.querySelector('.header h1').textContent = '🐾 ' + currentUser.name + '\\'s Kanban';
                }
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
                fetchTasks();
            }`,
);

fs.writeFileSync("index.html", html);
console.log("✅ Fixed both issues!");
console.log("1. ✅ Task# moved to bottom-right (no overlap)");
console.log('2. ✅ Added "My Tasks" / "All Tasks" tabs');
console.log('3. ✅ "My Tasks" is default view (shows only your tasks)');
console.log('4. ✅ Assignee filter in "All Tasks" tab');
