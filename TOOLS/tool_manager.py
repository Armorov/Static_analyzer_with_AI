import importlib
import pkgutil
import tools

def load_tools():
    tool_dict = {}
    for _, module_name, _ in pkgutil.iter_modules(tools.__path__):
        module = importlib.import_module(f"tools.{module_name}")
        for attr_name in dir(module):
            obj = getattr(module, attr_name)
            # берём только функции/классы, у которых есть атрибут .name
            if callable(obj) and hasattr(obj, "name"):
                tool_dict[getattr(obj, "name")] = obj
    return tool_dict
