import sys
from pathlib import Path

# Add the agent API root directory to sys.path so that
# "from agent_api.agents.calculator_agent import ..." resolves correctly
# when pytest runs from the monorepo root.
sys.path.insert(0, str(Path(__file__).parent))
