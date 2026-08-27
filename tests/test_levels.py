from __future__ import annotations

import json

import pytest

from brick_breaker.levels import InvalidLevelError, load_level, load_levels, parse_level


class TestParseLevel:
    def test_parses_valid_level(self):
        level = parse_level({"name": "Test", "grid": [[1, 2], [0, -1]]})
        assert level.name == "Test"
        assert level.rows == 2
        assert level.columns == 2

    def test_defaults_name_if_missing(self):
        level = parse_level({"grid": [[1]]})
        assert level.name == "Unnamed Level"

    def test_rejects_missing_grid(self):
        with pytest.raises(InvalidLevelError):
            parse_level({"name": "Broken"})

    def test_rejects_empty_grid(self):
        with pytest.raises(InvalidLevelError):
            parse_level({"grid": []})

    def test_rejects_ragged_rows(self):
        with pytest.raises(InvalidLevelError):
            parse_level({"grid": [[1, 2, 3], [1, 2]]})

    def test_rejects_invalid_brick_value(self):
        with pytest.raises(InvalidLevelError):
            parse_level({"grid": [[1, -2]]})  

    def test_allows_unbreakable_bricks(self):
        level = parse_level({"grid": [[-1, -1]]})
        assert level.grid == ((-1, -1),)


class TestLoadLevel:
    def test_loads_from_file(self, tmp_path):
        path = tmp_path / "level.json"
        path.write_text(json.dumps({"name": "From File", "grid": [[1, 1]]}))
        level = load_level(path)
        assert level.name == "From File"

    def test_bundled_levels_are_all_valid(self):
        from pathlib import Path

        levels_dir = Path(__file__).parent.parent / "levels"
        levels = load_levels(levels_dir)
        assert len(levels) >= 3
        for level in levels:
            assert level.rows > 0
            assert level.columns > 0


class TestLoadLevels:
    def test_loads_all_json_files_sorted(self, tmp_path):
        (tmp_path / "level_02.json").write_text(json.dumps({"name": "Two", "grid": [[1]]}))
        (tmp_path / "level_01.json").write_text(json.dumps({"name": "One", "grid": [[1]]}))
        levels = load_levels(tmp_path)
        assert [lvl.name for lvl in levels] == ["One", "Two"]

    def test_raises_on_empty_directory(self, tmp_path):
        with pytest.raises(InvalidLevelError):
            load_levels(tmp_path)
