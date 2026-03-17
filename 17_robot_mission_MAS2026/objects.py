# Group 17 - Created 16/03/2026 - Martinelli, Requeut

import mesa
from utils import COLOR_MAPPING

class Radioactivity(mesa.Agent):
    def __init__(self, model, zone):
        """Base class for Radioactivity Agents. This represent the radioactivity level of the location of this agent.

        Args:
            model: A model instance
            zone: 1, 2 or 3. Used to define radioactivity level.
        """
        super().__init__(model)
        self.__zone = zone
        self.__radioactivity_level = (self.random.random() + zone - 1)/3

    def get_radioactivity_level(self):
        return self.__radioactivity_level
    
    def get_display_dict(self):
        if self.__zone == 1:
            color = "#00800033"
        elif self.__zone == 2:
            color = "#b59f0033"
        elif self.__zone == 3:
            color = "#cc000033"
        else:
            color = "white"

        return {
            "size": 80,
            "color": color,
            "marker": "s",
        }

class WasteDisposalZone(mesa.Agent):
    def __init__(self, model):
        """Base class for Waste Disposal Zone.

        Args:
            model: A model instance
        """
        super().__init__(model)
        self.__disposed_count = 0

    def get_display_dict(self):
        return {
            "size": 80,
            "color": "black",
            "marker": "s",
        }
    
    def add_waste(self):
        self.__disposed_count += 1

    def get_disposed_count(self):
        return self.__disposed_count

class Waste(mesa.Agent):
    def __init__(self, model, color):
        """Base class for Waste Agents.

        Args:
            model: A model instance
        """
        super().__init__(model)
        self.color = color

    def get_display_dict(self):
        return {
            "size": 20,
            "color": COLOR_MAPPING.get(self.color, "black"),
            "marker": "*",
        }