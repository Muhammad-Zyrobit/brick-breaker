from __future__ import annotations

from brick_breaker.scores import get_high_score, load_scores, save_high_score


class TestScorePersistence:
    def test_no_file_yields_empty_scores(self, tmp_path):
        assert load_scores(tmp_path / "does_not_exist.json") == {}

    def test_saving_a_score_creates_the_file(self, tmp_path):
        path = tmp_path / "scores.json"
        save_high_score(path, "Level 1", 100)
        assert load_scores(path) == {"Level 1": 100}

    def test_higher_score_overwrites_lower(self, tmp_path):
        path = tmp_path / "scores.json"
        save_high_score(path, "Level 1", 100)
        was_new_high = save_high_score(path, "Level 1", 150)
        assert was_new_high is True
        assert get_high_score(path, "Level 1") == 150

    def test_lower_score_does_not_overwrite(self, tmp_path):
        path = tmp_path / "scores.json"
        save_high_score(path, "Level 1", 150)
        was_new_high = save_high_score(path, "Level 1", 100)
        assert was_new_high is False
        assert get_high_score(path, "Level 1") == 150

    def test_scores_for_different_levels_are_independent(self, tmp_path):
        path = tmp_path / "scores.json"
        save_high_score(path, "Level 1", 50)
        save_high_score(path, "Level 2", 75)
        assert get_high_score(path, "Level 1") == 50
        assert get_high_score(path, "Level 2") == 75

    def test_get_high_score_defaults_to_zero(self, tmp_path):
        path = tmp_path / "scores.json"
        assert get_high_score(path, "Never Played") == 0
