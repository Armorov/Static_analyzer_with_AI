def link_calls_with_ids(functions: list) -> list:
    """
    Проходит по всем функциям и для каждого вызова в CALL_LIST
    находит возможные реализации функций по имени и добавляет список их ID.
    Если имя вызова составное (order.total, obj->method), берется правая часть.
    """
    # индексируем функции по имени
    name_map = {}
    for fn in functions:
        fname = fn.get("FUNC_NAME")
        if fname:
            name_map.setdefault(fname, []).append(fn["ID"])

    def normalize_name(name: str) -> str:
        # оставляем самую правую часть по '.', '->'
        if not name:
            return ""
        for sep in [".", "->"]:
            if sep in name:
                name = name.split(sep)[-1]
        return name.strip()

    # обогащаем CALL_LIST
    for fn in functions:
        for call in fn.get("CALL_LIST", []):
            raw_name = call.get("NAME")
            callee_name = normalize_name(raw_name)
            if callee_name and callee_name in name_map:
                call["ID"] = name_map[callee_name]  # список ID возможных реализаций
            else:
                call["ID"] = []

    return functions


def child_flow(functions: list, start_id: str, depth=0, max_depth=10, visited=None):
    functions = link_calls_with_ids(functions=functions)
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
        "FUNC_NAME": fn["FUNC_NAME"],
        "CALL_LIST": [],
        "PATH": fn["PATH"],
        "START_POINT": fn["START_POINT"]
    }

    for call in fn.get("CALL_LIST", []):
        for callee_id in call.get("ID", []):
            subtree = child_flow(functions, callee_id, depth + 1, max_depth, visited)
            if subtree:
                result["CALL_LIST"].append(subtree)

    return result
