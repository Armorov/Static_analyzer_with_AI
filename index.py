from tree_sitter import Parser
from tree_sitter_language_pack import get_language

from ai_analyzer import analyze

from collections import deque


LANGUAGE_EXTENSIONS = {
    ".py": "python",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".js": "javascript",
    ".ts": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".swift": "swift",
    ".kt": "kotlin",
}


def indexing(target):
    all_functions = []

    for path in target.rglob("*"):
        if path.suffix.lower() in LANGUAGE_EXTENSIONS and path.is_file():
            chunks = {'FILE': None, 'DATA': None}
            print(f"[+] Обработка: {path.relative_to(target)}")
            try:
                code_text = path.read_text(encoding="utf-8")
            except Exception as e:
                print(f"[X] Ошибка чтения {path}: {e}")
                continue

            language_name = LANGUAGE_EXTENSIONS[path.suffix.lower()]
            try:
                language = get_language(language_name)
            except Exception as e:
                raise ValueError(f"[X] Не удалось загрузить язык '{language_name}': {e}")
            parser = Parser(language)

            tree = parser.parse(bytes(code_text, "utf8"))
            root_node = tree.root_node
            queue = deque([(root_node, None)])
            chunks = analyze(queue, str(path), language_name)
            exit()
            all_functions.extend(chunks)

    if all_functions:
        return all_functions
    else:
        print("[!] Не найдено документов для индексации.")
        return None