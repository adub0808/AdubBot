# This module contains functions to visualize ball paths, circles, and curves in 3D space

import math
from typing import List

from util.curves import bezier
from util.vec import Vec3, cross, normalize, axis_to_rotation, dot


def draw_ball_path(bot, duration: float, step_size: int):
    """
    Renders the predicted path of the ball over a given duration.
    - bot: The bot object with rendering capabilities.
    - duration: Duration in seconds to predict and draw.
    - step_size: Number of prediction steps to skip between points.
    
    """
    
    ball_prediction = bot.get_ball_prediction_struct()
    if ball_prediction is not None and duration > 0 and step_size > 0:
        time_passed = 0
        steps_taken = 0
        locations = [ball_prediction.slices[0].physics.location]
        while time_passed < duration and steps_taken + step_size < ball_prediction.num_slices:
            steps_taken += step_size
            time_passed += step_size * 0.016666  # Assuming 60 slices per second
            locations.append(ball_prediction.slices[steps_taken].physics.location)

        if steps_taken > 0:
            bot.renderer.begin_rendering()  # Begin the rendering
            color = bot.renderer.create_color(255, 255, 0, 0)  # Red color for the path
            for i in range(len(locations) - 1):
                bot.renderer.draw_line_3d(locations[i], locations[i+1], color)
            bot.renderer.end_rendering()  # End the rendering


def draw_circle(bot, center: Vec3, normal: Vec3, radius: float, pieces: int):
    """
    Draws a circle in 3D space.
    - bot: The bot object with rendering capabilities.
    - center: Center point of the circle.
    - normal: Vector perpendicular to the circle's plane.
    - radius: Radius of the circle.
    - pieces: Number of segments to approximate the circle.
    
    """
    
    # Create initial vector for circle points
    arm = normalize(cross(normal, center)) * radius
    angle = 2 * math.pi / pieces
    rotation_mat = axis_to_rotation(angle * normalize(normal))
    points = [center + arm]

    for i in range(pieces):
        arm = dot(rotation_mat, arm)  # Rotate the arm vector
        points.append(center + arm)

    bot.renderer.begin_rendering()  # Begin the rendering
    color = bot.renderer.orange()  # Orange color for the circle
    # Draw lines between points to form a circle
    for i in range(len(points)):
        bot.renderer.draw_line_3d(points[i], points[(i + 1) % len(points)], color)
    bot.renderer.end_rendering()  # End the rendering


def draw_bezier(bot, points: List[Vec3], time_step: float=0.05):
    """
    Draws a curve in 3D space.
    - bot: The bot object with rendering capabilities.
    - points: Control points for the Bezier curve.
    - time_step: Step size for drawing the curve, smaller for smoother curves.
    
    """
    
    time = 0
    last_point = points[0]
    bot.renderer.begin_rendering()  # Begin the rendering
    while time < 1:
        time += time_step
        current_point = bezier(time, points)
        # Draw segment of curve with a light pink color
        bot.renderer.draw_line_3d(last_point, current_point, bot.renderer.create_color(255, 180, 255, 210))
        last_point = current_point
    bot.renderer.end_rendering()  # End the rendering