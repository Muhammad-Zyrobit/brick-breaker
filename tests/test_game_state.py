from __future__ import annotations

import random

from brick_breaker.game import GameState
from brick_breaker.levels import Level


class _AlwaysDrop(random.Random):
    """Forces every power-up roll to succeed, for deterministic tests."""

    def random(self) -> float:
        return 0.0


class _NeverDrop(random.Random):
    def random(self) -> float:
        return 1.0


def make_state(tmp_path, grid=None, rng=None) -> GameState:
    grid = grid or [[1, 1]]
    level = Level(name="Test Level", grid=tuple(tuple(row) for row in grid))
    return GameState([level], scores_path=tmp_path / "scores.json", rng=rng or _NeverDrop())


class TestGameStateLifecycle:
    def test_starts_in_ready_status(self, tmp_path):
        state = make_state(tmp_path)
        assert state.status == "ready"
        assert state.lives == 3
        assert state.score == 0

    def test_launch_moves_to_playing(self, tmp_path):
        state = make_state(tmp_path)
        state.launch()
        assert state.status == "playing"

    def test_update_does_nothing_before_launch(self, tmp_path):
        state = make_state(tmp_path)
        ball_before = state.ball.rect
        state.update()
        assert state.ball.rect == ball_before

    def test_losing_all_lives_ends_run_as_lost(self, tmp_path):
        state = make_state(tmp_path)
        starting_lives = state.lives
        for _ in range(starting_lives):
            state.launch()
            state.ball.rect = state.ball.rect.moved(0, 10_000)
            state.update()
        assert state.status == "lost"

    def test_destroying_all_bricks_ends_run_as_won(self, tmp_path):
        state = make_state(tmp_path, grid=[[1]])
        state.launch()
        for brick in state.bricks:
            brick.hits_remaining = 0
        state.update()
        assert state.status == "won"

    def test_unbreakable_bricks_do_not_block_a_win(self, tmp_path):
        state = make_state(tmp_path, grid=[[1, -1]])
        state.launch()
        state.bricks[0].hits_remaining = 0  
        state.update()
        assert state.status == "won"

    def test_high_score_persisted_on_win(self, tmp_path):
        from brick_breaker.scores import get_high_score

        state = make_state(tmp_path, grid=[[1]])
        state.launch()
        state.score = 42
        for brick in state.bricks:
            brick.hits_remaining = 0
        state.update()
        assert get_high_score(state.scores_path, "Test Level") == 42


class TestAdvanceLevel:
    def test_advances_to_next_level_when_available(self, tmp_path):
        level1 = Level(name="L1", grid=((1,),))
        level2 = Level(name="L2", grid=((1,),))
        state = GameState([level1, level2], scores_path=tmp_path / "scores.json", rng=_NeverDrop())
        advanced = state.advance_level()
        assert advanced is True
        assert state.level.name == "L2"
        assert state.status == "ready"

    def test_loops_back_to_first_level_after_last(self, tmp_path):
        level1 = Level(name="L1", grid=((1,),))
        state = GameState([level1], scores_path=tmp_path / "scores.json", rng=_NeverDrop())
        advanced = state.advance_level()
        assert advanced is False
        assert state.level_index == 0
        assert state.status == "ready"  


class TestPowerUps:
    def test_powerup_can_be_forced_to_drop(self, tmp_path):
        state = make_state(tmp_path, grid=[[1]], rng=_AlwaysDrop())
        state.launch()
        state.bricks[0].hits_remaining = 1  
        state._maybe_drop_powerup()  
        assert state.active_powerup is not None
        assert state.powerup_timer > 0

    def test_powerup_expires_after_its_duration(self, tmp_path):
        state = make_state(tmp_path, grid=[[1]], rng=_AlwaysDrop())
        state.launch()
        state._maybe_drop_powerup()
        state.powerup_timer = 1
        state.update()
        assert state.active_powerup is None
