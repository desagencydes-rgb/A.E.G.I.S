
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.getcwd())

from agents.orchestrator import OrchestratorAgent
from loguru import logger

# Configure logger to print to stdout
logger.remove()
logger.add(sys.stdout, level="INFO")

async def verify_file_creation():
    print("--- Starting Verification: File Creation ---")
    
    # Initialize Orchestrator
    try:
        orchestrator = OrchestratorAgent()
        print("✅ Orchestrator Initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Orchestrator: {e}")
        return

    # Define the target file path
    target_dir = Path(os.getcwd()) / "verification_output"
    target_file = target_dir / "hello_world.java"
    
    # Cleanup previous run
    if target_file.exists():
        os.remove(target_file)
    if target_dir.exists():
        import shutil
        shutil.rmtree(target_dir)
        
    print(f"Target file: {target_file}")

    # Create the task
    # We simulate a user message that should trigger the coding agent via the orchestrator
    user_message = f"create a java hello world file at {str(target_file)}"
    
    print(f"User Message: '{user_message}'")
    
    # Process the message
    print("--- Processing Task ---")
    try:
        async for response_chunk in orchestrator.handle_message(user_message):
            print(f"[Stream]: {response_chunk}", end="")
    except Exception as e:
        print(f"\n❌ Exception during processing: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n--- Processing Complete ---")

    # Verify result
    if target_file.exists():
        content = target_file.read_text()
        print(f"✅ File created successfully!")
        print(f"--- File Content ---\n{content}\n--------------------")
        
        if "public class hello_world" in content or "public class HelloWorld" in content:
             print("✅ Content looks like valid Java")
        else:
             print("⚠️ Content might not be valid Java")
    else:
        print("❌ File was NOT created.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_file_creation())
