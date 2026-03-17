# Group 17 - Created 16/03/2026 - Martinelli, Requeut

###TO DO###
# Ensure no superposition of Robots and no superposition of wastes (both in init and after action)
###########



from mesa.datacollection import DataCollector
from mesa import Model
from mesa.space import MultiGrid
from agents import RobotAgent, GreenRobotAgent, RedRobotAgent, YellowRobotAgent
from objects import Radioactivity, WasteDisposalZone, Waste
from utils import Action, Color, MOVE_COORDS

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

        # Init grid
        self.width_z1 = width_z1
        self.width_z2 = width_z2
        self.width_z3 = width_z3
        self.grid = MultiGrid(width_z1 + width_z2 + width_z3, height, torus=False)

        # Init Radioactivity levels
        for _, pos in self.grid.coord_iter():
            self.grid.place_agent(Radioactivity(self, self.__get_zone(pos)), pos)

        # Init Robots
        agents = [GreenRobotAgent(self) for i in range(number_of_green_robots)] + [YellowRobotAgent(self) for i in range(number_of_yellow_robots)] + [RedRobotAgent(self) for i in range(number_of_red_robots)]
        for agent in agents:
            x = self.random.randrange(width_z1)
            y = self.random.randrange(height)
            self.grid.place_agent(agent, (x, y))

        # Init Wastes
        wastes = [Waste(self, Color.GREEN) for i in range(width_z1 * height) if self.random.random() <= initial_waste_density]
        for waste in wastes: 
            x = self.random.randrange(width_z1)
            y = self.random.randrange(height)
            self.grid.place_agent(waste, (x, y))

        # Init Waste disposal zone
        waste_disposal_zone = WasteDisposalZone(self)
        x = self.width_z1 + self.width_z2 + self.width_z3 - 1 # Waste disposal zone is on the last column of the grid
        y = self.random.randrange(height)
        self.grid.place_agent(waste_disposal_zone, (x, y))

    def __get_zone(self, pos):
        """Private method used to initialize the radioactivity levels of the grid."""
        if pos[0] < self.width_z1:
            return 1
        elif pos[0] < self.width_z1 + self.width_z2:
            return 2
        else:
            return 3

    def step(self):
        self.agents.select(lambda agent: isinstance(agent, RobotAgent)).shuffle_do("step_agent")
    
    def do(self, agent: RobotAgent, action):
        """Check if agent's action is valid and execute it."""
        dx,dy = MOVE_COORDS.get(action, (0,0))
        new_position = agent.pos[0]+dx, agent.pos[1]+dy 

        if new_position in self.grid.get_neighborhood(agent.pos, moore=False, include_center=False):
            zone = self.__get_zone(new_position)
            if agent.can_access_zone(zone):
                self.grid.move_agent(agent, new_position)

    def get_neighbors(self, agent):
        return self.grid.get_neighborhood(agent.pos, moore=False, include_center=False)