# Group 17 - Created 16/03/2026 - Martinelli, Requeut

import mesa
from utils import Action, Color, Type

class Radioactivity(mesa.Agent):
    def __init__(self, model, zone):
        """Base class for Radioactivity Agents.

        Args:
            model: A model instance
        """
        super().__init__(model)
        self.zone = zone
        self.radioactivity_level = (self.random.random() + zone - 1)/3

class WasteDisposalZone(mesa.Agent):
    def __init__(self, model, color):
        """Base class for Waste Disposal Zone.

        Args:
            model: A model instance
        """
        super().__init__(model)

class Waste(mesa.Agent):
    def __init__(self, model, color):
        """Base class for Waste Agents.

        Args:
            model: A model instance
        """
        super().__init__(model)
        self.color = color
        self.type = Type.WASTE
