from typing import Annotated, Optional
import typer
from pathlib import Path
import os
from generative_databases.generators.generator import Generator

params_dict = {}

app = typer.Typer()
APP_NAME = "generative_databases"


@app.command()
def enter_params():
    params_dict.update(
        {"sample_size": typer.prompt("What sample size is required?", type=int)}
    )
    params_dict.update(
        {"city_data": typer.prompt("Enter a path to city data source", type=str)}
    )
    params_dict.update(
        {
            "names_data": typer.prompt(
                "Enter a path to first names data source", type=str
            )
        }
    )
    params_dict.update(
        {
            "last_names_data": typer.prompt(
                "Enter a path to last names data source", type=str
            )
        }
    )
    params_dict.update(
        {
            "loc_w_prob": typer.confirm(
                "Is the localisation to be generated using weighted probability?"
            )
        }
    )
    params_dict.update(
        {
            "names_w_prob": typer.confirm(
                "Is the list of names to be generated using weighted probability?"
            )
        }
    )
    params_dict.update(
        {
            "sex_prob": min(
                100,
                typer.prompt(
                    "Enter a chance for a person to be female (0-100%)", type=int
                ),
            )
        }
    )
    params_dict.update(
        {
            "sec_name_prob": min(
                100,
                typer.prompt(
                    "Enter a chance for a person to have a second name (0-100%)",
                    type=int,
                ),
            )
        }
    )

    typer.echo("Enter a desired year range for person's birth")
    year_range_f = typer.prompt("From: ", type=int)
    year_range_t = typer.prompt("To: ", type=int)

    params_dict.update({"year_range": [year_range_f, year_range_t]})

    os.system("cls")
    typer.echo(typer.style("Your answers:", fg=typer.colors.GREEN))
    for k in params_dict.keys():
        typer.echo(f"{k}, {params_dict[k]}")


# @app.command()
# def generate_database():
#     G = Generator(
#         params_dict["sample_size"],
#         "temp",
#         params_dict["city_data"],
#         params_dict["names_data"],
#         params_dict["last_names_data"],
#     )


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
    typer.echo(typer.style("This is a message in green", fg=typer.colors.GREEN))
    typer.echo(typer.style("This is a message in red", fg=typer.colors.RED))
    typer.echo(typer.style("This is a message in blue", fg=typer.colors.BLUE))
