# his module provides utility functions for controlling car movement, focusing on steering and input.

import math

from rlbot.utils.structures.game_data_struct import PlayerInfo

from util.orientation import Orientation, relative_location
from util.vec import Vec3


def limit_to_safe_range(value: float) -> float:
    """
    Ensures that input values for controls are within the acceptable range of -1 to 1 for turning.
    
    """
    
    if value < -1:
        return -1
    if value > 1:
        return 1
    return value


def steer_toward_target(car: PlayerInfo, target: Vec3) -> float:
    """
    Calculates steering input to direct the car towards a target point.
    
    """
    # Determine the relative position of the target from the car's perspective
    relative = relative_location(Vec3(car.physics.location), Orientation(car.physics.rotation), target)
    # Calculate the angle between the car's forward direction and the target
    angle = math.atan2(relative.y, relative.x)
    # Convert angle to steering input, ensuring it's within safe bounds
    return limit_to_safe_range(angle * 5)