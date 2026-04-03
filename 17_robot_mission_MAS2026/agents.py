# Group 17 - Created 16/03/2026 - Martinelli, Requeut

import mesa
from utils import Action, Color, COLOR_MAPPING, MOVE_COORDS, RobotState, ISOLATION_LIMIT, ANSWER_LIMIT, WAITING_FOR_ARRIVAL_LIMIT, WAITING_ACCEPTANCE_LIMIT, WAITING_COLLECT_LIMIT
from abc import abstractmethod
from objects import Waste, Radioactivity, WasteDisposalZone
from math import ceil, exp

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative

class RobotAgent(CommunicatingAgent):
    def __init__(self, model, color, max_waste):
        """Base class for Robot Agents.

        Args:
            model: A model instance
        """
        model.agent_counter += 1
        agent_name = f"{color.name}_{model.agent_counter}"
        super().__init__(model, name=agent_name)
        self._knowledge = None
        self._inertia = [0,0]
        self._last_pos = None
        self._max_waste = max_waste
        self._content = {
            color: 0 for color in Color
        }
        self.color = color

        # Communication
        self.state = RobotState.NORMAL
        self.isolation_counter = 0 # Time with 1 waste without partner
        self.timeout_counter = 0 # Counter to avoid deadlock
        self.partner_id = None
        self.rendezvous_pos = None

    def step_agent(self):
        percepts = self.model.get_percepts(self)
        self._update(percepts)
        action = self._deliberate()
        self.model.do(self, action)
    
    def _update(self, percepts):
        self._knowledge = percepts

        if self._last_pos is not None and self._last_pos!=self.pos:
            dx = self.pos[0] - self._last_pos[0]
            dy = self.pos[1] - self._last_pos[1]

            self._inertia[0] = self.model.alpha * self._inertia[0] + (1 - self.model.alpha) * dx
            self._inertia[1] = self.model.alpha * self._inertia[1] + (1 - self.model.alpha) * dy
        
        self._last_pos = self.pos
    
    def _choose_random_move(self, moves):

        weights = []

        for move in moves:
            dx, dy = MOVE_COORDS[move]
            weight = exp(self.model.k * (self._inertia[0]*dx + self._inertia[1]*dy))
            weights.append(weight) 

        return self.model.random.choices(moves, weights=weights, k=1)[0]

    def _deliberate(self):
        if self.state == RobotState.NORMAL:
            if self.color == Color.GREEN or self.color == Color.YELLOW: # Only green and yellow robots will try to exchange wastes
                self._update_state()
        
            # Check if he can accept a potential trade
            if self._content[self.color] == 1 and not self.is_carrying_payload():
                new_msgs = self.get_new_messages()
                cfps = [m for m in new_msgs if m.get_performative() == MessagePerformative.CFP]
                if cfps:
                    msg = cfps[0]
                    self.partner_id = msg.get_exp()
                    self.state = RobotState.EVALUATING_CFP
                    return Action.COMMUNICATE
                
            return self._behavior_normal()
        
        elif self.state in [RobotState.SEEKING_PARTNER, RobotState.WAITING_PROPOSALS, RobotState.SELECTING_PARTNER, RobotState.DROPPING_WASTE, RobotState.WAITING_FOR_ARRIVAL, RobotState.STEPPING_ASIDE, RobotState.WAIT_FOR_COLLECT]:
            return self._behavior_initiator()
            
        elif self.state in [RobotState.EVALUATING_CFP, RobotState.WAITING_ACCEPTANCE, RobotState.TRAVELING_TO_RDV, RobotState.COLLECTING_WASTE]:
            return self._behavior_participant()

    def _behavior_normal(self):
        # Case 1: The robot carries an object ready to be deposited
        if self.is_carrying_payload():
            dx, dy = MOVE_COORDS[Action.MOVE_RIGHT]
            right_pos = (self.pos[0] + dx, self.pos[1] + dy)
            at_border = right_pos not in self._knowledge or not self.can_access_pos(right_pos)
            
            if at_border:
                # If the case is free, deposit
                if not self.get_objects_in_pos(self.pos, Waste):
                    return Action.INTERACT
                # Try to go to a free cell else
                else:
                    moves = self.get_available_moves([Action.MOVE_TOP, Action.MOVE_DOWN])
                    return self._choose_random_move(moves)

            # Move to the border of the accessible zone
            moves = self.get_available_moves([Action.MOVE_RIGHT])
            if moves != [Action.NOOP]:
                return self._choose_random_move(moves)
            else:
                # Blocked by another robot
                bypass = self.get_available_moves([Action.MOVE_TOP, Action.MOVE_DOWN, Action.MOVE_LEFT])
                return self._choose_random_move(bypass)
                
        # Case 2 : The robot is looking for a waste
        else:
            target_pos = self.find_target_waste()
            
            if target_pos == self.pos:
                return Action.INTERACT
            elif target_pos is not None:
                return self.move_towards(target_pos)
            else:
                all_moves = self.get_available_moves([Action.MOVE_RIGHT, Action.MOVE_LEFT, Action.MOVE_TOP, Action.MOVE_DOWN])
                return self._choose_random_move(all_moves)

    def _behavior_initiator(self):
        # print(f"{self.get_name()}: {self.state}")
        if self.state == RobotState.SEEKING_PARTNER:
            for agent in self.model.agents:
                if isinstance(agent, RobotAgent) and agent.color == self.color and agent != self:
                    msg = Message(self.get_name(), agent.get_name(), MessagePerformative.CFP, "Need partner")
                    self.send_message(msg)
            
            self.state = RobotState.WAITING_PROPOSALS
            self.timeout_counter = 0
            return Action.COMMUNICATE
        
        elif self.state == RobotState.WAITING_PROPOSALS:
            self.timeout_counter += 1
            if self.timeout_counter > ANSWER_LIMIT:
                self.state = RobotState.NORMAL
                return Action.NOOP
            
            new_msgs = self.get_new_messages()
            proposals = [m for m in new_msgs if m.get_performative() == MessagePerformative.PROPOSE]
            
            if proposals:
                msg = proposals[0]
                self.partner_id = msg.get_exp()
                self.state = RobotState.SELECTING_PARTNER
                return Action.COMMUNICATE
            
            # Go to the right for an possible exchange get further to facilitate exchange
            moves = self.get_available_moves([Action.MOVE_RIGHT])
            if moves != [Action.NOOP]:
                return self._choose_random_move(moves)
            else:
                # Blocked by another robot
                bypass = self.get_available_moves([Action.MOVE_TOP, Action.MOVE_DOWN, Action.MOVE_LEFT])
                return self._choose_random_move(bypass)
        
        elif self.state == RobotState.SELECTING_PARTNER:
            # TO DO : Improve rendez-vous point logic (e.g. farther than zone limit to avoid being blocked)
            self.rendezvous_pos = self.pos
            
            msg = Message(self.get_name(), self.partner_id, MessagePerformative.ACCEPT_PROPOSAL, self.rendezvous_pos)
            self.send_message(msg)

            self.state = RobotState.DROPPING_WASTE
            return Action.COMMUNICATE
            
        elif self.state == RobotState.DROPPING_WASTE:
            self.state = RobotState.WAITING_FOR_ARRIVAL
            self.timeout_counter = 0
            return Action.INTERACT
        
        elif self.state == RobotState.WAITING_FOR_ARRIVAL:
            self.timeout_counter += 1
            
            # If the partner did not come, we pick up back the waste
            if self.timeout_counter > WAITING_FOR_ARRIVAL_LIMIT:
                self.state = RobotState.NORMAL
                self.partner_id = None
                return Action.INTERACT
            new_msgs = self.get_new_messages()
            arrivals = [m for m in new_msgs if m.get_performative() == MessagePerformative.INFORM]
            for msg in arrivals:
                if msg.get_exp() == self.partner_id and msg.get_content() == "Arrived":
                    self.state = RobotState.STEPPING_ASIDE
                    return Action.COMMUNICATE
            return Action.NOOP
        
        elif self.state == RobotState.STEPPING_ASIDE:
            # If we haved moved, we freed the place as intended
            if self.pos != self.rendezvous_pos:
                self.state = RobotState.WAIT_FOR_COLLECT
                self.partner_id = None
                self.rendezvous_pos = None
                self.timeout_counter = 0
                return Action.NOOP
            
            moves = self.get_available_moves([Action.MOVE_RIGHT, Action.MOVE_LEFT, Action.MOVE_TOP, Action.MOVE_DOWN])
            if moves:
                return self._choose_random_move(moves)
        
        # Let time for the other robot to collect
        elif self.state == RobotState.WAIT_FOR_COLLECT:
            self.timeout_counter += 1
            if self.timeout_counter > 2:
                self.state = RobotState.NORMAL
            return Action.NOOP

    def _behavior_participant(self):
        # print(f"{self.get_name()}: {self.state}")
        if self.state == RobotState.EVALUATING_CFP:
            msg = Message(self.get_name(), self.partner_id, MessagePerformative.PROPOSE, "Available")
            self.send_message(msg)
            self.state = RobotState.WAITING_ACCEPTANCE
            self.timeout_counter = 0
            return Action.COMMUNICATE

        elif self.state == RobotState.WAITING_ACCEPTANCE:
            self.timeout_counter += 1
            if self.timeout_counter > WAITING_ACCEPTANCE_LIMIT:
                self.state = RobotState.NORMAL
                self.partner_id = None
                return Action.NOOP

            new_msgs = self.get_new_messages()
            acceptances = [m for m in new_msgs if m.get_performative() == MessagePerformative.ACCEPT_PROPOSAL]

            for msg in acceptances:
                if msg.get_exp() == self.partner_id:
                    self.rendezvous_pos = msg.get_content()
                    self.state = RobotState.TRAVELING_TO_RDV
                    self.timeout_counter = 0
                    return Action.COMMUNICATE
            
            return self._behavior_normal()

        elif self.state == RobotState.TRAVELING_TO_RDV:
            self.timeout_counter += 1
            if self.timeout_counter > WAITING_FOR_ARRIVAL_LIMIT:
                self.state = RobotState.NORMAL
                self.partner_id = None
                self.rendezvous_pos = None
                return Action.NOOP

            dx = abs(self.pos[0] - self.rendezvous_pos[0])
            dy = abs(self.pos[1] - self.rendezvous_pos[1])
            
            if dx + dy == 1: 
                msg = Message(self.get_name(), self.partner_id, MessagePerformative.INFORM, "Arrived")
                self.send_message(msg)
                self.state = RobotState.COLLECTING_WASTE
                self.timeout_counter = 0
                return Action.COMMUNICATE
            else:
                return self.move_towards(self.rendezvous_pos)

        elif self.state == RobotState.COLLECTING_WASTE:
            self.timeout_counter += 1
            if self.timeout_counter > WAITING_COLLECT_LIMIT:
                self.state = RobotState.NORMAL
                self.partner_id = None
                self.rendezvous_pos = None
                return Action.NOOP


            if self.pos == self.rendezvous_pos:
                self.state = RobotState.NORMAL
                self.partner_id = None
                self.rendezvous_pos = None
                print("Exchange was successfull")
                return Action.INTERACT

            if self.rendezvous_pos[0] > self.pos[0]:
                return Action.MOVE_RIGHT
            elif self.rendezvous_pos[0] < self.pos[0]:
                return Action.MOVE_LEFT
            elif self.rendezvous_pos[1] > self.pos[1]:
                return Action.MOVE_TOP
            elif self.rendezvous_pos[1] < self.pos[1]:
                return Action.MOVE_DOWN

            raise ValueError("Robot moved further from rendez-vous point in COLLECTING WASTE state.")

    def get_display_dict(self):
        if self.state != RobotState.NORMAL:
            return {
            "size": 50, 
            "color": COLOR_MAPPING.get(self.color, "black"),
            "marker": "<",
        }
        return {
            "size": 50,
            "color": COLOR_MAPPING.get(self.color, "black"),
            "marker": "o",
        }
    
    def can_access_zone(self, zone_number):
        return self.color.value >= zone_number
    
    def can_access_pos(self, pos):
        """Whether the robot has the authorization to access the given pos."""
        return self.can_access_zone(self.get_zone(pos))
    
    def can_pick(self, waste_color):
        """Whether the robot as the capacity and the right to pick a waste."""
        return (self.color.value == waste_color.value) and (sum(self._content.values()) < self._max_waste)
    
    def get_zone(self, pos):
        """Returns zone number based on radioactivity level."""
        radioactivity = next((content for content in self._knowledge[pos] if isinstance(content, Radioactivity)), None)
        try:
            return ceil(radioactivity.get_radioactivity_level() * 3)
        except:
            raise ValueError(f"No radioactivity object in cell {pos}")
    
    def pick(self, waste_color):
        """Pickup a waste and add to the robot's inventory."""
        if not self.can_pick(waste_color):
            raise ValueError("Agent can't pick more waste.")
        self._content[waste_color] += 1
    
    def transform(self):
        """Transform carried wastes into higher level waste if possible."""
        if self._content[self.color] == self._max_waste:
            next_value = self.color.value + 1
            if any(next_value == c.value for c in Color):
                self._content[self.color] -= self._max_waste
                self._content[Color(next_value)] += 1

    def deposit(self):
        """Remove a waste from the robot's inventory and returns the color of this waste."""
        # Try first to deposit transformed waste if exists
        next_value = self.color.value + 1
        if any(next_value == c.value for c in Color):
            next_color = Color(next_value)
            if self._content[next_color] > 0:
                self._content[next_color] -= 1
                return next_color
        
        # Try to deposit based waste (not transformed)
        if self._content[self.color] > 0:
            self._content[self.color] -= 1
            return self.color
            
        return None
    
    def get_waste_count(self, color: Color) -> int:
        """Returns the amount of waste of given color in the robot's inventory."""
        return self._content[color]
    
    def is_carrying_payload(self):
        """Check if robot carries a waste ready to be deposited (transformed or red)"""
        next_value = self.color.value + 1
        if any(next_value == c.value for c in Color):
            return self._content[Color(next_value)] > 0
        return self._content[self.color] > 0

    def get_objects_in_pos(self, pos, obj_type):
        """Extract objects of given type from given position."""
        if pos not in self._knowledge:
            return []
        return [obj for obj in self._knowledge[pos] if isinstance(obj, obj_type)]

    def get_available_moves(self, move_list):
        """Returns a list of valid moves among a given list of moves."""
        available_actions = []
        for action in move_list:
            dx, dy = MOVE_COORDS[action]
            new_pos = self.pos[0] + dx, self.pos[1] + dy
            
            if new_pos in self._knowledge:
                if self.can_access_pos(new_pos) and not self.get_objects_in_pos(new_pos, RobotAgent):
                    available_actions.append(action)
        if available_actions:
            return available_actions
        else:
            return [Action.NOOP]
    
    def find_target_waste(self):
        """Looks for a pickable waste in neighborhood."""
        # Waste below
        if any(w.color == self.color for w in self.get_objects_in_pos(self.pos, Waste)):
            return self.pos

        # Von Neumann neighborhood
        von_neumann = [
            (self.pos[0], self.pos[1]+1), (self.pos[0], self.pos[1]-1),
            (self.pos[0]-1, self.pos[1]), (self.pos[0]+1, self.pos[1])
        ]
        for pos in von_neumann:
            if any(w.color == self.color for w in self.get_objects_in_pos(pos, Waste)):
                return pos

        # Moore neighborood
        moore = [
            (self.pos[0]-1, self.pos[1]+1), (self.pos[0]+1, self.pos[1]+1),
            (self.pos[0]-1, self.pos[1]-1), (self.pos[0]+1, self.pos[1]-1)
        ]
        for pos in moore:
            if any(w.color == self.color for w in self.get_objects_in_pos(pos, Waste)):
                return pos

        return None

    def move_towards(self, target_pos):
        """Converts a target position into an action."""
        dx, dy = target_pos[0] - self.pos[0], target_pos[1] - self.pos[1]
        
        preferred = []
        if dx > 0: preferred.append(Action.MOVE_RIGHT)
        elif dx < 0: preferred.append(Action.MOVE_LEFT)
        if dy > 0: preferred.append(Action.MOVE_TOP)
        elif dy < 0: preferred.append(Action.MOVE_DOWN)
        
        # Try direct move
        available = self.get_available_moves(preferred)
        if available:
            return self._choose_random_move(available)
            
        # If path is blocked, random moove
        fallback = self.get_available_moves([Action.MOVE_RIGHT, Action.MOVE_LEFT, Action.MOVE_TOP, Action.MOVE_DOWN])
        return self._choose_random_move(fallback)
    
    def move_to_left_border_zone(self):
        """Computes an action to approach the left border of the zone corresponding to the agent's color"""
        # Case 1: The agent is in the zone corresponding to its color
        if self.get_zone(self.pos) == self.color.value:
            dx, dy = MOVE_COORDS[Action.MOVE_LEFT]
            left_pos = (self.pos[0] + dx, self.pos[1] + dy)
            
            if left_pos not in self._knowledge:
                moves = self.get_available_moves([Action.MOVE_TOP, Action.MOVE_DOWN, Action.MOVE_RIGHT])
                return self._choose_random_move(moves)
            
            # Moves up or down if the border is reached
            at_border = self.get_zone(left_pos) < self.color.value
            if at_border:
                moves = self.get_available_moves([Action.MOVE_TOP, Action.MOVE_DOWN])
                return self._choose_random_move(moves)
            
            # Tries to move left otherwise
            moves = self.get_available_moves([Action.MOVE_LEFT])
            if moves != [Action.NOOP]:
                return self._choose_random_move(moves)
            
            else:
                # Blocked by another robot
                bypass = self.get_available_moves([Action.MOVE_TOP, Action.MOVE_DOWN, Action.MOVE_RIGHT])
                return self._choose_random_move(bypass)
            
        # Case 2: The agent is in a zone at the left of its corresponding zone
        else:

            # Moves right if it can            
            moves = self.get_available_moves([Action.MOVE_RIGHT])
            if moves != [Action.NOOP]:
                return self._choose_random_move(moves)
            
            else:
                # Blocked by another robot
                bypass = self.get_available_moves([Action.MOVE_TOP, Action.MOVE_DOWN, Action.MOVE_LEFT])
                return self._choose_random_move(bypass)
            
    def _update_state(self):
        if self._content[self.color] == 1 and not self.is_carrying_payload():
            self.isolation_counter += 1
            if self.isolation_counter > ISOLATION_LIMIT:
                self.state = RobotState.SEEKING_PARTNER
                self.isolation_counter = 0
                return Action.COMMUNICATE
        else:
            self.isolation_counter = 0

    
class GreenRobotAgent(RobotAgent):
    def __init__(self, model):
        super().__init__(model, Color.GREEN, 2)

class YellowRobotAgent(RobotAgent):
    def __init__(self, model):
        super().__init__(model, Color.YELLOW, 2)

    def _behavior_normal(self):
        # Case 1: The robot carries an object ready to be deposited
        if self.is_carrying_payload():
            dx, dy = MOVE_COORDS[Action.MOVE_RIGHT]
            right_pos = (self.pos[0] + dx, self.pos[1] + dy)
            at_border = right_pos not in self._knowledge or not self.can_access_pos(right_pos)
            
            if at_border:
                # If the case is free, deposit
                if not self.get_objects_in_pos(self.pos, Waste):
                    return Action.INTERACT
                # Try to go to a free cell else
                else:
                    moves = self.get_available_moves([Action.MOVE_TOP, Action.MOVE_DOWN])
                    return self._choose_random_move(moves)

            # Move to the border of the accessible zone
            moves = self.get_available_moves([Action.MOVE_RIGHT])
            if moves != [Action.NOOP]:
                return self._choose_random_move(moves)
            else:
                # Blocked by another robot
                bypass = self.get_available_moves([Action.MOVE_TOP, Action.MOVE_DOWN, Action.MOVE_LEFT])
                return self._choose_random_move(bypass)
                
        # Case 2 : The robot is looking for a waste
        else:
            target_pos = self.find_target_waste()
            
            if target_pos == self.pos:
                return Action.INTERACT
            elif target_pos is not None:
                return self.move_towards(target_pos)
            else:
                return self.move_to_left_border_zone()

class RedRobotAgent(RobotAgent):
    def __init__(self, model):
        super().__init__(model, Color.RED, 1)
    
    def _behavior_normal(self):
        # Case 1: The robot carries an red waste ready to be deposited
        if self.is_carrying_payload():
            if self.get_objects_in_pos(self.pos, WasteDisposalZone):
                return Action.INTERACT
                
            # Look for the disposal zone
            for pos, contents in self._knowledge.items():
                if any(isinstance(obj, WasteDisposalZone) for obj in contents):
                    return self.move_towards(pos)

            dx, dy = MOVE_COORDS[Action.MOVE_RIGHT]
            right_pos = (self.pos[0] + dx, self.pos[1] + dy)
            
            # The robot is at the border
            if right_pos not in self._knowledge: 
                moves = self.get_available_moves([Action.MOVE_TOP, Action.MOVE_DOWN])
                if moves != [Action.NOOP]:
                    return self._choose_random_move(moves)
                else:
                    # Blocked by another robot
                    bypass = self.get_available_moves([Action.MOVE_LEFT])
                    return self._choose_random_move(bypass)

            # Move to the right border
            moves = self.get_available_moves([Action.MOVE_RIGHT])
            if moves != [Action.NOOP]:
                return self._choose_random_move(moves)
            else:
                # Blocked by another robot
                bypass = self.get_available_moves([Action.MOVE_TOP, Action.MOVE_DOWN, Action.MOVE_LEFT])
                return self._choose_random_move(bypass)
                
        # Case 2 : The robot is looking for a red waste
        else:
            target_pos = self.find_target_waste()
            
            if target_pos == self.pos:
                return Action.INTERACT
            elif target_pos is not None:
                return self.move_towards(target_pos)
            else:
                return self.move_to_left_border_zone()
    