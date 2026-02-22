"""
Setup script for AEGIS
Initializes databases, downloads models, and verifies installation
"""

import sys
from pathlib import Path
import sqlite3

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from loguru import logger

console = Console()

def setup_directories():
    """Create all required directories"""
    console.print("[cyan]Creating directories...[/cyan]")
    
    directories = [
        "data/vector_db",
        "data/memory/conversations",
        "data/memory/knowledge",
        "data/memory/logs",
        "data/backups",
    ]
    
    for dir_path in directories:
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
    
    console.print("[green]✓ Directories created[/green]")

def setup_sqlite_database():
    """Initialize SQLite database with schema"""
    console.print("[cyan]Initializing SQLite database...[/cyan]")
    
    db_path = Path("data/aegis.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Conversations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        summary TEXT,
        mode TEXT,
        participants TEXT
    )
    """)
    
    # Tasks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT,
        status TEXT,
        agent_assigned TEXT,
        start_time DATETIME,
        end_time DATETIME,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id)
    )
    """)
    
    # Permissions table (audit log)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS permissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        operation TEXT,
        danger_level TEXT,
        approval_status TEXT,
        user_message TEXT,
        had_code BOOLEAN
    )
    """)
    
    # Learning table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS learning (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pattern TEXT UNIQUE,
        frequency INTEGER DEFAULT 1,
        confidence REAL,
        last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Agent state table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_state (
        agent_id TEXT PRIMARY KEY,
        status TEXT,
        current_task TEXT,
        memory_usage_bytes INTEGER,
        last_active DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()
    
    console.print("[green]✓ SQLite database initialized[/green]")

def verify_ollama_models():
    """Verify required Ollama models are installed"""
    console.print("[cyan]Checking Ollama models...[/cyan]")
    
    import subprocess
    
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        required_models = [
            "hermes3:8b",
            "dolphin-llama3:8b",
            "phi3:latest",
            "dolphin-mistral:latest",
            "deepseek-coder:6.7b",
            "nomic-embed-text"
        ]
        
        installed = result.stdout.lower()
        missing = []
        
        for model in required_models:
            if model.lower().replace(":", " ") not in installed:
                missing.append(model)
        
        if missing:
            console.print(f"[yellow]⚠ Missing models: {', '.join(missing)}[/yellow]")
            console.print("[dim]Run: ollama pull <model_name>[/dim]")
        else:
            console.print("[green]✓ All required models installed[/green]")
        
    except subprocess.CalledProcessError:
        console.print("[red]✗ Could not check Ollama (is it running?)[/red]")
    except FileNotFoundError:
        console.print("[red]✗ Ollama not found. Install from https://ollama.ai[/red]")

def setup_env_file():
    """Create .env file from example if it doesn't exist"""
    console.print("[cyan]Checking environment configuration...[/cyan]")
    
    env_path = Path(".env")
    example_path = Path(".env.example")
    
    if not env_path.exists():
        if example_path.exists():
            import shutil
            shutil.copy(example_path, env_path)
            console.print("[green]✓ Created .env from .env.example[/green]")
        else:
            console.print("[yellow]⚠ No .env.example found[/yellow]")
    else:
        console.print("[green]✓ .env file exists[/green]")

def main():
    """Run full setup"""
    console.print("\n[bold cyan]🛡️  AEGIS Setup[/bold cyan]\n")
    
    try:
        setup_directories()
        setup_env_file()
        setup_sqlite_database()
        verify_ollama_models()
        
        console.print("\n[bold green]✅ Setup complete![/bold green]")
        console.print("\n[dim]Next steps:[/dim]")
        console.print("1. Ensure all models are downloaded (see above)")
        console.print("2. Run: [cyan]poetry install[/cyan]")
        console.print("3. Run: [cyan]poetry run aegis[/cyan]")
        
    except Exception as e:
        console.print(f"\n[bold red]Setup failed:[/bold red] {e}")
        logger.exception("Setup error")
        sys.exit(1)

if __name__ == "__main__":
    main()
