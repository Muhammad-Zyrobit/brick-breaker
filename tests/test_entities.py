from __future__ import annotations

from brick_breaker.entities import Ball, Brick, Paddle
from brick_breaker.geometry import Rect
from brick_breaker.physics import Velocity


class TestBrick:
    def test_hit_reduces_hits_remaining(self):
        brick = Brick(rect=Rect(0, 0, 10, 10), hits_remaining=2)
        brick.hit()
        assert brick.hits_remaining == 1
        assert not brick.destroyed

    def test_hit_returns_points_only_when_destroyed(self):
        brick = Brick(rect=Rect(0, 0, 10, 10), hits_remaining=2, points=10)
        assert brick.hit() == 0  
        assert brick.hit() == 10  

    def test_unbreakable_brick_never_destroyed(self):
        brick = Brick(rect=Rect(0, 0, 10, 10), hits_remaining=-1)
        for _ in range(10):
            assert brick.hit() == 0
        assert brick.unbreakable
        assert not brick.destroyed

    def test_hitting_destroyed_brick_is_a_noop(self):
        brick = Brick(rect=Rect(0, 0, 10, 10), hits_remaining=1, points=10)
        assert brick.hit() == 10
        assert brick.hit() == 0  


class TestPaddle:
    def test_move_clamps_to_left_edge(self):
        paddle = Paddle(rect=Rect(5, 480, 100, 15))
        paddle.move(dx=-50, window_width=500)
        assert paddle.rect.x == 0

    def test_move_clamps_to_right_edge(self):
        paddle = Paddle(rect=Rect(450, 480, 100, 15))
        paddle.move(dx=50, window_width=500)
        assert paddle.rect.x == 400  

    def test_set_width_keeps_paddle_centered(self):
        paddle = Paddle(rect=Rect(200, 480, 100, 15))
        original_center = paddle.rect.center_x
        paddle.set_width(200)
        assert paddle.rect.width == 200
        assert paddle.rect.center_x == original_center

    def test_base_width_recorded_on_creation(self):
        paddle = Paddle(rect=Rect(200, 480, 100, 15))
        assert paddle.base_width == 100
        paddle.set_width(200)
        assert paddle.base_width == 100  


class TestBall:
    def test_move_applies_velocity(self):
        ball = Ball(rect=Rect(10, 10, 8, 8), velocity=Velocity(dx=3, dy=-2))
        ball.move()
        assert ball.rect.x == 13
        assert ball.rect.y == 8
