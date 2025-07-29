from collections.abc import Mapping
from typing import Self

import attrs

from liblaf import grapes

from .constants import TANGERINE_START


@attrs.define
class Template:
    name: str = attrs.field()
    context: Mapping[str, str] = attrs.field(factory=dict)
    lines: list[str] = attrs.field(factory=list)

    @classmethod
    def from_lines(cls, lines: list[str]) -> Self:
        line: str = lines[0]
        idx: int = line.find(TANGERINE_START)
        line = line[idx + len(TANGERINE_START) :].strip()
        items: list[str] = line.split(maxsplit=1)
        name: str
        vars_str: str
        if len(items) == 1:
            (name,) = items
            vars_str = "{}"
        else:
            name, vars_str = items
            vars_str = vars_str[vars_str.find("{") :]
            vars_str = vars_str[: vars_str.rfind("}") + 1]
        return cls(name=name, context=grapes.yaml.decode(vars_str) or {}, lines=lines)
