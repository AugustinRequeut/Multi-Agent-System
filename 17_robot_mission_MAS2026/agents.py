# Group 17 - Created 16/03/2026 - Martinelli, Requeut

import mesa
from utils import Action, Color, Type

class RobotAgent(mesa.Agent):
    def __init__(self, model):
        """Base class for Robot Agents.

        Args:
            model: A model instance
        """
        super().__init__(model)
        self.knowledge = None
        self.color = None
        self.type = Type.ROBOT

    def step_agent(self):
        percepts = self.model.get_neighbors(self)
        self.update(percepts)
        action = self.deliberate()
        self.model.do(self, action)
    
    def update(self, percepts):
        pass

    def deliberate(self):
        # Random action for basic implementation
        action = self.model.random.choice(list(Action))
        return action
    
class GreenRobotAgent(RobotAgent):
    def __init__(self, model):
        super().__init__(model)
        self.color = Color.GREEN

class YellowRobotAgent(RobotAgent):
    def __init__(self, model):
        super().__init__(model)
        self.color = Color.YELLOW

class RedRobotAgent(RobotAgent):
    def __init__(self, model):
        super().__init__(model)
        self.color = Color.RED
    