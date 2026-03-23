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

- **Completed**: Environment setup and reactive agents implementation.
- **In Progress**: Addition of inter-agent communication.

**Technical Choices**

- **Spatial Constraints**:
  - No spatial superposition allowed for wastes.
  - No spatial superposition allowed for robots.
- **Agent Behavior**:
  - Robots are programmed to deposit wastes to their right.
  - Navigation is currently handled via random moves if no waste in their neighborhood

**Metrics Tracked**

- Evolution of the quantity of wastes for each color over time.
- Total number of wastes successfully deposited over time.

**Results and Current Limitations**

- Deadlock Issue: The system currently reaches a blocked state with unrecycled wastes remaining. Because agents are restricted from depositing a waste if it has not been transformed, robots end up holding onto single wastes indefinitely. This depletes the grid of available wastes and brings the recycling process to a halt. This issue will be fixed with communication.
