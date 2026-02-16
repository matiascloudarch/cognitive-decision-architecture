import sqlite3
import time
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.live import Live

# Configuration
DB_PATH = "cda_gate.db"
console = Console()

def fetch_audit_logs():
    """Fetches the latest execution logs from the Gate's audit database."""
    if not os.path.exists(DB_PATH):
        return []
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Fetch logs ordered by time
        cursor.execute("SELECT id, entity_id, action, executed_at FROM executed_intents ORDER BY executed_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except sqlite3.OperationalError:
        # Database lock or missing table handling
        return []

def generate_table() -> Table:
    """Generates the visual table for the terminal."""
    table = Table(title="[bold cyan]CDA System: Security Monitor[/bold cyan]", 
                  subtitle="[grey50]Press Ctrl+C to exit[/grey50]")
    
    table.add_column("Token ID (JTI)", justify="left", style="magenta", no_wrap=True)
    table.add_column("Entity", justify="center", style="green")
    table.add_column("Action", justify="center", style="yellow")
    table.add_column("Timestamp", justify="right", style="blue")

    logs = fetch_audit_logs()
    
    for log in logs:
        short_id = f"{log[0][:12]}..."
        table.add_row(short_id, log[1], log[2], log[3])
    
    return table

def start_monitor():
    """Main execution loop for the monitor."""
    console.clear()
    console.print("[bold green]Monitor online. Listening for Gate logs...[/bold green]\n")
    
    try:
        with Live(generate_table(), refresh_per_second=1) as live:
            while True:
                time.sleep(2)
                live.update(generate_table())
    except KeyboardInterrupt:
        console.print("\n[bold red]Monitor stopped.[/bold red]")

if __name__ == "__main__":
    start_monitor()