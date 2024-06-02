from typing import Annotated, Optional
import typer
import click
from pathlib import Path
import os

from generative_databases.generators.generator import Generator
from generative_databases.generators import data_importer

params_dict = {}

app = typer.Typer()
APP_NAME = "generative_databases"


@app.command()
def generate_database():
    """
    Enter parameters to build a database
    """
    params_dict.update(
        {"sample_size": typer.prompt("What sample size is required?", type=int)}
    )
    params_dict.update(
        {
            "city_data": typer.prompt(
                "Enter a path to city data source. Space for default",
                type=str,
            )
        }
    )
    params_dict.update(
        {
            "names_data": typer.prompt(
                "Enter a path to first names data source. Space for default",
                type=str,
            )
        }
    )
    params_dict.update(
        {
            "last_names_data": typer.prompt(
                "Enter a path to last names data source. Space for default",
                type=str,
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

    # Database Generation

    typer.echo(typer.style("Generating your database", fg=typer.colors.RED))
    try:
        G = Generator(params_dict=params_dict)
    except Exception as e:
        typer.echo(
            typer.style(
                "There has been a problem generating database!", fg=typer.colors.RED
            )
        )
        print(e)
    else:
        typer.echo(
            typer.style("Database generated Succesfully!", fg=typer.colors.GREEN)
        )

    # ask for save options
    if typer.confirm("Do you want to save the database?"):
        save_dict = {}
        choices = [
            "csv",
            "json",
            "xml",
            "excel",
            "html",
            "HDF5",
            "parquet",
            "feather",
            "stata",
            "sql",
        ]
        save_dict.update(
            {
                str(
                    typer.prompt("Enter a file format", type=click.Choice(choices))
                ).lower(): typer.prompt("Enter a path for the save file", type=str)
            }
        )
        while typer.confirm(
            "Do you want to save the database in another format/place?"
        ):
            save_dict.update(
                {
                    str(
                        typer.prompt("Enter a file format", type=click.Choice(choices))
                    ).lower(): typer.prompt("Enter a path for the save file", type=str)
                }
            )
        typer.style("Saving Database!", fg=typer.colors.RED)
        try:
            G.generate_and_save(save_dict)
        except Exception as e:
            typer.echo(
                typer.style(
                    "There has been a problem saving database!", fg=typer.colors.RED
                )
            )
            print(e)
        else:
            typer.echo(
                typer.style("Database saved Succesfully!", fg=typer.colors.GREEN)
            )


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
