from __future__ import annotations

import json
from pathlib import Path


def load_scores(path: str | Path) -> dict[str, int]:
    path = Path(path)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_high_score(path: str | Path, level_name: str, score: int) -> bool:
    scores = load_scores(path)
    if score > scores.get(level_name, 0):
        scores[level_name] = score
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2)
        return True
    return False


def get_high_score(path: str | Path, level_name: str) -> int:
    return load_scores(path).get(level_name, 0)
