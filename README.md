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

- Evolution of the quantity of wastes for each color over time.
- Total number of wastes successfully deposited over time.

**Results and Current Limitations**

- Even with inertia, the random navigation is still not sufficient enough to efficiently detect and pick all wastes.
