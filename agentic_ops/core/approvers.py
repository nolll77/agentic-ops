from pathlib import Path
from typing import Literal
import yaml
from pydantic import BaseModel, ConfigDict, ValidationError

class _S(BaseModel): model_config = ConfigDict(extra="forbid", frozen=True)

class LevelRule(_S):
    eligible: list[str]
    required_groups: list[str] = []

class Approvers(_S):
    schema_version: Literal[1]
    groups: dict[str, list[str]]
    levels: dict[Literal["L2", "L3"], LevelRule]

    @classmethod
    def load(cls, path: Path) -> "Approvers":
        try:
            a = cls.model_validate(yaml.safe_load(path.read_text()))
        except (OSError, yaml.YAMLError, ValidationError) as e:
            raise RuntimeError(f"approvers.yaml invalide, démarrage refusé: {e}") from e
        unknown = {g for l in a.levels.values() for g in (*l.eligible, *l.required_groups)} - set(a.groups)
        if unknown or not any(a.groups.values()):
            raise RuntimeError(f"approvers.yaml incohérent: groupes inconnus {unknown} ou aucun approbateur")
        return a

    def group_of(self, user_id: str, level: str) -> str | None:
        for g in self.levels[level].eligible:
            if user_id in self.groups.get(g, []):
                return g
        return None
