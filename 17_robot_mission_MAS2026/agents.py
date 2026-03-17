# Group 17 - Created 16/03/2026 - Martinelli, Requeut

import mesa
from utils import Action, Color, COLOR_MAPPING
from abc import abstractmethod

class RobotAgent(mesa.Agent):
    def __init__(self, model, color, max_waste):
        """Base class for Robot Agents.

        Args:
            model: A model instance
        """
        super().__init__(model)
        self.__knowledge = None
        self.__max_waste = max_waste
        self.__content = {
            color: 0 for color in Color
        }
        self.color = color

    def step_agent(self):
        percepts = self.model.get_percepts(self)
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
    
    def can_pick(self, waste_color):
        return (self.color.value == waste_color.value) and (sum(self.__content.values()) < self.__max_waste)
    
    def pick(self, waste_color):
        if not self.can_pick(waste_color):
            raise ValueError("Agent can't pick more waste.")
        self.__content[waste_color] += 1
    
    def transform(self):
        if self.__content[self.color] == self.__max_waste:
            next_value = self.color.value + 1
            if any(next_value == c.value for c in Color):
                self.__content[self.color] -= self.__max_waste
                self.__content[Color(next_value)] += 1

    def deposit(self):
        # Try first to deposit transformed waste if exists
        next_value = self.color.value + 1
        if any(next_value == c.value for c in Color):
            next_color = Color(next_value)
            if self.__content[next_color] > 0:
                self.__content[next_color] -= 1
                return next_color
        
        # Try to deposit based waste (not transformed)
        if self.__content[self.color] > 0:
            self.__content[self.color] -= 1
            return self.color
            
        return None
    
    def get_waste_count(self, color: Color) -> int:
        return self.__content[color]
    
class GreenRobotAgent(RobotAgent):
    def __init__(self, model):
        super().__init__(model, Color.GREEN, 2)

class YellowRobotAgent(RobotAgent):
    def __init__(self, model):
        super().__init__(model, Color.YELLOW, 2)

class RedRobotAgent(RobotAgent):
    def __init__(self, model):
        super().__init__(model, Color.RED, 1)
    