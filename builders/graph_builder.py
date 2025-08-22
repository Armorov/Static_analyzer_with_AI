import json


def generate_html(graph_data, vis_network_path='vis-network.min.js'):
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Function Call Graph</title>
    <script type="text/javascript" src="VIS_NETWORK_PATH"></script>
    <style type="text/css">
        html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            font-family: Arial, sans-serif;
        }
        #mynetwork {
            width: 100%;
            height: 100vh;
        }
        #info-panel {
            position: absolute;
            right: 0;
            top: 0;
            width: 300px;
            height: 100vh;
            padding: 15px;
            box-sizing: border-box;
            overflow-y: auto;
            background: #f5f5f5;
            border-left: 1px solid #ddd;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 100;
        }
        #info-panel.visible {
            transform: translateX(0);
        }
        .info-field {
            margin-bottom: 15px;
        }
        .info-field label {
            display: block;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .info-field input, .info-field textarea {
            width: 100%;
            padding: 8px;
            box-sizing: border-box;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .info-field input[readonly] {
            background: #eee;
        }
        .info-field textarea {
            min-height: 100px;
            resize: vertical;
        }
        .highlighted {
            background-color: #7BE141 !important;
            border-color: #5BB82C !important;
        }
        .highlighted-edge {
            stroke: #5BB82C !important;
        }
        #search-container {
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 101;
            background: white;
            padding: 5px;
            border-radius: 5px;
            box-shadow: 0 0 5px rgba(0,0,0,0.2);
        }
        #search-input {
            width: 250px;
            padding: 5px;
        }
    </style>
</head>
<body>
    <div id="search-container">
        <input type="text" id="search-input" placeholder="Search function..." list="functions-list">
        <datalist id="functions-list"></datalist>
    </div>
    <div id="mynetwork"></div>
    <div id="info-panel">
        <div class="info-field">
            <label>FUNC_NAME</label>
            <input type="text" id="node-name" readonly>
        </div>
        <div class="info-field">
            <label>ID</label>
            <input type="text" id="node-id" readonly>
        </div>
        <div class="info-field">
            <label>PATH</label>
            <input type="text" id="node-path" readonly>
        </div>
        <div class="info-field">
            <label>START_POINT</label>
            <input type="text" id="node-string" readonly>
        </div>
        <div class="info-field">
            <label>Заметки</label>
            <textarea id="node-notes"></textarea>
        </div>
    </div>

    <script type="text/javascript">
        var nodes = new vis.DataSet(NODES_DATA);
        var edges = new vis.DataSet(EDGES_DATA);
        var selectedNodeId = null;
        var notesData = {};
        var infoPanel = document.getElementById('info-panel');
        var notesField = document.getElementById('node-notes');

        // Функция поиска всех связанных узлов (как в оригинале)
        function findConnectedNodes(nodeId, direction) {
            var connectedNodes = [];
            var stack = [nodeId];
            
            while(stack.length > 0) {
                var current = stack.pop();
                connectedNodes.push(current);
                var connected = network.getConnectedNodes(current, direction);
                connected.forEach(function(node) {
                    if(connectedNodes.indexOf(node) === -1) {
                        stack.push(node);
                    }
                });
            }
            return connectedNodes;
        }

        function resetHighlight() {
            nodes.forEach(function(node) {
                nodes.update({
                    id: node.id,
                    color: {
                        background: '#D2E5FF',
                        border: '#2B7CE9'
                    }
                });
            });
            edges.forEach(function(edge) {
                edges.update({
                    id: edge.id,
                    color: {color: '#848484'}
                });
            });
        }

        // Заполняем datalist для автодополнения
        var functionsList = document.getElementById('functions-list');
        nodes.forEach(function(node) {
            var option = document.createElement('option');
            option.value = node.label + " (" + (node.path || 'N/A') + ")";
            option.dataset.nodeId = node.id;
            functionsList.appendChild(option);
        });

        var searchInput = document.getElementById('search-input');
        searchInput.addEventListener('input', function() {
            var value = searchInput.value;
            var found = nodes.get().find(n => value.startsWith(n.label));
            if(found) {
                // Имитируем клик по узлу, чтобы сохранить подсветку и панель
                network.selectNodes([found.id]);
                network.focus(found.id, {animation:true});
                network.emit("click", {nodes: [found.id]});
            }
        });

        var container = document.getElementById('mynetwork');
        var data = { nodes: nodes, edges: edges };
        var options = {
            layout: {
                improvedLayout: true,
                hierarchical: {
                    direction: "UD",
                    sortMethod: "directed",
                    nodeSpacing: 200,
                    levelSeparation: 200,
                    treeSpacing: 200,
                    edgeMinimization: true,
                    parentCentralization: true,
                    blockShifting: true
                }
            },
            physics: {
                hierarchicalRepulsion: { nodeDistance: 250, centralGravity: 0.0, springLength: 250, springConstant: 0.01, damping: 0.09 },
                solver: "hierarchicalRepulsion",
                stabilization: { enabled: true, iterations: 1000, updateInterval: 25 }
            },
            edges: {
                smooth: { enabled: true, type: 'curvedCW', roundness: 0.2 },
                arrows: { to: { enabled: true, scaleFactor: 0.8 } },
                color: { color: '#848484', highlight: '#5BB82C' }
            },
            nodes: { shape: 'box', margin: 10, font: { size: 12, face: 'Tahoma' }, widthConstraint: { minimum: 150 }, heightConstraint: { minimum: 50 } },
            interaction: { dragNodes: true, dragView: true, zoomView: true, hideEdgesOnDrag: false, tooltipDelay: 200 }
        };
        var network = new vis.Network(container, data, options);

        network.on("click", function(params) {
            if(params.nodes.length > 0) {
                selectedNodeId = params.nodes[0];
                var node = nodes.get(selectedNodeId);

                resetHighlight();

                var upstreamNodes = findConnectedNodes(selectedNodeId, 'from');
                var downstreamNodes = findConnectedNodes(selectedNodeId, 'to');
                var allConnectedNodes = [...new Set([...upstreamNodes, ...downstreamNodes, selectedNodeId])];

                allConnectedNodes.forEach(function(nodeId) {
                    nodes.update({
                        id: nodeId,
                        color: {
                            background: '#7BE141',
                            border: '#5BB82C'
                        }
                    });
                });

                infoPanel.classList.add('visible');
                document.getElementById('node-name').value = node.label;
                document.getElementById('node-id').value = node.id;
                document.getElementById('node-path').value = node.path || 'N/A';
                document.getElementById('node-string').value = node.string_num || 'N/A';
                notesField.value = node.notes || '';
            } else {
                resetHighlight();
                selectedNodeId = null;
                infoPanel.classList.remove('visible');
            }
        });

        notesField.addEventListener('input', function() {
            if(selectedNodeId) {
                nodes.update({id: selectedNodeId, notes: notesField.value});
                notesData[selectedNodeId] = notesField.value;
                localStorage.setItem('functionCallGraphNotes', JSON.stringify(notesData));
            }
        });

        // Загрузка сохранённых заметок
        var savedNotes = localStorage.getItem('functionCallGraphNotes');
        if(savedNotes) {
            notesData = JSON.parse(savedNotes);
            nodes.forEach(function(node) {
                if(notesData[node.id]) {
                    node.notes = notesData[node.id];
                    nodes.update(node);
                }
            });
        }

        network.on("stabilizationIterationsDone", function() {
            network.fit({animation: {duration: 1000, easingFunction: 'easeInOutQuad'}});
        });
    </script>
</body>
</html>
"""
    html = html_template.replace("VIS_NETWORK_PATH", vis_network_path)\
                        .replace("NODES_DATA", json.dumps(graph_data['nodes']))\
                        .replace("EDGES_DATA", json.dumps(graph_data['edges']))
    return html



def generate_child_graph(input_data, output_file, vis_network_path='vis-network.min.js'):
    def get_child_nodes_from_tree(func):
        nodes = []
        edges = []
        node_ids = set()
        edge_set = set()
        visited = set()

        def traverse(node):
            func_id = node.get('ID')
            func_name = node.get('FUNC_NAME', 'unknown')
            func_path = node.get('PATH', 'не найдено')
            func_string = str(node.get('START_POINT', 'не найдено'))

            if not func_id or func_id in visited:
                return
            visited.add(func_id)

            node_data = {
                'id': func_id,
                'label': func_name,
                'title': f"ID: {func_id}\nName: {func_name}",
                'font': {'size': 12},
                'margin': 5,
                'shape': 'box',
                'color': {
                    'background': '#D2E5FF',
                    'border': '#2B7CE9',
                    'highlight': {
                        'background': '#97C2FC',
                        'border': '#2B7CE9'
                    }
                },
                'path': func_path,
                'string_num': func_string,
                'notes': ''
            }

            if func_id not in node_ids:
                nodes.append(node_data)
                node_ids.add(func_id)

            for callee in node.get('CALL_LIST', []):
                callee_id = callee.get('ID')
                if not callee_id or callee_id in visited:
                    continue

                if (func_id, callee_id) not in edge_set:
                    edges.append({
                        'from': func_id,
                        'to': callee_id,
                        'arrows': 'to',
                        'smooth': {
                            'type': 'curvedCW',
                            'roundness': 0.2
                        },
                        'color': {'color': '#848484'}
                    })
                    edge_set.add((func_id, callee_id))

                traverse(callee)

        traverse(func)
        return {'nodes': nodes, 'edges': edges}


    try:
        if not input_data or not isinstance(input_data, dict):
            raise ValueError("[!] Неверный формат даннных")

        graph = get_child_nodes_from_tree(input_data)
        
        if not graph['nodes']:
            print("[!] Нет узлов для генерации графа")
        
        html_content = generate_html(graph, vis_network_path)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[V] HTML успешно создан: {output_file}")
    except Exception as e:
        print(f"[X] Ошибка: {e}")




def generate_parrent_graph(input_data, output_file, vis_network_path='vis-network.min.js'):
    def get_parrent_nodes(data):
        nodes = []
        edges = []
        node_ids = set()
        edge_set = set()

        def traverse(func, parent_id=None):
            if not func or 'ID' not in func or 'FUNC_NAME' not in func:
                return

            func_id = func['ID']
            func_name = func['FUNC_NAME']
            func_path = func.get('PATH', 'не найдено')
            func_string = str(func.get('START_POINT', 'не найдено'))

            node_data = {
                'id': func_id,
                'label': func_name,
                'title': f"ID: {func_id}\nName: {func_name}",
                'font': {'size': 12},
                'margin': 5,
                'shape': 'box',
                'color': {
                    'background': '#D2E5FF',
                    'border': '#2B7CE9',
                    'highlight': {
                        'background': '#97C2FC',
                        'border': '#2B7CE9'
                    }
                },
                'path': func_path,
                'string_num': func_string,
                'notes': ''
            }

            if func_id not in node_ids:
                nodes.append(node_data)
                node_ids.add(func_id)

            if parent_id and (parent_id, func_id) not in edge_set:
                edges.append({
                    'from': parent_id,
                    'to': func_id,
                    'arrows': 'to',
                    'smooth': {
                        'type': 'curvedCW',
                        'roundness': 0.2
                    },
                    'color': {'color': '#848484'}
                })
                edge_set.add((parent_id, func_id))

            if 'CALLED_BY' in func and isinstance(func['CALLED_BY'], list):
                for called_func in func['CALLED_BY']:
                    traverse(called_func, func_id)

        traverse(data)
        return {'nodes': nodes, 'edges': edges}


    try:
        if not input_data or not isinstance(input_data, dict):
            raise ValueError("[!] Неверный формат даннных")

        graph = get_parrent_nodes(input_data)
        
        if not graph['nodes']:
            print("[!] Нет узлов для генерации графа")
        
        html_content = generate_html(graph, vis_network_path)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[V] HTML успешно создан: {output_file}")
    except Exception as e:
        print(f"[X] Ошибка: {e}")
