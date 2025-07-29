"""Console script for air_init_mcp."""

import typer
from rich.console import Console

from air_init_mcp import utils

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for air_init_mcp."""
    console.print("Replace this message by putting your code into air_init_mcp.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()
