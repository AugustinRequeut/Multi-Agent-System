from mesa.datacollection import DataCollector
from mesa import Model
from mesa.space import MultiGrid
from agents import RobotAgent
from utils import Action 

class RobotMission(Model):
    """A model with some number of agents."""
    def __init__(self, number_of_green_robots=10, number_of_yellow_robots=10, number_of_red_robots=10, width_z1=10, width_z2=10, width_z3=10, height=30, seed=None):
        """Initialize the model.

        Args:
            number_of_green_robots (int, optional): Number of green robots. Defaults to 10.
            number_of_yellow_robots (int, optional): Number of yellown robots. Defaults to 10.
            number_of_red_robots (int, optional): Number of red robots. Defaults to 10.
            width_z1 (int, optional): z1 grid width. Defaults to 10.
            width_z2 (int, optional): z2 grid width. Defaults to 10.
            width_z3 (int, optional): z3 grid width. Defaults to 10.
            height (int, optional): Grid height. Defaults to 30.
            seed (int, optional): Random seed. Defaults to None.
        """

        super().__init__(seed=seed)
        self.grid = MultiGrid(width_z1 + width_z2 + width_z3, height, torus=True)
        agents = [RobotAgent(self) for i in range(number_of_green_robots)]
        for agent in agents:
            x = self.random.random(width_z1)
            y = self.random.random(height)
            self.grid.place_agent(agent, (x, y))


    def step(self):
        self.agents.shuffle_do("step_agent")
    
    def do(self, agent, action):

        if action == Action.MOVE_RIGHT:
            new_position = agent.pos[0] + 1, agent.pos[1]
        if action == Action.MOVE_LEFT:
            new_position = agent.pos[0] - 1, agent.pos[1]
        if action == Action.MOVE_TOP:
            new_position = agent.pos[0], agent.pos[1] + 1
        if action == Action.MOVE_DOWN:
            new_position = agent.pos[0], agent.pos[1] - 1

        if new_position in self.grid.get_neighborhood(agent.pos, moore=False, include_center=False):
            self.grid.move_agent(agent, new_position)

        return self.grid.get_neighborhood(agent.pos, moore=False, include_center=False)

    def percept(self, agent):
        return self.grid.get_neighborhood(agent.pos, moore=False, include_center=False)
        