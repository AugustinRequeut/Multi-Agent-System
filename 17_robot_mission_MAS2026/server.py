# Group 17 - Created 16/03/2026 - Martinelli, Requeut

from mesa.visualization import SolaraViz, make_space_component
from model import RobotMission
from utils import AgentColor


def agent_portrayal(agent):
    size = 10
    color = "black"
    if agent.color == AgentColor.GREEN:
        color = "green"
    elif agent.color == AgentColor.YELLOW:
        color = "yellow"
    elif agent.color == AgentColor.RED:
        color = "red"

    return {"size": size, "color": color}

model_params = {
}

# Create initial model instance
model = RobotMission()

SpaceGraph = make_space_component(agent_portrayal)

#Create the Dashboard
page = SolaraViz(
    model,
    components=[SpaceGraph],
    model_params=model_params,
    name="Robot Mission",
)
# This is required to render the visualization in the Jupyter notebook
page
# to start : "solara run server.py"