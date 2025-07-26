from pydantic import BaseModel


class Skill(BaseModel):
    name: str = ""
    description: str = ""
    current_level: int = 0
    max_level: int = 10
    can_add_spell: bool = False
