from __future__ import annotations

from dataclasses import dataclass, field

from .geometry import Rect
from .physics import Velocity


@dataclass
class Brick:
    rect: Rect
    hits_remaining: int  
    points: int = 10

    @property
    def unbreakable(self) -> bool:
        return self.hits_remaining < 0

    @property
    def destroyed(self) -> bool:
        return self.hits_remaining == 0

    def hit(self) -> int:
        if self.unbreakable or self.destroyed:
            return 0
        self.hits_remaining -= 1
        return self.points if self.hits_remaining == 0 else 0


@dataclass
class Paddle:
    rect: Rect
    speed: float = 8.0
    base_width: float = 0.0  

    def __post_init__(self) -> None:
        if self.base_width == 0.0:
            self.base_width = self.rect.width

    def move(self, dx: float, window_width: float) -> None:
        new_x = max(0.0, min(window_width - self.rect.width, self.rect.x + dx))
        self.rect = Rect(new_x, self.rect.y, self.rect.width, self.rect.height)

    def set_width(self, new_width: float) -> None:
        center = self.rect.center_x
        self.rect = Rect(center - new_width / 2, self.rect.y, new_width, self.rect.height)


@dataclass
class Ball:
    rect: Rect
    velocity: Velocity

    def move(self) -> None:
        self.rect = self.rect.moved(self.velocity.dx, self.velocity.dy)
