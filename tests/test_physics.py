from __future__ import annotations

from brick_breaker.geometry import Rect
from brick_breaker.physics import (
    Velocity,
    bounce_off_paddle,
    is_out_of_bounds,
    reflect_off_brick,
    reflect_off_walls,
)


class TestReflectOffBrick:
    def test_bounces_vertically_on_top_hit(self):
        ball = Rect(x=10, y=18, width=10, height=10)  
        brick = Rect(x=0, y=20, width=30, height=10)  
        velocity = Velocity(dx=3, dy=4)
        result = reflect_off_brick(ball, velocity, brick)
        assert result == Velocity(dx=3, dy=-4)

    def test_bounces_horizontally_on_side_hit(self):
        ball = Rect(x=18, y=10, width=10, height=10) 
        brick = Rect(x=20, y=0, width=10, height=30)  
        velocity = Velocity(dx=4, dy=3)
        result = reflect_off_brick(ball, velocity, brick)
        assert result == Velocity(dx=-4, dy=3)

    def test_is_deterministic_given_same_inputs(self):
        ball = Rect(0, 0, 10, 10)
        brick = Rect(5, 5, 10, 10)
        velocity = Velocity(2, 2)
        assert reflect_off_brick(ball, velocity, brick) == reflect_off_brick(ball, velocity, brick)


class TestReflectOffWalls:
    def test_bounces_off_left_wall(self):
        ball = Rect(x=-1, y=50, width=10, height=10)
        result = reflect_off_walls(ball, Velocity(dx=-3, dy=2), window_width=500, window_height=500)
        assert result == Velocity(dx=3, dy=2)

    def test_bounces_off_right_wall(self):
        ball = Rect(x=495, y=50, width=10, height=10)
        result = reflect_off_walls(ball, Velocity(dx=3, dy=2), window_width=500, window_height=500)
        assert result == Velocity(dx=-3, dy=2)

    def test_bounces_off_top_wall(self):
        ball = Rect(x=100, y=-1, width=10, height=10)
        result = reflect_off_walls(ball, Velocity(dx=3, dy=-2), window_width=500, window_height=500)
        assert result == Velocity(dx=3, dy=2)

    def test_no_bounce_in_open_space(self):
        ball = Rect(x=100, y=100, width=10, height=10)
        velocity = Velocity(dx=3, dy=2)
        assert reflect_off_walls(ball, velocity, window_width=500, window_height=500) == velocity

    def test_does_not_double_bounce_moving_away_from_wall(self):
        ball = Rect(x=0, y=100, width=10, height=10)
        velocity = Velocity(dx=3, dy=2)
        assert reflect_off_walls(ball, velocity, window_width=500, window_height=500) == velocity


class TestOutOfBounds:
    def test_ball_above_bottom_is_in_bounds(self):
        ball = Rect(x=0, y=400, width=10, height=10)
        assert not is_out_of_bounds(ball, window_height=500)

    def test_ball_past_bottom_is_out_of_bounds(self):
        ball = Rect(x=0, y=495, width=10, height=10)
        assert is_out_of_bounds(ball, window_height=500)


class TestBounceOffPaddle:
    def test_center_hit_goes_straight_up(self):
        paddle = Rect(x=200, y=480, width=100, height=15)
        ball = Rect(x=245, y=470, width=10, height=10)  
        result = bounce_off_paddle(ball, paddle, base_speed=4, max_horizontal_speed=6)
        assert result.dx == 0
        assert result.dy == -4

    def test_left_edge_hit_bounces_left(self):
        paddle = Rect(x=200, y=480, width=100, height=15)
        ball = Rect(x=195, y=470, width=10, height=10)  
        result = bounce_off_paddle(ball, paddle, base_speed=4, max_horizontal_speed=6)
        assert result.dx < 0

    def test_right_edge_hit_bounces_right(self):
        paddle = Rect(x=200, y=480, width=100, height=15)
        ball = Rect(x=295, y=470, width=10, height=10)  
        result = bounce_off_paddle(ball, paddle, base_speed=4, max_horizontal_speed=6)
        assert result.dx > 0

    def test_horizontal_speed_never_exceeds_max(self):
        paddle = Rect(x=200, y=480, width=100, height=15)
        ball = Rect(x=1000, y=470, width=10, height=10)  
        result = bounce_off_paddle(ball, paddle, base_speed=4, max_horizontal_speed=6)
        assert abs(result.dx) <= 6
