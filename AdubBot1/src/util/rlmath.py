# This module lets RLBot use high-level mathematics to udnerstand its enviroment, including vector operations, interpolation, and angles.

import math


def sign0(x) -> float:
    """
    Returns the sign of x, but returns 0 if x is 0.
    """
    return x and (1, -1)[x < 0]


def sign(x) -> float:
    """
    Returns the sign of x, where 0 is considered positive.
    """
    return (1, -1)[x < 0]


def clip(x, minimum, maximum):
    """
    Clips x to be within the range [minimum, maximum].
    """
    return min(max(minimum, x), maximum)


def clip01(x) -> float:
    """
    Clips x to be within the range [0, 1].
    """
    return clip(x, 0, 1)


def lerp(a, b, t: float):
    """
    Performs linear interpolation between a and b by factor t.
    """
    return (1 - t) * a + t * b


def inv_lerp(a, b, v) -> float:
    return a if b - a == 0 else (v - a) / (b - a)


def remap(prev_low, prev_high, new_low, new_high, v) -> float:
    """
    Remaps a value from one range to another.
    """
    out = inv_lerp(prev_low, prev_high, v)
    out = lerp(new_low, new_high, out)
    return out


def fix_ang(ang: float) -> float:
    return ((ang + math.pi) % math.tau) - math.pi


def is_closer_to_goal_than(a, b, team_index):
    """
    Checks if point 'a' is closer to the goal of the given team than 'b'.
    """
    return (a.y < b.y, a.y > b.y)[team_index]


# Unit tests
if __name__ == "__main__":
    assert clip(12, -2, 2) == 2
    assert clip(-20, -5, 3) == -5