"""
Setup Script for ChatDev-AEGIS Bridge

Automates the integration setup process:
1. Check prerequisites
2. Install dependencies
3. Copy bridge to ChatDev
4. Test basic functionality
"""

import sys
import subprocess
from pathlib import Path
import shutil
from loguru import logger

# Paths
AEGIS_ROOT = Path(__file__).parent.parent
CHATDEV_ROOT = AEGIS_ROOT / "ChatDev"
BRIDGE_SOURCE = AEGIS_ROOT / "chatdev_bridge"
BRIDGE_DEST = CHATDEV_ROOT / "node" / "aegis_bridge"


def check_prerequisites():
    """Check that required components are installed"""
    print("\n=== Checking Prerequisites ===")
    
    # Check ChatDev exists
    if not CHATDEV_ROOT.exists():
        print(f"⚠ ChatDev not found at: {CHATDEV_ROOT}")
        print("Cloning ChatDev repository now... (this may take a moment)")
        try:
            subprocess.run(
                ["git", "clone", "https://github.com/OpenBMB/ChatDev.git", str(CHATDEV_ROOT)],
                check=True,
                capture_output=True,
                text=True
            )
            print("✓ ChatDev repository cloned successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to clone ChatDev: {e.stderr}")
            return False
        except FileNotFoundError:
            print("❌ Git is not installed or not in PATH")
            return False
    else:
        print("✓ ChatDev repository found")
    
    # Check Python version
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python {version.major}.{version.minor} found, need 3.11+")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    
    # Check Ollama (optional - will warn but not fail)
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✓ Ollama is running")
        else:
            print("⚠ Ollama not responding (optional for setup)")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("⚠ Ollama not found (required for runtime)")
    
    return True


def install_chatdev_dependencies():
    """Install ChatDev Python dependencies"""
    print("\n=== Installing ChatDev Dependencies ===")
    
    # Check if uv is available
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        use_uv = True
        print("✓ uv package manager found")
    except (FileNotFoundError, subprocess.CalledProcessError):
        use_uv = False
        print("⚠ uv not found, falling back to pip")
    
    try:
        if use_uv:
            # Use uv sync
            print("Installing with uv sync...")
            result = subprocess.run(
                ["uv", "sync"],
                cwd=CHATDEV_ROOT,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
        else:
            # Use pip
            print("Installing with pip...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                cwd=CHATDEV_ROOT,
                capture_output=True,
                text=True,
                timeout=300
            )
        
        if result.returncode == 0:
            print("✓ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Installation failed:\n{result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Installation timed out")
        return False
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False


def copy_bridge_to_chatdev():
    """Copy AEGIS bridge to ChatDev node directory"""
    print("\n=== Installing AEGIS Bridge ===")
    
    # Create node directory if it doesn't exist
    node_dir = CHATDEV_ROOT / "node"
    if not node_dir.exists():
        print("Creating ChatDev/node/ directory...")
        node_dir.mkdir(parents=True)
    
    # Remove existing bridge if present
    if BRIDGE_DEST.exists():
        print(f"Removing existing bridge at {BRIDGE_DEST}")
        shutil.rmtree(BRIDGE_DEST)
    
    # Copy bridge
    print(f"Copying bridge from {BRIDGE_SOURCE} to {BRIDGE_DEST}")
    shutil.copytree(BRIDGE_SOURCE, BRIDGE_DEST)
    
    # Verify copy
    required_files = ["__init__.py", "aegis_node.py", "config.py", "permission_enforcer.py", "memory_bridge.py"]
    for file in required_files:
        file_path = BRIDGE_DEST / file
        if not file_path.exists():
            print(f"❌ Missing file: {file}")
            return False
    
    print("✓ Bridge copied successfully")
    print(f"   Location: {BRIDGE_DEST}")
    return True


def create_env_file():
    """Create .env file in ChatDev if it doesn't exist"""
    print("\n=== Configuring Environment ===")
    
    env_example = CHATDEV_ROOT / ".env.example"
    env_file = CHATDEV_ROOT / ".env"
    
    if env_file.exists():
        print("✓ .env file already exists")
        return True
    
    if env_example.exists():
        print("Copying .env.example to .env")
        shutil.copy(env_example, env_file)
        print("✓ Created .env file")
        print("⚠ You may need to configure API keys in .env")
        return True
    else:
        print("⚠ .env.example not found - skipping")
        return True


def test_bridge():
    """Test that bridge can be imported"""
    print("\n===Testing Bridge ===")
    
    sys.path.insert(0, str(CHATDEV_ROOT / "node"))
    
    try:
        from aegis_bridge import AEGISAgentNode, BridgeConfig, PermissionEnforcer
        print("✓ Bridge modules import successfully")
        
        # Test configuration
        agent_types = list(BridgeConfig.AGENT_TYPES.keys())
        print(f"✓ {len(agent_types)} agent types registered:")
        for agent_type in agent_types[:5]:
            print(f"    - {agent_type}")
        if len(agent_types) > 5:
            print(f"    ... and {len(agent_types) - 5} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Bridge import failed: {e}")
        return False


def print_next_steps():
    """Print instructions for next steps"""
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print("\nNext Steps:")
    print("\n1. Configure API Keys (if using cloud models):")
    print(f"   Edit: {CHATDEV_ROOT / '.env'}")
    print("   Set API_KEY and BASE_URL for your LLM provider")
    
    print("\n2. Start ChatDev Server:")
    print(f"   cd {CHATDEV_ROOT}")
    print("   uv run python server_main.py --port 6400")
    
    print("\n3. Test AEGIS Integration:")
    print(f"   cd {AEGIS_ROOT}")
    print("   python scripts/test_chatdev_integration.py")
    
    print("\n4. Access Web Console:")
    print("   Open: http://localhost:5173")
    print("   (After starting frontend with 'cd frontend && npm run dev')")
    
    print("\n5. Try Example Workflow:")
    print("   Load: workflows/aegis_simple_test.yaml")
    print("   Task: 'Research Python async and create example code'")
    
    print("\n" + "="*60 + "\n")


def main():
    """Run full setup"""
    print("\n" + "="*60)
    print("AEGIS-ChatDev Bridge Setup")
    print("="*60)
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please fix issues and retry.")
        sys.exit(1)
    
    # Step 2: Install ChatDev dependencies (optional - can skip)
    print("\nWould you like to install ChatDev dependencies? (This may take several minutes)")
    print("You can skip this if you've already installed them or plan to do it manually.")
    
    # For automated setup, we'll skip dependency installation for now
    # Users can run: cd ChatDev && uv sync manually
    print("\nSkipping dependency installation (run 'cd ChatDev && uv sync' manually)")
    
    # Step 3: Copy bridge
    if not copy_bridge_to_chatdev():
        print("\n❌ Bridge installation failed")
        sys.exit(1)
    
    # Step 4: Create .env
    create_env_file()
    
    # Step 5: Test bridge
    if not test_bridge():
        print("\n⚠ Bridge test failed, but installation may still work")
    
    # Done
    print_next_steps()


if __name__ == "__main__":
    main()
