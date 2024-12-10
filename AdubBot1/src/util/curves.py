# This module provides functions for creating and manipulating curves, specifically for path planning in a 3D space like Rocket League's field.

from typing import List

from util.rlmath import clip
from util.vec import normalize, Vec3


def curve_from_arrival_dir(src, target, arrival_direction, w=1):
    """
    Calculates a point on a curve where the car arrives in a specific direction.
    - src: Starting position (Vec3)
    - target: Target position (Vec3)
    - arrival_direction: The direction the path should head towards after the target (Vec3)
    - w: Weight of the curve, defaults to 1 for equal distance calculation
    - Returns: A Vec3 representing a point on the curve
    
    """
    dir = normalize(arrival_direction)  # Normalize the direction vector (set a starting place)
    tx, ty = target.x, target.y
    sx, sy = src.x, src.y
    dx, dy = dir.x, dir.y

    # Solve for t where the point is equidistant from src and target along the arrival direction to figure out where car needs to move to
    t = - (tx * tx - 2 * tx * sx + ty * ty - 2 * ty * sy + sx * sx + sy * sy) / (2 * (tx * dx + ty * dy - sx * dx - sy * dy))
    t = clip(t, -1700, 1700)  # Clip 't' to avoid extreme values

    return target + w * t * dir  # Return the point on the curve


def bezier(t: float, points: List[Vec3]) -> Vec3:
    """
    Computes a point on a Bezier curve for a given parameter t.
    - t: The parameter t where 0 <= t <= 1, representing the position on the curve
    - points: List of control points defining the Bezier curve
    - Returns: A Vec3 representing a point on the Bezier curve
    
    """
    n = len(points)
    if n == 1:
        return points[0]  # If only one point, return it
    else:
        # Recursive calculation of Bezier curve point, gotten from online stackoverflow posts
        return (1 - t) * bezier(t, points[0:-1]) + t * bezier(t, points[1:n])