# python 3 headers, required if submitting to Ansible

from __future__ import absolute_import, division, print_function

__metaclass__ = type
import re
from typing import Any

from ansible.utils.display import Display

display = Display()


class FilterModule(object):
    """
    ansible filter
    """

    def filters(self):
        return {
            "network_bind": self.network_bind,
            "redis_to_valkey": self.redis_to_valkey,
        }

    def network_bind(self, data):
        """ """
        display.v(f"bodsch.redis::network_bind(data : {data}")
        result = []

        if isinstance(data, str):
            result.append(data)

        if isinstance(data, list):
            result = data

        # display.v(f"return : {result}")
        return result

    def redis_to_valkey(self, data):
        """ """
        display.v(f"bodsch.redis::redis_to_valkey(data : {data}")

        result = replace_strings_in_values(
            obj=data,
            needle="redis",
            replacement="valkey",
            ignore_case=True,
            whole_word=False,
        )

        display.v(f"return : {result}")
        return result


def replace_strings_in_values(
    obj: Any,
    needle: str,
    replacement: str,
    *,
    ignore_case: bool = True,
    whole_word: bool = False,
) -> Any:
    """
    Ersetzt in allen *Values* von dict/list/tuple/set Strings per Regex.
    Keys bleiben unverändert. Gibt eine neue, transformierte Struktur zurück.
    """
    pattern = re.escape(needle)
    if whole_word:
        pattern = rf"\b{pattern}\b"

    flags = re.IGNORECASE if ignore_case else 0
    rx = re.compile(pattern, flags)

    def _walk(x: Any) -> Any:
        if isinstance(x, str):
            return rx.sub(replacement, x)

        if isinstance(x, dict):
            # nur Values verändern
            return {k: _walk(v) for k, v in x.items()}

        if isinstance(x, list):
            return [_walk(i) for i in x]

        if isinstance(x, tuple):
            return tuple(_walk(i) for i in x)

        if isinstance(x, set):
            return {_walk(i) for i in x}

        return x

    return _walk(obj)
