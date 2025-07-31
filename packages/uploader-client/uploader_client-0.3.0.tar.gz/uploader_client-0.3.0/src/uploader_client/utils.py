from importlib import (
    import_module,
)


def import_string(dotted_path: str):
    """
    Импортирует модуль по указанному пути, и возвращает атрибут/класс указанный последним элементом пути. В случае
    ошибочного импорта возникает исключение ImportError.
    """

    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError as err:
        raise ImportError(f"{dotted_path} doesn't look like a module path") from err

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        raise ImportError(f'Module "{module_path}" does not define a "{class_name}" attribute/class') from err
