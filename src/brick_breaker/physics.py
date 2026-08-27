from __future__ import annotations

from dataclasses import dataclass

from .geometry import Rect


@dataclass(frozen=True)
class Velocity:
    dx: float
    dy: float


def reflect_off_brick(ball: Rect, velocity: Velocity, brick: Rect) -> Velocity:
    overlap_x, overlap_y = ball.overlap(brick)
    if overlap_x < overlap_y:
        return Velocity(-velocity.dx, velocity.dy)
    return Velocity(velocity.dx, -velocity.dy)


def reflect_off_walls(ball: Rect, velocity: Velocity, window_width: float, window_height: float) -> Velocity:
    dx, dy = velocity.dx, velocity.dy
    if ball.left <= 0 and dx < 0:
        dx = -dx
    elif ball.right >= window_width and dx > 0:
        dx = -dx
    if ball.top <= 0 and dy < 0:
        dy = -dy
    return Velocity(dx, dy)


def is_out_of_bounds(ball: Rect, window_height: float) -> bool:
    return ball.bottom >= window_height


def bounce_off_paddle(ball: Rect, paddle: Rect, base_speed: float, max_horizontal_speed: float) -> Velocity:
    offset = (ball.center_x - paddle.center_x) / (paddle.width / 2)
    offset = max(-1.0, min(1.0, offset))
    dx = offset * max_horizontal_speed
    dy = -abs(base_speed)
    return Velocity(dx, dy)
