from typing import Annotated, Optional
import typer
from .data import name as gen_name, Gender
from pathlib import Path

app = typer.Typer()
APP_NAME = "generative_databases"


@app.callback()
def config():
    """
    This is a CLI tool to generate databases.
    """
    app_dir = typer.get_app_dir(APP_NAME)
    config_path: Path = Path(app_dir) / "config.json"
    if not config_path.is_file():
        print("Config file doesn't exist yet")


@app.callback()
def callback():
    """
    This is a CLI tool to generate databases.
    """
    typer.echo("Welcome to the generative databases CLI tool")


@app.command()
def shoot():
    """
    Shoot the database.
    """
    typer.echo("Shooting the database")


@app.command()
def load():
    """
    Load the database.
    """
    typer.echo("Loading the database")


@app.command()
def name(
    sex: Annotated[Gender, typer.Option("--gender", "-g", help="Select a gender")]
):
    """
    Generate a name.
    """
    res = gen_name(sex)
    typer.echo(f"Generated name: {res}")


@app.command()
def ask_name():
    """
    Ask for a name.
    """
    name = typer.prompt("What is your name?")
    typer.echo(f"You entered: {name}")


@app.command()
def confirm(
    yes: Annotated[
        Optional[bool],
        typer.Option("--yes", "-y", help="Confirm the operation"),
    ] = None
):
    """
    Confirm playground.
    """

    delete = yes is not None or typer.confirm(
        "Do you want to delete the database?",
        #   abort=True # if this is set to True, the program will exit if the user answers "no",
    )
    if delete:
        typer.echo("Deleting the database")
    else:
        typer.echo("Phew! That was close!")


@app.command()
def colored():
    """
    Print a colored message.
    """
    typer.echo("This is a message in green", fg=typer.colors.GREEN)
    typer.echo("This is a message in red", fg=typer.colors.RED)
    typer.echo("This is a message in blue", fg=typer.colors.BLUE)
