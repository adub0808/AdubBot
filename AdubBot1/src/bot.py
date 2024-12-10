# Import necessary modules for RLBot framework, custom controllers, behaviors, and utilities

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.messages.flat.QuickChatSelection import QuickChatSelection
from rlbot.utils.structures.game_data_struct import GameTickPacket

from controllers import other
from behaviors.carry import Carry
from behaviors.clear_ball import ClearBall
from behaviors.save_goal import SaveGoal
from behaviors.shoot_at_goal import ShootAtGoal
from controllers.fly import FlyController
from maneuvers.kickoff import choose_kickoff_maneuver
from util.info import GameInfo
from controllers.drive import DriveController
from controllers.shooting import ShotController
from controllers.aim_cone import AimCone
from util.rendering import draw_ball_path
from behaviors.utsystem import utilSystem, Choice
from util.vec import xy, Vec3, norm, dot

RENDER = True  # enable or disable rendering

class MyBot(BaseAgent):
    
    def __init__(self, name, team, index):
        super().__init__(name, team, index)  # Initialize base agent
        self.do_rendering = RENDER  # Set rendering based on RENDER flag
        self.info = None  # GameInfo object for storing game data
        self.choice = None  # Current behavioral choice
        self.maneuver = None  # Current maneuver object
        self.doing_kickoff = False  # Flag for kickoff state
        self.ut = None  # Utility system for decision making
        self.drive = DriveController()  # Controller for driving maneuvers
        self.shoot = ShotController()  # Controller for shooting
        self.fly = FlyController()  # Controller for aerial maneuvers

    def initialize_agent(self):
        # Setup game info and utility system at the start of the game
        self.info = GameInfo(self.index, self.team)
        self.ut = utilSystem([DefaultBehaviour(), ShootAtGoal(), ClearBall(self), SaveGoal(self), Carry()])

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # Process game tick packet to update game info
        if not self.info.field_info_loaded:
            self.info.read_field_info(self.get_field_info())
            if not self.info.field_info_loaded:
                return SimpleControllerState()  # Return empty controls if field info isn't loaded
        self.info.read_packet(packet)

        # End game celebration
        if packet.game_info.is_match_ended:
            return other.celebrate(self)  # Celebrate if the match has ended

        # Start rendering context
        self.renderer.begin_rendering()

        # Use bot's decision logic
        controller = self.use_brain()

        # Render game state if enabled
        if self.do_rendering:
            draw_ball_path(self, 4, 5)  # Draw predicted ball path
            doing = self.maneuver or self.choice
            if doing is not None:
                status_str = f'{self.name}: {doing.__class__.__name__}'
                # Commented out rendering - possibly for debugging or performance
                # self.renderer.draw_string_2d(300, 700 + self.index * 20, 1, 1, status_str, self.renderer.team_color(alt_color=True))

        # End rendering context
        self.renderer.end_rendering()

        # Feedback for next tick
        self.feedback(controller)

        return controller  # Return the controller state for car movement

    def print(self, s):
        # Custom print function to log with team color
        team_name = "[BLUE]" if self.team == 0 else "[ORANGE]"
        print("Beast", self.index, team_name, ":", s)

    def feedback(self, controller):
        # Update last inputs if a controller is provided
        if controller is None:
            self.print(f"None controller from state: {self.choice.__class__} & {self.maneuver.__class__}")
        else:
            self.info.my_car.last_input.roll = controller.roll
            self.info.my_car.last_input.pitch = controller.pitch
            self.info.my_car.last_input.yaw = controller.yaw
            self.info.my_car.last_input.boost = controller.boost

    def use_brain(self) -> SimpleControllerState:
        # Decision making logic for kickoff and regular gameplay
        if self.info.is_kickoff and not self.doing_kickoff:
            self.maneuver = choose_kickoff_maneuver(self)
            self.doing_kickoff = True
            self.print("Kickoff - Hello world!")

        # If no maneuver or current maneuver is done, decide next action
        if self.maneuver is None or self.maneuver.done:
            self.maneuver = None
            self.doing_kickoff = False
            self.choice = self.ut.evaluate(self)  # Use utility system to pick behavior
            ctrl = self.choice.exec(self)  # Execute chosen behavior
            # If a maneuver was started by the choice, execute it instead
            if self.maneuver is not None:
                self.ut.reset()
                self.choice = None
                return self.maneuver.exec(self)
            return ctrl

        return self.maneuver.exec(self)  # Continue executing current maneuver

class DefaultBehaviour(Choice):
    def __init__(self):
        pass

    def util(self, bot):
        # Default utility score, low priority behavior
        return 0.1

    def exec(self, bot):
        # Basic behavior logic for positioning and chasing
        car = bot.info.my_car
        ball = bot.info.ball
        car_to_ball = ball.pos - car.pos
        ball_to_enemy_goal = bot.info.enemy_goal - ball.pos
        own_goal_to_ball = ball.pos - bot.info.own_goal
        dist = norm(car_to_ball)

        offence = ball.pos.y * bot.info.team_sign < 0
        dot_enemy = dot(car_to_ball, ball_to_enemy_goal)
        dot_own = dot(car_to_ball, own_goal_to_ball)
        right_side_of_ball = dot_enemy > 0 if offence else dot_own > 0

        if right_side_of_ball:
            # Aim towards enemy goal
            dir_to_post_1 = (bot.info.enemy_goal + Vec3(3800, 0, 0)) - bot.info.ball.pos
            dir_to_post_2 = (bot.info.enemy_goal + Vec3(-3800, 0, 0)) - bot.info.ball.pos
            cone = AimCone(dir_to_post_1, dir_to_post_2)
            cone.get_goto_point(bot, car.pos, bot.info.ball.pos)
            if bot.do_rendering:
                cone.draw(bot, bot.info.ball.pos)

            # Drive towards ball
            return bot.drive.go_towards_point(bot, xy(ball.pos), 2000, True, True, can_dodge=dist > 2200)
        else:
            # Return to own goal
            return bot.drive.go_towards_point(bot, bot.info.own_goal_field, 2000, True, True)