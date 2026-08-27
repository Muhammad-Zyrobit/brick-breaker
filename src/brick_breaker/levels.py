from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Level:
    name: str
    grid: tuple[tuple[int, ...], ...] 

    @property
    def rows(self) -> int:
        return len(self.grid)

    @property
    def columns(self) -> int:
        return len(self.grid[0]) if self.grid else 0


class InvalidLevelError(ValueError):
    pass


def parse_level(data: dict) -> Level:
    if "grid" not in data or not isinstance(data["grid"], list) or not data["grid"]:
        raise InvalidLevelError("level file must have a non-empty 'grid' field")

    grid = data["grid"]
    row_length = len(grid[0])
    for row in grid:
        if len(row) != row_length:
            raise InvalidLevelError("all rows in 'grid' must have the same length")
        for value in row:
            if not isinstance(value, int) or value < -1:
                raise InvalidLevelError(f"invalid brick value {value!r}: must be an integer >= -1")

    return Level(name=data.get("name", "Unnamed Level"), grid=tuple(tuple(row) for row in grid))


def load_level(path: str | Path) -> Level:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return parse_level(data)


def load_levels(directory: str | Path) -> list[Level]:
    directory = Path(directory)
    paths = sorted(directory.glob("*.json"))
    if not paths:
        raise InvalidLevelError(f"no level files found in {directory}")
    return [load_level(p) for p in paths]
