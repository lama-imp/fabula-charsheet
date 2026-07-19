from __future__ import annotations

import ast
import re

from pydantic import BaseModel
from typing import TYPE_CHECKING
from enum import StrEnum, auto

from .class_name import ClassName

if TYPE_CHECKING:
    from data.models import LocNamespace

_BRACKET_PATTERN = re.compile(r"【([^】]*)】")
_ALLOWED_AST_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Constant,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.USub,
    ast.UAdd,
)


def _resolve_skill_level_placeholders(text: str, level: int, token: str) -> str:
    if not token:
        return text

    token_pattern = re.compile(rf"\b{re.escape(token)}\b")

    def resolve_bracket(match: re.Match) -> str:
        content = token_pattern.sub(str(level), match.group(1))

        expression = content.replace("&nbsp;", " ").replace("×", "*").replace("x", "*")
        try:
            tree = ast.parse(expression, mode="eval")
            for node in ast.walk(tree):
                if not isinstance(node, _ALLOWED_AST_NODES):
                    raise ValueError("disallowed expression")
                if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float)):
                    raise ValueError("disallowed constant")
            total = eval(compile(tree, "<skill_level_expr>", "eval"))
        except (SyntaxError, ValueError, ZeroDivisionError, TypeError):
            return f"【{content}】"

        if isinstance(total, float) and total.is_integer():
            total = int(total)
        return f"【{total}】"

    return _BRACKET_PATTERN.sub(resolve_bracket, text)

class HeroicSkillName(StrEnum):
    deep_pockets = auto()
    monkey_grip = auto()
    chimeric_mastery = auto()
    comet = auto()
    greater_theriomorphosis = auto()
    hope = auto()
    volcano = auto()
    extra_hp = auto()
    extra_mp = auto()
    extra_ip = auto()
    extra_spells = auto()
    upgrade = auto()
    heroic_companion = auto()
    revelation = auto()


class Skill(BaseModel):
    name: str = ""
    current_level: int = 0
    max_level: int = 1
    can_add_spell: bool = False

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"skill_{self.name}"
        return getattr(loc, key, self.name.capitalize())

    def localized_description(self, loc: LocNamespace) -> str:
        key = f"skill_{self.name}_description"
        return getattr(loc, key, f"[Missing description for {self.name}]")

    def resolved_description(self, loc: LocNamespace) -> str:
        token = getattr(loc, "skill_level_short", "")
        return _resolve_skill_level_placeholders(self.localized_description(loc), self.current_level, token)

class HeroicSkill(BaseModel):
    name: str = ""
    required_class: list[ClassName] = list()
    required_skill: Skill | None = None
    can_add_several_times: bool = False

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"skill_{self.name}"
        return getattr(loc, key, self.name.capitalize())

    def localized_description(self, loc: LocNamespace) -> str:
        key = f"skill_{self.name}_description"
        return getattr(loc, key, f"[Missing description for {self.name}]")
