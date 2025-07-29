# -*- coding: utf-8 -*-

"""
Defines the base 'baderkit' command that all other commands stem from.
"""

from enum import Enum
from pathlib import Path

import typer

from baderkit.command_line.tools import tools_app

# from typing_extensions import Annotated


baderkit_app = typer.Typer(rich_markup_mode="markdown")


@baderkit_app.callback(no_args_is_help=True)
def base_command():
    """
    This is the base command that all baderkit commands stem from
    """
    pass


@baderkit_app.command()
def version():
    """
    Prints the version of baderkit that is installed
    """
    import baderkit

    print(f"Installed version: v{baderkit.__version__}")


class Method(str, Enum):
    weight = "weight"
    hybrid_weight = "hybrid-weight"
    ongrid = "ongrid"
    reverse_neargrid = "reverse-neargrid"
    neargrid = "neargrid"


class RefinementMethod(str, Enum):
    recursive = "recursive"
    single = "single"


class Format(str, Enum):
    vasp = "vasp"
    cube = "cube"


class PrintOptions(str, Enum):
    all_atoms = "all_atoms"
    sel_atoms = "sel_atoms"
    sum_atoms = "sum_atoms"
    all_basins = "all_basins"
    sel_basins = "sel_basins"
    sum_basins = "sum_basins"


@baderkit_app.command()
def run(
    charge_file: Path = typer.Argument(
        default=...,
        help="The path to the charge density file",
    ),
    reference_file: Path = typer.Option(
        None,
        "--reference_file",
        "-ref",
        help="The path to the reference file",
    ),
    method: Method = typer.Option(
        Method.reverse_neargrid,
        "--method",
        "-m",
        help="The method to use for separating bader basins",
        case_sensitive=False,
    ),
    refinement_method: RefinementMethod = typer.Option(
        RefinementMethod.recursive,
        "--refinement-method",
        "--rm",
        help="For methods that refine the edges (neargrid, hybrid-neargrid), whether to refine recursively or a single time.",
        case_sensitive=False,
    ),
    format: Format = typer.Option(
        None,
        "--format",
        "-f",
        help="The format of the files",
        case_sensitive=False,
    ),
    print: PrintOptions = typer.Option(
        None,
        "--print",
        "-p",
        help="Optional printing of atom or bader basins",
        case_sensitive=False,
    ),
    indices=typer.Argument(
        default=[],
        help="The indices used for print method. Can be added at the end of the call. For example: `baderkit run CHGCAR -p sel_basins 0 1 2`",
    ),
):
    """
    Runs a bader analysis on the provided files. File formats are automatically
    parsed based on the name. Current accepted files include VASP's CHGCAR/ELFCAR
    or .cube files.
    """
    from baderkit.core import Bader

    # instance bader
    bader = Bader.from_dynamic(
        charge_filename=charge_file,
        reference_filename=reference_file,
        method=method,
        refinement_method=refinement_method,
        format=format,
    )
    # write summary
    bader.write_results_summary()

    # write basins
    if indices is None:
        indices = []
    if print == "all_atoms":
        bader.write_all_atom_volumes()
    elif print == "all_basins":
        bader.write_all_basin_volumes()
    elif print == "sel_atoms":
        bader.write_atom_volumes(atom_indices=indices)
    elif print == "sel_basins":
        bader.write_basin_volumes(basin_indices=indices)
    elif print == "sum_atoms":
        bader.write_atom_volumes_sum(atom_indices=indices)
    elif print == "sum_basins":
        bader.write_basin_volumes_sum(basin_indices=indices)


# Register other commands
baderkit_app.add_typer(tools_app, name="tools")
