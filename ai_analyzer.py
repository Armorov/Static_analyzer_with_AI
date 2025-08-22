from hashlib import md5
from langchain_ollama import ChatOllama
from typing import List, Dict
from prompts import prompt_lang_setting
from tools.tool_manager import load_tools
import json

# настройки sitter под конкретный язык
sitter_lang_settings = {
    "kotlin": {'FUNC': 'function_declaration', 
               'CLASS': 'class_declaration',
               },
    "c": {'FUNC': 'function_definition', 
          'CLASS': None,
          },
}


# словарь всех доступных инструментов
TOOLS = load_tools()


def handle_tool_calls(response) -> Dict | None:
    """
    Обрабатывает вызов инструмента и возвращает результат одного вызова.
    """
    for call in getattr(response, "tool_calls", []):
        tool_name = call.get("name")
        args = call.get("args", {})
        func = TOOLS.get(tool_name)
        if func:
            try:
                return func(**args)
            except Exception as e:
                print(f"⚠️ Ошибка при вызове инструмента {tool_name}: {e}")
                return None
        else:
            print(f"⚠️ Инструмент {tool_name} не зарегистрирован.")
    return None


def ai_work(code, prompt) -> Dict | None:
    chat = ChatOllama(model='gpt-oss:20b', temperature=0.1)
    messages = [
        {'role':'system', 'content': f'''Ты эксперт в синтаксическом и семантическом анализе программного кода. 
         Для записи результатат воспользуйся одной из следующий функций save_func, save_class, save_source.
         Правила анализа кода: {prompt}.\n'''},
        {'role':'user', 'content': f'Код для анализа:\n{code}'}
    ]
    response = chat.invoke(messages, tools=list(TOOLS.values()))
    return handle_tool_calls(response)

TEST_CLASS_MODE = False
TEST_SOURCE_MODE = True

def analyze(queue, path, landuage_name):
    """
    Обходит дерево синтаксических узлов и вызывает ai_work для каждого узла-функции.
    """
    def get_text(node):
        return node.text.decode('utf-8') if node and node.text else ''

    functions = []
    current_function = None
    while queue:
        node, current_function = queue.popleft()
        if not node:
            continue

        if TEST_SOURCE_MODE:
            temp_dict = ai_work(get_text(node), prompt_lang_setting[landuage_name]['SOURCE'])
            print(json.dumps(temp_dict, ensure_ascii=False, indent=4))
            temp_dict.update({'PATH': path})
            for func in temp_dict.get('FUNCS'):
                id_name = f'{path}_{func.get('START_POINT')}'
                result = {'ID': f"{md5(id_name.encode()).hexdigest()}",
                        'VALUES': [],
                        'CALLED_BY': [],
                        'DEFINITION': [],
                }
                func.update(result)
            print(json.dumps(temp_dict, ensure_ascii=False, indent=4))
            exit()
            
            
        if node.type == sitter_lang_settings[landuage_name]['FUNC']:
            print('func')
            temp_dict = ai_work(get_text(node), prompt_lang_setting[landuage_name]['FUNC'])
            if temp_dict:
                id_name = f'{path}_{node.start_point[0] + 1}'
                result = {'ID': f"{md5(id_name.encode()).hexdigest()}",
                          'PATH': path,
                          'VALUES': [],
                          'CALLED_BY': [],
                          'DEFINITION': [],
                          'START_POINT': node.start_point[0] + 1,
                          'END_POINT': node.end_point[0] + 1
                        }
                result.update(temp_dict)
                functions.append(result)
                print(json.dumps(result, ensure_ascii=False, indent=4))
        
        elif TEST_CLASS_MODE and node.type == sitter_lang_settings[landuage_name]['CLASS']:
            print('class')
            temp_dict = ai_work(get_text(node), prompt_lang_setting[landuage_name]['CLASS'])
        
        # кладём детей в очередь
        for child in node.named_children:
            if child:
                queue.append((child, current_function))
    return functions
