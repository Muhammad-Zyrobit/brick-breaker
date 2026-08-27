from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .entities import Paddle
from .physics import Velocity


class PowerUpKind(Enum):
    WIDE_PADDLE = "wide_paddle"
    SLOW_BALL = "slow_ball"


@dataclass(frozen=True)
class PowerUpSpec:
    kind: PowerUpKind
    duration_frames: int
    drop_chance: float 


WIDE_PADDLE = PowerUpSpec(kind=PowerUpKind.WIDE_PADDLE, duration_frames=600, drop_chance=0.12)
SLOW_BALL = PowerUpSpec(kind=PowerUpKind.SLOW_BALL, duration_frames=420, drop_chance=0.10)

ALL_POWERUPS: tuple[PowerUpSpec, ...] = (WIDE_PADDLE, SLOW_BALL)


def apply_wide_paddle(paddle: Paddle, multiplier: float = 1.6) -> None:
    paddle.set_width(paddle.base_width * multiplier)


def revert_wide_paddle(paddle: Paddle) -> None:
    paddle.set_width(paddle.base_width)


def apply_slow_ball(velocity: Velocity, factor: float = 0.6) -> Velocity:
    return Velocity(velocity.dx * factor, velocity.dy * factor)


def revert_slow_ball(velocity: Velocity, factor: float = 0.6) -> Velocity:
    return Velocity(velocity.dx / factor, velocity.dy / factor)


def roll_for_drop(rng) -> PowerUpSpec | None:
    for spec in ALL_POWERUPS:
        if rng.random() < spec.drop_chance:
            return spec
    return None
