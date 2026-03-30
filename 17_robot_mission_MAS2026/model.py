# Group 17 - Created 16/03/2026 - Martinelli, Requeut

from mesa.datacollection import DataCollector
from mesa import Model
from mesa.space import MultiGrid
from agents import RobotAgent, GreenRobotAgent, RedRobotAgent, YellowRobotAgent
from objects import Radioactivity, WasteDisposalZone, Waste
from utils import Action, Color, MOVE_COORDS
from communication.message.MessageService import MessageService

def compute_waste_by_color(model, color):
        total_waste = 0
        for agent in model.agents:
            # Wastes on the grid
            if isinstance(agent, Waste) and agent.color == color:
                total_waste += 1
                
            # Wastes in the robots inventory
            elif isinstance(agent, RobotAgent):
                total_waste += agent.get_waste_count(color)
        
        return total_waste

def compute_disposed_waste(model):
    for agent in model.agents:
        if isinstance(agent, WasteDisposalZone):
            return agent.get_disposed_count()
    return 0

class RobotMission(Model):
    """A model with some number of agents."""
    def __init__(self, number_of_green_robots=1, number_of_yellow_robots=1, number_of_red_robots=1, initial_waste_density=0.1, width_z1=10, width_z2=10, width_z3=10, height=30, seed=None):
        """Initialize the model.

        Args:
            number_of_green_robots (int, optional): Number of green robots. Defaults to 10.
            number_of_yellow_robots (int, optional): Number of yellow robots. Defaults to 10.
            number_of_red_robots (int, optional): Number of red robots. Defaults to 10.
            initial_waste_density (float, optional): Probability that a zone 1 cell contains a waste at the beginning. Defaults to 0.4
            width_z1 (int, optional): z1 grid width. Defaults to 10.
            width_z2 (int, optional): z2 grid width. Defaults to 10.
            width_z3 (int, optional): z3 grid width. Defaults to 10.
            height (int, optional): Grid height. Defaults to 30.
            seed (int, optional): Random seed. Defaults to None.
        """

        super().__init__(seed=seed)

        # Reset message service
        if hasattr(MessageService, "_MessageService__instance"):
            MessageService._MessageService__instance = None
        elif hasattr(MessageService, "_instance"):
            MessageService._instance = None
        elif hasattr(MessageService, "__instance"):
            MessageService.__instance = None

        self._message_service = MessageService(self, instant_delivery=False)

        self.datacollector = DataCollector(
            model_reporters={
                "Green Waste": lambda m: compute_waste_by_color(m, Color.GREEN),
                "Yellow Waste": lambda m: compute_waste_by_color(m, Color.YELLOW),
                "Red Waste": lambda m: compute_waste_by_color(m, Color.RED),
                "Disposed": compute_disposed_waste
            },
        )

        # Init grid
        self.width_z1 = width_z1
        self.width_z2 = width_z2
        self.width_z3 = width_z3
        self.grid = MultiGrid(width_z1 + width_z2 + width_z3, height, torus=False)

        z1_coords = [pos for _, pos in self.grid.coord_iter() if self._get_zone(pos) == 1]

        # Init Radioactivity levels
        for _, pos in self.grid.coord_iter():
            self.grid.place_agent(Radioactivity(self, self._get_zone(pos)), pos)

        # Init Robots
        self.agent_counter = 0
        agents = [GreenRobotAgent(self) for _ in range(number_of_green_robots)] + [YellowRobotAgent(self) for _ in range(number_of_yellow_robots)] + [RedRobotAgent(self) for _ in range(number_of_red_robots)]
        robot_positions = self.random.sample(z1_coords, len(agents))
        for agent, pos in zip(agents, robot_positions):
            self.grid.place_agent(agent, pos)

        # Init Wastes
        for pos in z1_coords:
            if self.random.random() <= initial_waste_density:
                waste = Waste(self, Color.GREEN)
                self.grid.place_agent(waste, pos)

        # Init Waste disposal zone
        waste_disposal_zone = WasteDisposalZone(self)
        x = self.width_z1 + self.width_z2 + self.width_z3 - 1 # Waste disposal zone is on the last column of the grid
        y = self.random.randrange(height)
        self.grid.place_agent(waste_disposal_zone, (x, y))

    def _get_zone(self, pos):
        """Private method used to initialize the radioactivity levels of the grid."""
        if pos[0] < self.width_z1:
            return 1
        elif pos[0] < self.width_z1 + self.width_z2:
            return 2
        else:
            return 3

    def step(self):
        self._message_service.dispatch_messages()
        self.agents.select(lambda agent: isinstance(agent, RobotAgent)).shuffle_do("step_agent")
        self.datacollector.collect(self)
    
    def do(self, agent: RobotAgent, action):
        """Check if agent's action is valid and execute it."""
        if action == Action.NOOP:
            pass
        if action in MOVE_COORDS:
            self._handle_move(agent, action)

        elif action == Action.INTERACT:
            self._handle_interaction(agent)

        elif action == Action.COMMUNICATE:
            pass
    
    def _handle_move(self, agent: RobotAgent, action):
        """Handle agent movement and ensure the move is valid."""
        dx, dy = MOVE_COORDS[action]
        new_position = (agent.pos[0] + dx, agent.pos[1] + dy)
        # Check if position is valid
        if new_position in self.grid.get_neighborhood(agent.pos, moore=False, include_center=False):
            zone = self._get_zone(new_position)
            if agent.can_access_zone(zone):
                # Check if cell has no robot in it
                cell_contents = self.grid.get_cell_list_contents([new_position])
                is_occupied_by_robot = any(isinstance(obj, RobotAgent) for obj in cell_contents)
                if not is_occupied_by_robot:
                    self.grid.move_agent(agent, new_position)

    def _handle_interaction(self, agent: RobotAgent):
        """Handle waste collection, transformation and deposit."""
        cell_contents = self.grid.get_cell_list_contents([agent.pos])
        wastes = [obj for obj in cell_contents if isinstance(obj, Waste)]
        if len(wastes) > 1:
            raise ValueError("More than 1 waste in the same cell.")
        elif len(wastes) == 1:
            waste = wastes[0]
            if agent.can_pick(waste.color):
                agent.pick(waste.color)

                self.grid.remove_agent(waste)
                waste.remove()

                agent.transform()
        else:
            waste_color = agent.deposit()
            disposal_zone = next((obj for obj in cell_contents if isinstance(obj, WasteDisposalZone)), None)
            
            if waste_color:
                if disposal_zone:
                    disposal_zone.add_waste()
                else:
                    new_waste = Waste(self, waste_color)
                    self.grid.place_agent(new_waste, agent.pos)

    def get_percepts(self, agent: RobotAgent):
        """Returns a dict corresponding to the agent's perception."""
        percepts = {}

        neighborhood = self.grid.get_neighborhood(
            agent.pos, 
            moore=True,
            include_center=True
        )

        for pos in neighborhood:
            contents = self.grid.get_cell_list_contents([pos])
            percepts[pos] = contents

        return percepts