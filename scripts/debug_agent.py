import sys
from pathlib import Path
import traceback

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from agents import OrchestratorAgent
    from core.config import config
    
    print(f"Config type: {type(config)}")
    print(f"Config dir: {dir(config)}")
    if hasattr(config, 'orchestrator_model'):
        print(f"Orchestrator model: {config.orchestrator_model}")
    else:
        print("MISSING orchestrator_model in config!")
        
    print("Attempting instantiation...")
    agent = OrchestratorAgent()
    print("Success!")
except Exception:
    traceback.print_exc()
