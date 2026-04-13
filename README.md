# Multi-Agent-System

## Installation and Execution

**1. Clone the repository**

```bash
git clone https://github.com/AugustinRequeut/Multi-Agent-System.git
cd Multi-agent-System
```

**2. Create a virtual environment**

```bash
python -m venv venv
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the server**

```bash
cd 17_robot_mission_MAS2026
solara run server.py
```

## Technical Choices and Progress

**Current Status**

- **Completed**: 
  - Environment setup and reactive agents implementation.
  - Addition of inter-agent communication.

**Technical Choices**

- **Spatial Constraints**:
  - No spatial superposition allowed for wastes.
  - No spatial superposition allowed for robots.
- **Agent Behavior**:
  - Robots are programmed to move towards wastes of their color in their Moore neighborhood if they do not carry a waste payload, and to pick them once they have reached them.
  - They are designed to deposit waste payloads to the right border of the zone of their color.
  - Navigation is currently handled via random moves (with inertia) if there is no waste in their neighborhood.
    - An inertia decay factor is used to update the inertia of an agent according to its last move. 
    - An inertia power is used to determine the impact of the inertia on the choice of the random move.
  - Red robots remember the location of the disposal zone once first discovered. 
  - If green and yellow robots have exceeded a number of steps carrying one waste of their color, a communication process begin:
    - An agent in that situation sends a message to other agents to ask for an exchange of wastes.
    - Agents in the same situation can propose themselves for the exchange.
    - The agent chooses one of them (if there is at least one) and gives its position.
    - Once the other agent has reached it, it sends a message to the agent.
    - The agent deposit its waste and the other agent pick it.  
    - Each stage of this process has a limit of steps to avoid deadlocked cases.
  This process is described in the following sequence diagram :
  ![Alt Sequence Diagram](sequence_diagram.png?raw=true)

**Metrics Tracked**

A model is evaluated by:

- The average number of steps required to deposit all wastes across multiple simulations.
- The disposal score on multiple simulations: equal to four times the number of red wastes deposited.
- The efficiency on multiple simulations: the percentage of the disposed score compared to the total value of wastes at the beginning of each simulation, ponderated the following way : 
  - green waste : 1 point
  - yellow waste : 2 points
  - red waste : 4 points 
- The average cleared waste value and its standard deviation.

**Results**

The current experiment compares model behavior with and without inter-agent communication.

- With communication:
  - Average completion: 741.1 steps
  - Efficiency: 84.71%
  - Disposed score: 175.6 ± 70.8 points
- Without communication:
  - Average completion: 928.7 steps
  - Efficiency: 81.56%
  - Disposed score: 171.9 ± 72.7 points

This shows that communication improves efficiency by about 3.15 percentage points in the current run.

**Results and Current Limitations**

- Even with inertia, the random navigation is still not sufficient enough to efficiently detect and pick all wastes.
- There still exists some rare cases of softlock, especially around the waste disposal zone.
