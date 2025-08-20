def child_flow(functions: list, start_id: str, depth=0, max_depth=10, visited=None):
    if visited is None:
        visited = set()

    # Индексируем функции по ID для быстрого доступа
    function_map = {fn["ID"]: fn for fn in functions}

    if start_id not in function_map or start_id in visited or depth > max_depth:
        return None

    visited.add(start_id)
    fn = function_map[start_id]

    result = {
        "ID": fn["ID"],
        "NAME": fn["NAME"],
        "CALLS": [],
        "PATH": fn["PATH"],
        "STRING": fn["STRING"]
    }

    for call in fn.get("CALLS", []):
        for callee_id in call.get("ID", []):
            subtree = child_flow(functions, callee_id, depth + 1, max_depth, visited)
            if subtree:
                result["CALLS"].append(subtree)

    return result
