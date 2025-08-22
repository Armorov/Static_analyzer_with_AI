# tools/save_results.py
from typing import List, Dict


def save_func(CLASS_NAME: str, FUNC_NAME: str, ARG_LIST: List[Dict], CALL_LIST: List[Dict]):
    """Сохраняет результат анализа функции"""
    print('FUNC_RES')
    return {
        "CLASS_NAME": CLASS_NAME,
        "FUNC_NAME": FUNC_NAME,
        "ARG_LIST": ARG_LIST,
        "CALL_LIST": CALL_LIST,
    }
save_func.name = "save_results"


def save_class(CLASS_LIST: List[Dict]):
    """Сохраняет результат анализа класса или интерфейса или структуры"""
    #print(CLASS_LIST)
    print('CLASS_RES')
    return CLASS_LIST
save_class.name = "save_class"


def save_source(SOURCE_LIST: Dict):
    """Сохраняет результат анализа кода программы"""
    return SOURCE_LIST
save_source.name = "save_source"
