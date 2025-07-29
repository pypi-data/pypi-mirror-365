from typing import Any


def omit_empty(dict_to_update: dict[str, Any]):
    new_dict = {}
    for key, value in dict_to_update.items():
        if value:
            new_dict[key] = value
    return new_dict
