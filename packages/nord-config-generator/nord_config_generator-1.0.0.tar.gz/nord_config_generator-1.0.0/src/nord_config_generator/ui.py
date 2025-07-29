from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.theme import Theme
from rich.table import Table
from pathlib import Path
import os

class ConsoleManager:
    def __init__(self):
        custom_theme = Theme({
            "info": "cyan",
            "success": "bold green",
            "warning": "yellow",
            "error": "bold red",
            "title": "bold magenta",
            "path": "underline bright_blue"
        })
        self.console = Console(theme=custom_theme)

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_title(self):
        self.console.print(Panel("[title]NordVPN Configuration Generator[/title]", expand=False, border_style="info"))

    def get_user_input(self, prompt: str, is_secret: bool = False) -> str:
        return self.console.input(f"[info]{prompt}[/info]", password=is_secret).strip()

    def get_preferences(self, defaults) -> dict:
        self.console.print("\n[info]Configuration Options (press Enter to use defaults)[/info]")
        dns = self.get_user_input(f"Enter DNS server IP (default: {defaults.dns}): ")
        endpoint_type = self.get_user_input("Use IP instead of hostname for endpoints? (y/N): ")
        keepalive = self.get_user_input(f"Enter PersistentKeepalive value (default: {defaults.persistent_keepalive}): ")
        return {"dns": dns, "endpoint_type": endpoint_type, "keepalive": keepalive}

    def print_message(self, style: str, message: str):
        self.console.print(f"[{style}]{message}[/{style}]")

    def create_progress_bar(self, transient: bool = True) -> Progress:
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
            transient=transient
        )

    def print_summary(self, output_dir: Path, total_configs: int, best_configs: int, elapsed_time: float):
        summary_table = Table.grid(padding=(0, 2))
        summary_table.add_column(style="info")
        summary_table.add_column()
        summary_table.add_row("Output Directory:", f"[path]{output_dir}[/path]")
        summary_table.add_row("Standard Configs:", f"{total_configs}")
        summary_table.add_row("Optimized Configs:", f"{best_configs}")
        summary_table.add_row("Time Taken:", f"{elapsed_time:.2f} seconds")

        self.console.print(Panel(
            summary_table,
            title="[success]Generation Complete[/success]",
            border_style="success",
            expand=False
        ))