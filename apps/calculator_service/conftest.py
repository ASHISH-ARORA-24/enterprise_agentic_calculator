import sys
from pathlib import Path

# Add the calculator service root directory to sys.path so that
# "from app.domain.calculator import ..." resolves correctly
# when pytest runs from the monorepo root.
#
# Without this, Python looks for "app" starting from the repo root
# and cannot find it. With this, it looks inside apps/calculator_service/
# where the actual "app" package lives.
sys.path.insert(0, str(Path(__file__).parent))
