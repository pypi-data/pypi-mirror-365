# path: timing/cli.py
import webbrowser
from pathlib import Path
from typing_extensions import Annotated

import typer
from rich.console import Console
from rich.table import Table

from . import config
from .engine import get_engine
from .report.builder import generate_dashboard
from .storage.sqlite import SqliteStorage

app = typer.Typer(
    rich_markup_mode="markdown",
    help="A local performance timer for Python applications.",
)
console = Console()


@app.command()
def init():
    """
    Initialize the database in the correct location.
    """
    console.print("--- Setting up Timing Module Database ---")
    engine = get_engine()
    if not engine.is_enabled():
        console.print(
            "⚠️ Timing tool is currently disabled. Run `timing enable` first if you want to record events."
        )
    engine.setup()


@app.command()
def status():
    """
    Display the current status and configuration.
    """
    settings = config.timing_settings
    is_enabled = settings.IS_ENABLED
    db_path = settings.DB_PATH

    table = Table(title="Timing Tool Status")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="magenta")

    status_emoji = "✅" if is_enabled else "❌"
    table.add_row("Enabled", f"{status_emoji} {is_enabled}")
    table.add_row("Database Path", str(db_path))

    event_count = 0
    if db_path.exists():
        try:
            storage = SqliteStorage(db_path)
            event_count = len(storage.read_all_completed())
        except Exception as e:
            console.print(f"[red]Error reading database: {e}[/red]")

    table.add_row("Completed Events", str(event_count))
    console.print(table)


@app.command()
def enable():
    """
    Enable the timing tool by creating a global config file.
    """
    config.set_enabled_state(True)
    console.print(
        "[green]✓ Timing tool enabled.[/green] Your shell will now record timing events."
    )


@app.command()
def disable():
    """
    Disable the timing tool by updating the global config file.
    """
    config.set_enabled_state(False)
    console.print(
        "[yellow]✓ Timing tool disabled.[/yellow] Events will no longer be recorded."
    )


@app.command()
def report(
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="The path for the output HTML file.",
            default="timing_dashboard.html",
        ),
    ],
    no_open: Annotated[
        bool,
        typer.Option("--no-open", help="Do not open the report in a browser."),
    ] = False,
):
    """
    Generate and optionally open the HTML performance report.
    """
    try:
        output_path = output.resolve()
        generate_dashboard(str(output_path))
        if not no_open:
            console.print(f"Opening {output_path} in your browser...")
            webbrowser.open(output_path.as_uri())
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("Have you run `timing init` and recorded some events?")
    except Exception as e:
        console.print(f"[red]Error: Failed to generate report. {e}[/red]")


if __name__ == "__main__":
    app()
