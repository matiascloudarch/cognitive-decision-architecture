import os
import asyncio
import sqlite3
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

# --- CONFIGURATION ---
DB_PATH = "cda_gate.db"
console = Console()

def get_logs():
    """
    Fetches execution logs from the Gate's database.
    Replaced blocking calls with a safer connection management.
    """
    try:
        if not os.path.exists(DB_PATH):
            return []
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Optimized query for performance
        cursor.execute("""
            SELECT id, entity_id, action, executed_at 
            FROM executed_intents 
            ORDER BY executed_at DESC 
            LIMIT 15
        """)
        
        rows = cursor.fetchall()
        conn.close()
        return rows
    except sqlite3.OperationalError:
        # Handles cases where the database is locked or table is not yet created
        return []

def generate_table() -> Table:
    """
    Generates a professional real-time visual table for the terminal.
    """
    table = Table(title="CDA Global Execution Monitor", highlight=True)
    table.add_column("Intent ID", style="cyan", no_wrap=True)
    table.add_column("Entity", style="magenta")
    table.add_column("Action", style="green")
    table.add_column("Timestamp", style="yellow")

    logs = get_logs()
    if not logs:
        table.add_row("No data", "Waiting for", "execution...", "---")
    else:
        for row in logs:
            table.add_row(str(row[0]), str(row[1]), str(row[2]), str(row[3]))
            
    return table

async def run_monitor():
    """
    Async loop to refresh the UI without blocking the system.
    """
    console.clear()
    console.print(Panel("[bold green]CDA Monitoring System Active[/bold green]\nMonitoring 'cda_gate.db' for activity..."))
    
    with Live(generate_table(), refresh_per_second=2) as live:
        while True:
            await asyncio.sleep(0.5)
            live.update(generate_table())

if __name__ == "__main__":
    try:
        asyncio.run(run_monitor())
    except KeyboardInterrupt:
        console.print("\n[bold red]Monitor stopped by user.[/bold red]")