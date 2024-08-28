import math
from typing import NewType

degrees = NewType('degrees', float)
Vec2f = tuple[float, float]
Vec2i = tuple[int, int]


def get_pos_on_circle(pos: Vec2f, radius: float, angle: degrees) -> Vec2f:
    x = radius * math.sin(math.radians(angle))
    y = radius * math.cos(math.radians(angle))
    return pos[0] + x, pos[1] - y


def vec_to_int(pos: Vec2f) -> Vec2i:
    return int(pos[0]), int(pos[1])
