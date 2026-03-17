# Group 17 - Created 16/03/2026 - Martinelli, Requeut

from mesa.visualization import SolaraViz, make_space_component
from model import RobotMission

def agent_portrayal(agent):
    return agent.get_display_dict()

model_params = {
    "number_of_green_robots": {
        "type": "SliderInt",
        "value": 5,
        "label": "Number of Green Robots:",
        "min": 1,
        "max": 20,
        "step": 1,
    },
    "number_of_yellow_robots": {
        "type": "SliderInt",
        "value": 5,
        "label": "Number of Yellow Robots:",
        "min": 1,
        "max": 20,
        "step": 1,
    },
    "number_of_red_robots": {
        "type": "SliderInt",
        "value": 5,
        "label": "Number of Red Robots:",
        "min": 1,
        "max": 20,
        "step": 1,
    },
    "initial_waste_density": {
        "type": "SliderFloat",
        "value": 0.1,
        "label": "Density of waste:",
        "min": 0.01,
        "max": 0.5,
        "step": 0.01,
    },
}

# Create initial model instance
model = RobotMission(number_of_green_robots=10, number_of_yellow_robots=10, number_of_red_robots=10, initial_waste_density=0.1)

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