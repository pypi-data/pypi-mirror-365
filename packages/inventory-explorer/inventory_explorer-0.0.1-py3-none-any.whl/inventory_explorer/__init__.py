from argparse import ArgumentParser

__version__ = "v0.0.1"

import sys
from pathlib import Path
from glob import glob
from itertools import chain

from inventory_explorer.ansible import get_default_inventory_path
from inventory_explorer.aliases import read_aliases_file, expand_aliases
from inventory_explorer.app import run


def expand_extra_vars_globs(extra_vars: list[str]) -> list[str]:
    """
    Expand any shell globs in extra var file filenames.

    This is non-standard Ansible behaviour but potentially quite handy (e.g.
    for OpenStack Ansible which by convention includes a set of extra vars
    files in its invocations based on a shell glob).
    """
    return list(
        chain.from_iterable(
            (f"@{filename}" for filename in sorted(glob(vars[1:], recursive=True)))
            if vars.startswith("@")
            else [vars]
            for vars in extra_vars
        )
    )


def main() -> None:
    parser = ArgumentParser(
        description="""
            An interactive tool for interactively exploring an Ansible
            inventory.
        """
    )
    parser.add_argument(
        "--inventory",
        "-i",
        type=Path,
        default=None,
        action="append",
        help="""
            The Ansible inventory to explore. If not specified, will default to
            whatever is configured in your Ansible environment. If a file named
            `inventory-explorer-aliases.yml` exists in the current directory,
            the provided inventory name will be looked up in that file to be
            resolved to its full path. May be used multiple times.
        """,
    )
    parser.add_argument(
        "--extra-vars",
        "-e",
        type=str,
        default=[],
        action="append",
        help="""
            Extra variables to specify, using the syntax expected by Ansible.
            As an extension to the Ansible syntax, extra vars filenames
            containing a shell-style glob patterns will be expanded to all
            matching files.
        """,
    )

    args = parser.parse_args()

    # Expand all aliases
    inventory_files: list[Path]
    extra_vars: list[str]
    if args.inventory is not None:
        aliases = read_aliases_file()
        inventory_files, extra_vars = expand_aliases(args.inventory, aliases)
    else:
        inventory_files = [get_default_inventory_path()]
        extra_vars = []
    extra_vars.extend(args.extra_vars)

    # Expand any globs in file extra vars
    extra_vars = expand_extra_vars_globs(extra_vars)

    # Check inventory files reachable
    for inventory_file in inventory_files:
        if not inventory_file.is_file():
            print(f"Inventory file not found: {inventory_file}")
            sys.exit(1)

    # Check extra vars files are reachable
    for vars in extra_vars:
        if vars.startswith("@") and not Path(vars[1:]).is_file():
            print(f"Extra vars file not found: {vars}")
            sys.exit(1)

    run(inventory_files, extra_vars)
