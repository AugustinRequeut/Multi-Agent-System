# Group 17 - Created 16/03/2026 - Martinelli, Requeut

import mesa
from utils import Action, Color, COLOR_MAPPING
from abc import abstractmethod

class RobotAgent(mesa.Agent):
    def __init__(self, model):
        """Base class for Robot Agents.

        Args:
            model: A model instance
        """
        super().__init__(model)
        self.__knowledge = None
        self.color = None

    def step_agent(self):
        percepts = self.model.get_neighbors(self)
        self.__update(percepts)
        action = self.__deliberate()
        self.model.do(self, action)
    
    def __update(self, percepts):
        pass
    
    @abstractmethod
    def __deliberate(self):
        # Random action for basic implementation
        action = self.model.random.choice(list(Action))
        return action
    
    def get_display_dict(self):
        return {
            "size": 50,
            "color": COLOR_MAPPING.get(self.color, "black"),
            "marker": "o",
        }
    
    def can_access_zone(self, zone_number):
        return self.color.value >= zone_number
    
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
    