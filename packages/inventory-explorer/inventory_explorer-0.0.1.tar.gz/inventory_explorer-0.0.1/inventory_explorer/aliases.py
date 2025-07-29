"""
Inventory aliases files allow you to write ``--inventory <somevalue>`` as a
shorthand for a specific inventory defined in the
``inventory-explorer-aliases.yml file``.
"""

import sys
from pathlib import Path
from dataclasses import dataclass, field
from itertools import chain

import yaml


@dataclass
class Alias:
    name: str
    inventory_files: list[Path] = field(default_factory=list)
    extra_vars: list[str] = field(default_factory=list)


def read_aliases_file() -> dict[str, Alias]:
    """
    Attempt to read an aliases file from the current directory. Returns an
    empty dict if this fails for any reason.
    """
    alias_file = Path("inventory-explorer-aliases.yml")
    aliases: dict[str, Alias] = {}
    try:
        if alias_file.is_file():
            raw_aliases = yaml.safe_load(alias_file.read_text())
            if not isinstance(raw_aliases, dict):
                raise ValueError("Expected a dictionary of aliases to values.")

            aliases = {}
            for name, value in raw_aliases.items():
                # Normalise the value into the 'detailed' form
                if isinstance(value, str):
                    value = {"inventory_files": [value]}

                if isinstance(value, list):
                    value = {"inventory_files": value}

                if not isinstance(value, dict):
                    raise ValueError(
                        "Expected each alias to be a string, list or dict."
                    )

                # Check values are sensible
                unexpected_keys = set(value) - {"inventory_files", "extra_vars"}
                if unexpected_keys:
                    raise ValueError(f"Unexpected keys: {', '.join(unexpected_keys)}")

                inventory_files = value.get("inventory_files", [])
                if not isinstance(inventory_files, list):
                    raise ValueError(
                        "Expected inventory_files to be a list of strings."
                    )
                if not all(isinstance(file, str) for file in inventory_files):
                    raise ValueError("Expected inventory filenames to be strings.")

                extra_vars = value.get("extra_vars", [])
                if not isinstance(extra_vars, list):
                    raise ValueError("Expected extra_vars to be a list of strings.")
                if not all(isinstance(vars, str) for vars in extra_vars):
                    raise ValueError("Expected extra vars to be strings.")

                aliases[name] = Alias(
                    name=name,
                    inventory_files=list(map(Path, inventory_files)),
                    extra_vars=extra_vars,
                )
    except Exception as exc:
        print(
            f"Error loading inventory-explorer-aliases.yml: {exc.__class__.__name__}: {exc}",
            file=sys.stderr,
        )

    return aliases


def expand_aliases(
    inventory_files: list[Path],
    aliases: dict[str, Alias],
) -> tuple[list[Path], list[str]]:
    """
    Expand all aliases defined as names in 'inventory_files'.

    Returns the new list of inventory files (with alias names substituted for
    their filenames). Also returns an extended list of extra_vars specified by
    any used aliases.

    Substitute any aliases in a list of inventory filenames with the files
    specified in a set of aliases.
    """
    expanded_inventory_files = list(
        chain.from_iterable(
            aliases[str(inventory_file)].inventory_files
            if str(inventory_file) in aliases
            else [inventory_file]
            for inventory_file in inventory_files
        )
    )

    extra_vars = [
        vars
        for name in map(str, inventory_files)
        if name in aliases
        for vars in aliases[name].extra_vars
    ]

    return expanded_inventory_files, extra_vars
