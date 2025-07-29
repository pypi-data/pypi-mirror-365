"""
This module contains the actual application logic for the inventory explorer.

The general implementation concept is that each function presents some part of
the UI. Once the user has finished their interaction with that part of the UI
(e.g. they've made a choice from a list of options or finished viewing a file)
the function returns a new callable representing the next piece of UI to show.

When a component of the UI wants to exit, it should raise KeyboardInterrupt.
"""

from typing import Callable

from functools import partial
from textwrap import indent
from pathlib import Path

from fzy import use_yaml_multiline_strings
import yaml

from inventory_explorer.background_processing import CachedBackgroundCall
from inventory_explorer.ansible import (
    Host,
    Group,
    Inventory,
    load_ansible_inventory,
    evaluate_host_vars,
)
from inventory_explorer.tui import (
    choice,
    fzf,
    editor,
    fzy,
    fzy_files,
)


def select_host(
    inventory: Inventory, extra_vars: list[str], subset: set[str] | None = None
) -> Callable:
    """
    Let the user pick a host. If subset is specified, allow a choice from this
    subset of hosts only.
    """
    host = fzf(
        sorted(subset if subset is not None else inventory.hosts),
        prompt="host> ",
        history_file=inventory.directory / ".inventory_navigator_host_history",
    )
    if host is None:
        raise KeyboardInterrupt()

    return partial(show_host, inventory, extra_vars, host)


def show_host(inventory: Inventory, extra_vars: list[str], host: str) -> Callable:
    """
    Display basic information about a host and let the user pick what extra
    information they'd like to see next.
    """
    print()
    print(f"\033[1mHost: {host}\033[0m")

    print(f"  Groups:")
    print(
        indent(
            "\n".join(sorted(inventory.hosts[host].groups)),
            "    ",
        )
    )

    if inventory.hosts[host].files:
        print(f"  Host variable files:")
        print(
            indent(
                "\n".join(map(str, inventory.hosts[host].files)),
                "    ",
            )
        )

    print()
    print("What would you like to do?")
    return choice(
        {
            "v Display combined host, group and extra variables": partial(
                show_combined_host_vars, inventory, extra_vars, host
            ),
            "h Display just host variables": partial(
                show_host_vars, inventory, extra_vars, host
            ),
            "x Display template-expanded host variables": partial(
                show_expanded_host_vars, inventory, extra_vars, host
            ),
        }
        | (
            {
                "f Display host variable files": partial(
                    show_host_vars_files, inventory, extra_vars, host
                ),
                "e Edit host variable files": partial(
                    edit_host_vars_files, inventory, extra_vars, host
                ),
            }
            if inventory.hosts[host].files
            else {}
        )
        | {
            "g Jump to containing group": partial(
                select_group, inventory, extra_vars, inventory.hosts[host].groups
            ),
        }
    )


def show_host_vars_files(
    inventory: Inventory, extra_vars: list[str], host: str
) -> Callable:
    """
    Show the contents of all host variables files for this host.
    """
    fzy_files(*inventory.hosts[host].files)
    return partial(show_host, inventory, extra_vars, host)


def edit_host_vars_files(
    inventory: Inventory, extra_vars: list[str], host: str
) -> Callable:
    """
    Edit all host variables files for this host.
    """
    editor(*inventory.hosts[host].files)
    return partial(show_host, inventory, extra_vars, host)


def show_combined_host_vars(
    inventory: Inventory, extra_vars: list[str], host: str
) -> Callable:
    """
    Show the combined inventory + host_vars variables for a host.
    """
    fzy(yaml.dump(inventory.hosts[host].vars))

    return partial(show_host, inventory, extra_vars, host)


def show_host_vars(inventory: Inventory, extra_vars: list[str], host: str) -> Callable:
    """
    Show just host-defined variables for a host.
    """
    fzy(yaml.dump(inventory.hosts[host].host_vars))

    return partial(show_host, inventory, extra_vars, host)


def show_expanded_host_vars(
    inventory: Inventory, extra_vars: list[str], host: str
) -> Callable:
    """
    Show the Ansible evaluated variables for a host.
    """
    try:
        hostvars = evaluate_host_vars(inventory, extra_vars, host)
    except KeyboardInterrupt:
        print("Aborted host variable evaluation.")
        return partial(show_host, inventory, extra_vars, host)

    fzy(yaml.dump(hostvars))

    return partial(show_host, inventory, extra_vars, host)


def select_group(
    inventory: Inventory, extra_vars: list[str], subset: set[str] | None = None
) -> Callable:
    """
    Let the user pick a group. If subset is specified, allow a choice from this
    subset of groups only.
    """
    group = fzf(
        sorted(subset if subset is not None else inventory.groups),
        prompt="group> ",
        history_file=inventory.files[-1].parent / ".inventory_navigator_group_history",
    )
    if group is None:
        raise KeyboardInterrupt()

    return partial(show_group, inventory, extra_vars, group)


def show_group(inventory: Inventory, extra_vars: list[str], group: str) -> Callable:
    """
    Display basic information about a group and let the user pick what extra
    information they'd like to see next.
    """
    print()
    print(f"\033[1mGroup: {group}\033[0m")

    print(f"  Hosts:")
    print(
        indent(
            "\n".join(sorted(inventory.groups[group].hosts)),
            "    ",
        )
    )

    if inventory.groups[group].files:
        print(f"  Group variable files:")
        print(
            indent(
                "\n".join(map(str, inventory.groups[group].files)),
                "    ",
            )
        )

    print()
    print("What would you like to do?")
    return choice(
        {
            "v Display group variables (excluding parent group variables)": partial(
                show_group_vars, inventory, extra_vars, group
            ),
        }
        | (
            {
                "f Display group variable files": partial(
                    show_group_vars_files, inventory, extra_vars, group
                ),
                "e Edit group variable files": partial(
                    edit_group_vars_files, inventory, extra_vars, group
                ),
            }
            if inventory.groups[group].files
            else {}
        )
        | {
            "h Jump to member host": partial(
                select_host, inventory, extra_vars, inventory.groups[group].hosts
            ),
        }
    )


def show_group_vars_files(
    inventory: Inventory, extra_vars: list[str], group: str
) -> Callable:
    """
    Show the contents of all group variables files for this host.
    """
    fzy_files(*inventory.groups[group].files)
    return partial(show_group, inventory, extra_vars, group)


def edit_group_vars_files(
    inventory: Inventory, extra_vars: list[str], group: str
) -> Callable:
    """
    Edit all group variables files for this host.
    """
    editor(*inventory.groups[group].files)
    return partial(show_group, inventory, extra_vars, group)


def show_group_vars(
    inventory: Inventory, extra_vars: list[str], group: str
) -> Callable:
    """
    Show the combined inventory + group_vars variables for a group.
    """
    fzy(yaml.dump(inventory.groups[group].group_vars))

    return partial(show_group, inventory, extra_vars, group)


def run(inventory_files: list[Path], extra_vars: list[str]) -> None:
    # Start loading the inventory immediately in the background rather than
    # waiting until after the user to make their first choice...
    get_inventory = CachedBackgroundCall(
        partial(load_ansible_inventory, inventory_files, extra_vars)
    )

    # Make display of multiline strings easier to read
    use_yaml_multiline_strings()

    while True:
        # Initial prompt
        print("What would you like to find?")
        try:
            initial_fn = choice(
                {
                    "Host": select_host,
                    "Group": select_group,
                }
            )
        except KeyboardInterrupt:
            break

        # Wait for inventory to finish loading
        if not get_inventory.ready:
            print("Loading inventory...")
        inventory = get_inventory()

        # The main UI loop. On exit from this we go back to the starting prompt
        # to allow the user to start again from any host.
        fn = partial(initial_fn, inventory, extra_vars)
        while True:
            try:
                fn = fn()  # type: ignore
            except KeyboardInterrupt:
                print()
                break
