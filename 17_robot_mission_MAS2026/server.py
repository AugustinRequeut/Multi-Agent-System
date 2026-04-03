# Group 17 - Created 16/03/2026 - Martinelli, Requeut

from mesa.visualization import SolaraViz, make_space_component, make_plot_component
from model import RobotMission
from utils import COLOR_MAPPING, Color

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
    "alpha": {
        "type": "SliderFloat",
        "value": 0.2,
        "label": "alpha:",
        "min": 0.0,
        "max": 1.0,
        "step": 0.01,
    },
    "k": {
        "type": "SliderFloat",
        "value": 1.0,
        "label": "k:",
        "min": 0.0,
        "max": 10.0,
        "step": 0.5,
    },
}

# Create initial model instance
model = RobotMission(number_of_green_robots=10, number_of_yellow_robots=10, number_of_red_robots=10, initial_waste_density=0.1)

SpaceGraph = make_space_component(agent_portrayal)
WastePlot = make_plot_component(
    {
        "Green Waste": COLOR_MAPPING[Color.GREEN],
        "Yellow Waste": COLOR_MAPPING[Color.YELLOW],
        "Red Waste": COLOR_MAPPING[Color.RED],
        "Disposed": "black"
    }
)

#Create the Dashboard
page = SolaraViz(
    model,
    components=[SpaceGraph, WastePlot],
    model_params=model_params,
    name="Robot Mission",
)
# This is required to render the visualization in the Jupyter notebook
page
# to start : "solara run server.py"