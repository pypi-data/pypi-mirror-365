"""
Various routines for working with Ansible and its inventory data.
"""

from typing import Any, Iterator

from pathlib import Path
from dataclasses import dataclass, field
import subprocess
import json
from tempfile import TemporaryDirectory
from textwrap import dedent
from itertools import chain

import yaml


class AnsibleError(Exception):
    """Thrown if we have trouble running an Ansible command."""


def get_default_inventory_path() -> Path:
    """
    Get the current default inventory path (e.g. as configured in
    `ansible.cfg`).
    """
    ansible = subprocess.run(
        [
            "ansible-config",
            "dump",
            "--format",
            "json",
        ],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )

    if ansible.returncode != 0:
        raise AnsibleError(ansible.stdout + ansible.stderr)

    ansible_config = json.loads(ansible.stdout)
    ansible_config_by_name = {
        option["name"]: option
        for option in ansible_config
        # The special {"GALAXY_SERVERS": {...}} entry lacks a name, but is also
        # not interesting here...
        if "name" in option
    }
    inventory_names = ansible_config_by_name["DEFAULT_HOST_LIST"]["value"]

    try:
        # Attempt to return a path relative to the current directory
        return Path(inventory_names[0]).relative_to(Path().resolve())
    except ValueError:
        return Path(inventory_names[0])


def enumerate_variables_files(vars_dir: Path, name: str) -> list[Path]:
    """
    Given a group_vars or host_vars directory and a group or host name
    (respectively) return the list of files defining variables for that group
    or host.
    """
    files = []

    for extension in ["", ".yml", ".yaml", ".json"]:
        if (vars_dir / f"{name}{extension}").is_file():
            files.append(vars_dir / f"{name}{extension}")

    files.extend(
        f
        for f in (vars_dir / name).glob("**/*")
        if f.is_file() and f.suffix in ["", ".yml", ".yaml", ".json"]
    )

    files.sort()

    return files


@dataclass
class Host:
    # Host name
    name: str

    # Files in host_vars for this host
    files: list[Path] = field(default_factory=list)

    # The combined host, group and extra variables for this host.
    vars: dict[str, Any] = field(default_factory=dict)

    # Variables defined just for this host, excluding group and extra variables
    host_vars: dict[str, Any] = field(default_factory=dict)

    # Groups this host is transitively a member of
    groups: set[str] = field(default_factory=set)


@dataclass
class Group:
    # Group name
    name: str

    # Filenames of group_vars definition files
    files: list[Path] = field(default_factory=list)

    # Variables defined on this Group, not including extra variables, or
    # variables defined by parent groups.
    group_vars: dict[str, Any] = field(default_factory=dict)

    # Hosts which are (transitively) a member of this group
    hosts: set[str] = field(default_factory=set)

    # Direct child group names
    children: set[str] = field(default_factory=set)


@dataclass
class Inventory:
    # Inventory file names
    files: list[Path]

    # The directory name of the last inventory (semi-arbitrary choice -- this
    # inventory has the highest priority so...). This is only used as a
    # location to store fzf history files.
    directory: Path

    # The hosts defined in the inventory
    hosts: dict[str, Host]

    # The groups defined in the inventory
    groups: dict[str, Group]


def load_ansible_inventory(
    inventory_files: list[Path],
    extra_vars: list[str],
) -> Inventory:
    """
    Load an Ansible inventory.
    """
    # Here we run the ansible-inventory process twice, once in --export mode,
    # which keeps host and group variables separate, and once in normal mode,
    # which emits the combined host and group variables for each host.

    ansible_inventory_arguments = ["ansible-inventory", "--list"]
    for inventory_file in inventory_files:
        ansible_inventory_arguments.extend(["--inventory", str(inventory_file)])
    for vars in extra_vars:
        ansible_inventory_arguments.extend(["--extra-vars", str(vars)])

    with TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)

        # NB: Run the two ansible-inventory processes in parallel
        export_mode_stderr_file = (tmpdir / "export_mode.stderr").open("w+")
        export_mode_proc = subprocess.Popen(
            ansible_inventory_arguments + ["--export"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=export_mode_stderr_file,
            text=True,
        )

        normal_mode_stderr_file = (tmpdir / "normal_mode.stderr").open("w+")
        normal_mode_proc = subprocess.Popen(
            ansible_inventory_arguments,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=normal_mode_stderr_file,
            text=True,
        )

        assert export_mode_proc.stdout is not None
        assert normal_mode_proc.stdout is not None
        export_mode_stdout = export_mode_proc.stdout.read()
        normal_mode_stdout = normal_mode_proc.stdout.read()

        export_mode_proc.wait()
        normal_mode_proc.wait()

        if export_mode_proc.returncode != 0:
            export_mode_stderr_file.seek(0)
            export_mode_stderr = export_mode_stderr_file.read()
            raise AnsibleError(export_mode_stdout + export_mode_stderr)
        if normal_mode_proc.returncode != 0:
            normal_mode_stderr_file.seek(0)
            normal_mode_stderr = normal_mode_stderr_file.read()
            raise AnsibleError(normal_mode_stdout + normal_mode_stderr)

    export_mode_inventory = json.loads(export_mode_stdout)
    normal_mode_inventory = json.loads(normal_mode_stdout)

    all_hosts = {
        host_name
        for group_name, data in export_mode_inventory.items()
        for host_name in data.get("hosts", [])
        if group_name != "_meta"
    }

    inventory = Inventory(
        files=inventory_files,
        directory=inventory_files[-1].parent,
        hosts={
            host_name: Host(
                name=host_name,
                files=list(
                    chain.from_iterable(
                        enumerate_variables_files(
                            inventory_file.parent / "host_vars", host_name
                        )
                        for inventory_file in inventory_files
                    )
                ),
                vars=normal_mode_inventory["_meta"]["hostvars"].get(host_name, {}),
                host_vars=export_mode_inventory["_meta"]["hostvars"].get(host_name, {}),
            )
            for host_name in all_hosts
        },
        groups={
            group_name: Group(
                name=group_name,
                files=list(
                    chain.from_iterable(
                        enumerate_variables_files(
                            inventory_file.parent / "group_vars", group_name
                        )
                        for inventory_file in inventory_files
                    )
                ),
                group_vars=data.get("vars", {}),
                hosts=set(data.get("hosts", [])),
                children=set(data.get("children", [])),
            )
            for group_name, data in export_mode_inventory.items()
            if group_name != "_meta"
        },
    )

    def enumerate_group_and_children(group_name: str) -> Iterator[str]:
        """Recursively iterate over the group and child groups specified."""
        if group_name in inventory.groups:
            yield group_name
            for child_name in inventory.groups[group_name].children:
                yield from enumerate_group_and_children(child_name)

    # Transitively populate groups properties of Group objects
    for group_name in inventory.groups:
        for child_name in enumerate_group_and_children(group_name):
            for host_name in inventory.groups[child_name].hosts:
                inventory.hosts[host_name].groups.add(group_name)

    # Transitively populate hosts properties of Host objects
    for host_name, host in inventory.hosts.items():
        for group_name in host.groups:
            inventory.groups[group_name].hosts.add(host_name)

    return inventory


def evaluate_host_vars(
    inventory: Inventory, extra_vars: list[str], host: str
) -> dict[str, Any]:
    """
    Evaluate the host variables for a given host. Returns the evaluated host
    vars.
    """
    print("Evaluating host variables...")
    with TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        playbook = tmpdir / "playbook.yml"
        hostvars_file = tmpdir / "hostvars.yml"

        playbook.write_text(
            dedent(
                f"""
                    ---
                    - hosts: {host}
                      gather_facts: false
                      become: false
                      tasks:
                        - delegate_to: localhost
                          copy:
                            content: "{{{{ hostvars[inventory_hostname] | to_yaml }}}}"
                            dest: "{hostvars_file}"
                """
            )
        )

        ansible = subprocess.run(
            [
                "ansible-playbook",
            ]
            + list(
                chain.from_iterable(
                    ("--inventory", str(inventory_file))
                    for inventory_file in inventory.files
                )
            )
            + list(
                chain.from_iterable(("--extra-vars", str(vars)) for vars in extra_vars)
            )
            + [
                str(playbook),
            ],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
        )

        if ansible.returncode != 0:
            raise AnsibleError(ansible.stdout + ansible.stderr)

        return yaml.safe_load(hostvars_file.read_text())
