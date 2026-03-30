# Group 17 - Created 16/03/2026 - Martinelli, Requeut

from enum import Enum

class Action(Enum):
    MOVE_RIGHT = 1
    MOVE_LEFT = 2
    MOVE_TOP = 3
    MOVE_DOWN = 4
    NOOP = 5
    INTERACT = 6
    COMMUNICATE = 7

class RobotState(Enum):
    NORMAL = 1
    
    # State of initiator
    SEEKING_PARTNER = 2
    WAITING_PROPOSALS = 3
    SELECTING_PARTNER = 4
    DROPPING_WASTE = 5
    WAITING_FOR_ARRIVAL = 6
    STEPPING_ASIDE = 7
    
    # State of colaborator
    EVALUATING_CFP = 8
    WAITING_ACCEPTANCE = 9
    TRAVELING_TO_RDV = 10
    COLLECTING_WASTE = 11

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

ISOLATION_LIMIT = 40 # Time until which the robot starts looking for a partner to exchange
ANSWER_LIMIT = 10 # Time until which the robot stops waiting for a response
WAITING_FOR_ARRIVAL_LIMIT = 40 # Time until which the robot stops waiting for a its partner arrival