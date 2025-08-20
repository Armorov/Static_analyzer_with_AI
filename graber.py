import copy

# Рекурсивно строим дерево вызовов от target_id вверх по CALLED_BY.
def build_called_by_tree(target_id, functions, visited=None):
    id_to_func = {func['ID']: func for func in functions}
    if visited is None:
        visited = set()
    if target_id in visited:
        # Возвращаем заглушку для циклической ссылки
        return {'ID': target_id, 'CYCLE': True}
    visited.add(target_id)
    try:
        func = copy.deepcopy(id_to_func[target_id])
    except:
        print('[X] ID не найден')
        exit()
    func['CALLED_BY'] = []

    for parent_id in id_to_func[target_id].get('CALLED_BY', []):
        if parent_id in id_to_func:
            parent_tree = build_called_by_tree(parent_id, functions, visited.copy())
            func['CALLED_BY'].append(parent_tree)
    return func