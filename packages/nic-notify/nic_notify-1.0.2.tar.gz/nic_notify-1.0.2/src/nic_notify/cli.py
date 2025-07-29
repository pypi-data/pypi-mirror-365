"""Console script for notify_service."""

import typer
from rich.console import Console

from notify_service import utils

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for notify_service."""
    console.print("Replace this message by putting your code into "
               "notify_service.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()
