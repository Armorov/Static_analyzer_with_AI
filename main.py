from pathlib import Path
from json import dump, load

from index import indexing
from graber import build_called_by_tree
from graph_builder import generate_parrent_graph
from graph_builder import generate_child_graph
from child_builder import child_flow




if __name__ == '__main__':

    path_ = Path('./TEST')
    result_folder = './RESULTS'


    test_id = None
    #test_id = 'f09c57c50bf11ba939761824979bcf06'

    if not test_id:
        if path_.exists():
            # Этап №1 - сбор информации о функциях
            func_data = indexing(path_)
            with open(f'{result_folder}/origin_data.json', 'w', encoding='utf-8') as write_data:
                dump(func_data, write_data, indent=4)
        else:
            print('no data files')
            exit()

    if test_id:
        with open(f'{result_folder}/origin_data.json', 'r', encoding='utf-8') as read_data:
            func_data = load(read_data)
        # Этап №3.1 - построение цепочки по всем потомкам
        child_graber = child_flow(func_data, test_id)
        # Этап №3.2 - создание html файла содержащего граф вызовов от конкретного родителя до потомков
        generate_child_graph(child_graber, f'{result_folder}/{test_id}_children.html')
        # Этап №3.2 - построение цепочки родителей от ID потомка
        parrent_graber = build_called_by_tree(test_id, func_data)
        # Этап №3.3 - создание html файла содержащего граф вызовов от родителей до конкретного потомка 
        generate_parrent_graph(parrent_graber, f'{result_folder}/{test_id}_parrents.html')

