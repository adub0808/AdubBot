from rlbot.agents.base_agent import SimpleControllerState


class Maneuver:
    def __init__(self):
        self.done = False

    def exec(self, bot) -> SimpleControllerState:
        raise NotImplementedError
