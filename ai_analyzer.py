import os
import json
from hashlib import md5
from langchain_ollama import ChatOllama
from typing import List, Dict


prompt_lang_setting = {
    "kotlin": {'FUNC': """
               ты анализируешь код на языке программирования Kotlin.
               Твоя задача выделить:
               FUNC_PATH - путь до файла, где реализован код
               FUNC_NAME - имя анализируемой функции
               ARG_LIST- список аргументов которые она принимает вида {'NAME': имя аргумента, 'TYPE': тип аргумента} 
               FUNC_LIST - список имен вызовов в теле этой функции вида {'NAME': имя вызываемой функции или метода, 'ARGS': список имен объектов, которые она принимает} 
               """},
    "c": {},
}


sitter_lang_settings = {
    "kotlin": {'FUNC': 'function_declaration', 
               'CLASS': None
               },
    "c": {'FUNC': 'function_definition', 
          'CLASS': None
          },
}


def save_results(FUNC_PATH: str, FUNC_NAME: str, ARG_LIST: List[Dict], FUNC_LIST: List[Dict]):
    """
  Сохраняет результат анализа кода

  Args:
        FUNC_NAME - имя анализируемой функции
        ARG_LIST - список аргументов которые она принимает вида {'NAME': имя аргумента, 'TYPE': тип аргумента} 
        FUNC_LIST - список имен вызовов в теле этой функции вида {'NAME': имя вызываемой функции или метода, 'ARGS': список имен объектов, которые она принимает} 
    """
    print(FUNC_PATH, FUNC_NAME, ARG_LIST, FUNC_LIST)


# словарь всех доступных инструментов
TOOLS = {
    "save_results": save_results,
    # сюда можно добавлять новые функции, которые LLM может вызвать
}


def handle_tool_calls(response):
    """
    Обрабатывает все вызовы инструментов из LLM-ответа.
    Для каждого вызова ищет Python-функцию по имени и вызывает её с аргументами.
    Работа обёрнута в try/except, чтобы ошибки одного инструмента не падали весь процесс.
    """
    for call in getattr(response, "tool_calls", []):
        tool_name = call.get("name")
        args = call.get("args", {})
        func = TOOLS.get(tool_name)
        if func:
            try:
                func(**args)
            except Exception as e:
                print(f"⚠️ Ошибка при вызове инструмента {tool_name}: {e}")
        else:
            print(f"⚠️ Инструмент {tool_name} не зарегистрирован.")


def ai_work(code, prompt, path):
    chat = ChatOllama(model='qwen3:30b-a3b-instruct-2507-q4_K_M', temperature=0.1)
    messages = [
        {'role':'system', 'content': f'Ты эксперт в синтаксическом и сематическом анализе программного кода. Правила анализа кода: {prompt}.\n'},
        {'role':'user', 'content': f'Код реализован в файле {path}. Код для анализа:\n{code}'}
    ]

    response = chat.invoke(messages, tools=list(TOOLS.values()))
    handle_tool_calls(response)  # теперь все инструменты вызовутся автоматически


def analyze(queue, path, landuage_name):
    """
    Обходит дерево синтаксических узлов и вызывает ai_work для каждого узла-функции.
    """
    def get_text(node):
        return node.text.decode('utf-8') if node and node.text else ''

    current_function = None
    while queue:
        node, current_function = queue.popleft()
        if not node:
            continue

        if node.type == sitter_lang_settings[landuage_name]['FUNC']:
            ai_work(get_text(node), prompt_lang_setting[landuage_name]['FUNC'], path)

        # кладём детей в очередь
        for child in node.named_children:
            if child:
                queue.append((child, current_function))