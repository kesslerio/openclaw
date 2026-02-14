#!/usr/bin/env node

const fs = require("fs");

let html = fs.readFileSync("index.html", "utf8");

// 1. Add task numbering CSS and display
const taskNumberCSS = `
        .task-number {
            position: absolute;
            top: 8px;
            left: 8px;
            background: #2C7DA0;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: 600;
        }
`;

html = html.replace("</style>", taskNumberCSS + "    </style>");

// Add task number to card creation
html = html.replace(
  `card.innerHTML = \``,
  `card.innerHTML = \`
                <div class="task-number">#\${task.id}</div>`,
);

// 2. Add category filter buttons before controls div
const categoryFilterHTML = `
        <div class="category-filters" style="display: flex; justify-content: center; gap: 10px; margin-bottom: 15px; flex-wrap: wrap;">
            <button class="btn" onclick="filterByCategory('all')" id="filter-all">All Tasks (46)</button>
            <button class="btn" onclick="filterByCategory('copper')" id="filter-copper">🟡 Copper AI</button>
            <button class="btn" onclick="filterByCategory('property')" id="filter-property">🔵 Property</button>
            <button class="btn" onclick="filterByCategory('personal')" id="filter-personal">🟣 Personal</button>
            <button class="btn" onclick="filterByCategory('nike')" id="filter-nike">🟪 Nike</button>
        </div>
`;

html = html.replace(
  '<div class="controls">',
  categoryFilterHTML + '\n        <div class="controls">',
);

// 3. Add collapsible sections CSS
const collapsibleCSS = `
        .details-section h3 {
            cursor: pointer;
            user-select: none;
        }
        
        .details-section h3:hover {
            color: #14546d;
        }
        
        .details-section h3::before {
            content: '▼ ';
            font-size: 0.8em;
            transition: transform 0.2s;
            display: inline-block;
        }
        
        .details-section.collapsed h3::before {
            content: '▶ ';
        }
        
        .details-section.collapsed .details-content,
        .details-section.collapsed > div:not(h3) {
            display: none;
        }
`;

html = html.replace("    </style>", collapsibleCSS + "    </style>");

// 4. Add multi-user PIN system
const userPINs = `
        // Multi-user PIN system
        const USER_PINS = {
            '408480': { name: 'Arvind', role: 'owner', canEdit: true },
            '123456': { name: 'Vee', role: 'admin', canEdit: true },
            '789012': { name: 'Megha', role: 'viewer', canEdit: false },
            '111111': { name: 'Nike', role: 'admin', canEdit: true }
        };
        
        let currentUser = null;
`;

html = html.replace("const PIN = '408480';", userPINs);

// Update checkPin function
html = html.replace(
  `if (input.value === PIN) {
                sessionStorage.setItem('kanban_auth', 'true');
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
                fetchTasks();
            } else {
                error.style.display = 'block';
                input.value = '';
                input.focus();
            }`,
  `const user = USER_PINS[input.value];
            if (user) {
                currentUser = user;
                sessionStorage.setItem('kanban_auth', 'true');
                sessionStorage.setItem('kanban_user', JSON.stringify(user));
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
                document.querySelector('.header h1').textContent = '🐾 ' + user.name + '\\'s Kanban';
                fetchTasks();
            } else {
                error.style.display = 'block';
                input.value = '';
                input.focus();
            }`,
);

// Add category filter function
const filterJS = `
        
        let currentFilter = 'all';
        
        function filterByCategory(category) {
            currentFilter = category;
            
            // Update button states
            document.querySelectorAll('.category-filters .btn').forEach(btn => {
                btn.style.background = 'white';
                btn.style.color = '#2C7DA0';
            });
            
            const activeBtn = document.getElementById('filter-' + category);
            if (activeBtn) {
                activeBtn.style.background = '#2C7DA0';
                activeBtn.style.color = 'white';
            }
            
            renderBoard();
        }
        
        // Update renderBoard to respect filter
        const originalRenderBoard = renderBoard;
        renderBoard = function() {
            const filteredTasks = currentFilter === 'all' 
                ? tasks 
                : tasks.filter(t => t.category === currentFilter);
            
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
            
            // Update filter button counts
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
        };
        
        // Make sections collapsible
        document.addEventListener('DOMContentLoaded', () => {
            document.querySelectorAll('.details-section h3').forEach(header => {
                header.addEventListener('click', (e) => {
                    e.target.closest('.details-section').classList.toggle('collapsed');
                });
            });
        });
`;

const lastScriptTag = html.lastIndexOf("</script>");
html = html.substring(0, lastScriptTag) + filterJS + html.substring(lastScriptTag);

fs.writeFileSync("index.html", html);
console.log("✅ Vee's 4 features added successfully!");
console.log("1. ✅ Task numbering (#ID on each card)");
console.log("2. ✅ Category filters (All, Copper, Property, Personal, Nike)");
console.log("3. ✅ Collapsible sections in details view");
console.log("4. ✅ Multi-user PINs (Arvind: 408480, Vee: 123456, Megha: 789012, Nike: 111111)");
