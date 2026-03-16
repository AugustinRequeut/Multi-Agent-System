# Group 17 - Created 16/03/2026 - Martinelli, Requeut

from enum import Enum

class Action(Enum):
    MOVE_RIGHT = 1
    MOVE_LEFT = 2
    MOVE_TOP = 3
    MOVE_DOWN = 4
    INTERACT = 5

class Color(Enum):
    GREEN = 1
    YELLOW = 2
    RED = 3

class Type(Enum):
    ROBOT = 1
    WASTE = 2