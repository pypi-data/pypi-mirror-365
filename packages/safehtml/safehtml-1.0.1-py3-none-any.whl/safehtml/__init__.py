from string.templatelib import Template
from html import escape
from typing import Literal


def _convert(value: object, conversion: Literal['a', 'r', 's'] | None) -> object:
    match conversion:
        case 'a':
            return ascii(value)
        case 'r':
            return repr(value)
        case 's':
            return str(value)

    return value


def html(template: Template) -> str:
    assert isinstance(template, Template), f'Expected a Template from a t-string, but got {type(template).__name__}.'

    result = []
    for item in template:
        if isinstance(item, str):
            result.append(item)
        else:
            converted_val = _convert(item.value, item.conversion)
            formatted_val = format(converted_val, item.format_spec)
            safe_val = escape(str(formatted_val))
            result.append(safe_val)

    return ''.join(result)
