# This module contains utility functions for analyzing future ball positions particularly focused on predicting if and when the ball will enter a goal.

from typing import Callable

from rlbot.utils.structures.ball_prediction_struct import BallPrediction, Slice

# Define the threshold for considering a ball inside the goal; slightly more than field length + ball radius
GOAL_THRESHOLD = 5235

# Number of frames to jump when searching for the ball in the goal, balancing efficiency and accuracy
GOAL_SEARCH_INCREMENT = 20


def find_slice_at_time(ball_prediction: BallPrediction, game_time: float):
    """
    Finds the ball's position at a specific future time from the ball prediction data.
    - ball_prediction: BallPrediction object with future ball positions.
    - game_time: The time in the future to check.
    - Returns: A Slice object representing the ball's state at the closest predicted time, or None if out of bounds.
    """
    start_time = ball_prediction.slices[0].game_seconds
    approx_index = int((game_time - start_time) * 60)  # 60 slices per second
    if 0 <= approx_index < ball_prediction.num_slices:
        return ball_prediction.slices[approx_index]
    return None


def predict_future_goal(ball_prediction: BallPrediction):
    """
    Predicts if the ball will go into a goal based on its predicted path.
    - ball_prediction: BallPrediction object.
    - Returns: The first Slice where the ball is in the goal, or None if it doesn't enter.
    """
    return find_matching_slice(ball_prediction, 0, lambda s: abs(s.physics.location.y) >= GOAL_THRESHOLD,
                               search_increment=20)


def find_matching_slice(ball_prediction: BallPrediction, start_index: int, predicate: Callable[[Slice], bool],
                        search_increment=1):
    """
    Searches through the ball prediction to find the first slice where a condition is met.
    - ball_prediction: BallPrediction object.
    - start_index: Where to start the search.
    - predicate: A function that checks if a slice meets some condition.
    - search_increment: How many slices to jump when searching for efficiency, then backtrack for accuracy.
    - Returns: The first Slice matching the predicate, or None if no match is found.
    """
    for coarse_index in range(start_index, ball_prediction.num_slices, search_increment):
        if predicate(ball_prediction.slices[coarse_index]):
            # Backtrack to find the exact first slice that matches
            for j in range(max(start_index, coarse_index - search_increment), coarse_index):
                ball_slice = ball_prediction.slices[j]
                if predicate(ball_slice):
                    return ball_slice
    return None