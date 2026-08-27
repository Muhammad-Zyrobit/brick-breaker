from __future__ import annotations

import random
from pathlib import Path

import pygame

from .entities import Ball, Brick, Paddle
from .geometry import Rect
from .levels import Level, load_levels
from .physics import Velocity, bounce_off_paddle, is_out_of_bounds, reflect_off_brick, reflect_off_walls
from .powerups import (
    PowerUpKind,
    apply_slow_ball,
    apply_wide_paddle,
    revert_slow_ball,
    revert_wide_paddle,
    roll_for_drop,
)
from .scores import get_high_score, save_high_score

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
BRICK_AREA_HEIGHT = 300
PADDLE_HEIGHT = 15
PADDLE_WIDTH = 100
BALL_RADIUS = 8
FRAME_RATE = 60
LIVES_PER_LEVEL = 3

COLOR_BG = (15, 15, 20)
COLOR_PADDLE = (70, 130, 230)
COLOR_BALL = (230, 230, 230)
COLOR_TEXT = (255, 255, 255)
BRICK_COLORS = {1: (0, 200, 80), 2: (240, 240, 240), 3: (240, 130, 20), -1: (90, 90, 90)}

LEVELS_DIR = Path(__file__).parent.parent.parent / "levels"
SCORES_PATH = Path.home() / ".brick_breaker" / "scores.json"


def _bricks_from_level(level: Level) -> list[Brick]:
    brick_width = WINDOW_WIDTH / level.columns
    brick_height = BRICK_AREA_HEIGHT / level.rows
    bricks = []
    for row_idx, row in enumerate(level.grid):
        for col_idx, value in enumerate(row):
            if value == 0:
                continue
            rect = Rect(col_idx * brick_width, row_idx * brick_height, brick_width, brick_height)
            bricks.append(Brick(rect=rect, hits_remaining=value))
    return bricks


def _new_ball(paddle: Paddle) -> Ball:
    rect = Rect(paddle.rect.center_x - BALL_RADIUS, paddle.rect.top - BALL_RADIUS * 2, BALL_RADIUS * 2, BALL_RADIUS * 2)
    return Ball(rect=rect, velocity=Velocity(dx=3, dy=-4))


def _new_paddle() -> Paddle:
    rect = Rect((WINDOW_WIDTH - PADDLE_WIDTH) / 2, WINDOW_HEIGHT - PADDLE_HEIGHT * 3, PADDLE_WIDTH, PADDLE_HEIGHT)
    return Paddle(rect=rect)


def _rect_to_pygame(rect: Rect) -> pygame.Rect:
    return pygame.Rect(int(rect.x), int(rect.y), int(rect.width), int(rect.height))


class GameState:
    def __init__(self, levels: list[Level], scores_path: Path | None = None, rng: random.Random | None = None) -> None:
        self.levels = levels
        self.level_index = 0
        self.rng = rng or random.Random()
        self.scores_path = scores_path or SCORES_PATH
        self.reset_level()

    @property
    def level(self) -> Level:
        return self.levels[self.level_index]

    def reset_level(self) -> None:
        self.bricks = _bricks_from_level(self.level)
        self.paddle = _new_paddle()
        self.ball = _new_ball(self.paddle)
        self.lives = LIVES_PER_LEVEL
        self.score = 0
        self.ball_launched = False
        self.active_powerup: PowerUpKind | None = None
        self.powerup_timer = 0
        self.status = "ready"  

    def advance_level(self) -> bool:
        if self.level_index + 1 >= len(self.levels):
            self.level_index = 0
            self.reset_level()
            return False
        self.level_index += 1
        self.reset_level()
        return True

    def update(self) -> None:
        if self.status != "playing":
            return

        self.ball.move()
        self.ball.velocity = reflect_off_walls(self.ball.rect, self.ball.velocity, WINDOW_WIDTH, WINDOW_HEIGHT)

        if self.ball.rect.collides(self.paddle.rect) and self.ball.velocity.dy > 0:
            self.ball.velocity = bounce_off_paddle(self.ball.rect, self.paddle.rect, base_speed=4, max_horizontal_speed=6)

        for brick in self.bricks:
            if brick.destroyed or not self.ball.rect.collides(brick.rect):
                continue
            self.ball.velocity = reflect_off_brick(self.ball.rect, self.ball.velocity, brick.rect)
            points = brick.hit()
            self.score += points
            if points > 0:
                self._maybe_drop_powerup()
            break 

        if is_out_of_bounds(self.ball.rect, WINDOW_HEIGHT):
            self.lives -= 1
            if self.lives <= 0:
                self.status = "lost"
                save_high_score(self.scores_path, self.level.name, self.score)
            else:
                self.ball = _new_ball(self.paddle)
                self.ball_launched = False
                self.status = "ready"

        if all(b.destroyed or b.unbreakable for b in self.bricks):
            self.status = "won"
            save_high_score(self.scores_path, self.level.name, self.score)

        if self.active_powerup is not None:
            self.powerup_timer -= 1
            if self.powerup_timer <= 0:
                self._clear_powerup()

    def _maybe_drop_powerup(self) -> None:
        spec = roll_for_drop(self.rng)
        if spec is None:
            return
        if self.active_powerup is not None:
            self._clear_powerup()
        self.active_powerup = spec.kind
        self.powerup_timer = spec.duration_frames
        if spec.kind == PowerUpKind.WIDE_PADDLE:
            apply_wide_paddle(self.paddle)
        elif spec.kind == PowerUpKind.SLOW_BALL:
            self.ball.velocity = apply_slow_ball(self.ball.velocity)

    def _clear_powerup(self) -> None:
        if self.active_powerup == PowerUpKind.WIDE_PADDLE:
            revert_wide_paddle(self.paddle)
        elif self.active_powerup == PowerUpKind.SLOW_BALL:
            self.ball.velocity = revert_slow_ball(self.ball.velocity)
        self.active_powerup = None
        self.powerup_timer = 0

    def launch(self) -> None:
        if self.status == "ready":
            self.status = "playing"
            self.ball_launched = True
        elif self.status in ("won", "lost"):
            self.reset_level()


def _draw(window: pygame.Surface, font: pygame.font.Font, state: GameState) -> None:
    window.fill(COLOR_BG)

    for brick in state.bricks:
        if brick.destroyed:
            continue
        color = BRICK_COLORS.get(brick.hits_remaining, (255, 255, 255))
        pygame.draw.rect(window, color, _rect_to_pygame(brick.rect))
        pygame.draw.rect(window, (0, 0, 0), _rect_to_pygame(brick.rect), 1)

    pygame.draw.rect(window, COLOR_PADDLE, _rect_to_pygame(state.paddle.rect))
    pygame.draw.circle(
        window, COLOR_BALL,
        (int(state.ball.rect.x + BALL_RADIUS), int(state.ball.rect.y + BALL_RADIUS)),
        BALL_RADIUS,
    )

    high_score = get_high_score(SCORES_PATH, state.level.name)
    hud_lines = [
        f"{state.level.name}   Score: {state.score}   Best: {max(high_score, state.score)}   Lives: {state.lives}",
    ]
    if state.active_powerup is not None:
        hud_lines.append(f"Power-up: {state.active_powerup.value}")
    for i, line in enumerate(hud_lines):
        window.blit(font.render(line, True, COLOR_TEXT), (10, 10 + i * 24))

    if state.status == "ready":
        _center_text(window, font, "CLICK OR PRESS SPACE TO LAUNCH")
    elif state.status == "won":
        is_last_level = state.level_index + 1 >= len(state.levels)
        msg = "YOU WIN! CLICK TO PLAY AGAIN" if is_last_level else "LEVEL COMPLETE! CLICK TO CONTINUE"
        _center_text(window, font, msg)
    elif state.status == "lost":
        _center_text(window, font, "GAME OVER - CLICK TO RETRY")

    pygame.display.update()


def _center_text(window: pygame.Surface, font: pygame.font.Font, text: str) -> None:
    surface = font.render(text, True, COLOR_TEXT)
    rect = surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60))
    window.blit(surface, rect)


def main() -> None:
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Brick Breaker")
    font = pygame.font.SysFont("Arial", 20)
    clock = pygame.time.Clock()

    levels = load_levels(LEVELS_DIR)
    state = GameState(levels)

    running = True
    while running:
        clock.tick(FRAME_RATE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                if state.status == "won":
                    state.advance_level()  
                else:
                    state.launch()

        keys = pygame.key.get_pressed()
        dx = 0.0
        if keys[pygame.K_LEFT]:
            dx -= state.paddle.speed
        if keys[pygame.K_RIGHT]:
            dx += state.paddle.speed
        state.paddle.move(dx, WINDOW_WIDTH)
        if state.status == "ready":
            state.ball = _new_ball(state.paddle)

        state.update()
        _draw(window, font, state)

    pygame.quit()


if __name__ == "__main__":
    main()
