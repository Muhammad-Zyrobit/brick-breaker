from __future__ import annotations

from brick_breaker.entities import Paddle
from brick_breaker.geometry import Rect
from brick_breaker.physics import Velocity
from brick_breaker.powerups import (
    PowerUpKind,
    apply_slow_ball,
    apply_wide_paddle,
    revert_slow_ball,
    revert_wide_paddle,
    roll_for_drop,
)


class _FixedRng:
    """Deterministic stand-in for `random.Random`, so drop-chance tests
    don't depend on actual randomness."""

    def __init__(self, value: float) -> None:
        self.value = value

    def random(self) -> float:
        return self.value


class TestRollForDrop:
    def test_returns_none_when_roll_is_high(self):
        assert roll_for_drop(_FixedRng(0.99)) is None

    def test_returns_a_powerup_when_roll_is_low(self):
        result = roll_for_drop(_FixedRng(0.0))
        assert result is not None
        assert result.kind == PowerUpKind.WIDE_PADDLE 


class TestWidePaddle:
    def test_apply_widens_paddle(self):
        paddle = Paddle(rect=Rect(200, 480, 100, 15))
        apply_wide_paddle(paddle, multiplier=1.5)
        assert paddle.rect.width == 150

    def test_revert_restores_original_width(self):
        paddle = Paddle(rect=Rect(200, 480, 100, 15))
        apply_wide_paddle(paddle, multiplier=1.5)
        revert_wide_paddle(paddle)
        assert paddle.rect.width == 100


class TestSlowBall:
    def test_apply_reduces_speed(self):
        velocity = Velocity(dx=5, dy=5)
        result = apply_slow_ball(velocity, factor=0.5)
        assert result == Velocity(dx=2.5, dy=2.5)

    def test_revert_is_inverse_of_apply(self):
        original = Velocity(dx=4, dy=-4)
        slowed = apply_slow_ball(original, factor=0.6)
        restored = revert_slow_ball(slowed, factor=0.6)
        assert round(restored.dx, 6) == 4
        assert round(restored.dy, 6) == -4
