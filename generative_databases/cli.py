import typer

app = typer.Typer()


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
