# Group 17 - Created 16/03/2026 - Martinelli, Requeut

from enum import Enum

class Action(Enum):
    MOVE_RIGHT = 1
    MOVE_LEFT = 2
    MOVE_TOP = 3
    MOVE_DOWN = 4
    INTERACT = 5

class Color(Enum): # Enum value is used to match zones values
    GREEN = 1
    YELLOW = 2
    RED = 3

MOVE_COORDS = {
    Action.MOVE_RIGHT: (1, 0),
    Action.MOVE_LEFT: (-1,0),
    Action.MOVE_TOP: (0,1),
    Action.MOVE_DOWN: (0,-1)
}

COLOR_MAPPING = {
    Color.GREEN: "#008000",
    Color.YELLOW: "#d7c21d",
    Color.RED: "#cc0000",
}