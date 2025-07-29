import pytest

from typing import Iterator

import os
from pathlib import Path
from textwrap import dedent

from inventory_explorer.ansible import (
    get_default_inventory_path,
    enumerate_variables_files,
    Host,
    Group,
    Inventory,
    load_ansible_inventory,
    evaluate_host_vars,
)


@pytest.fixture
def chdir(tmp_path: Path) -> Iterator[None]:
    orig_dir = os.getcwd()
    try:
        os.chdir(tmp_path)
        yield
    finally:
        os.chdir(orig_dir)


class TestGetDefaultInventoryPath:
    def test_system_default(self, chdir: None) -> None:
        assert get_default_inventory_path() == Path("/etc/ansible/hosts")

    def test_configuration_file(self, tmp_path: Path, chdir: None) -> None:
        inventory = Path("inventory.yml")
        inventory.write_text("foo:\n  hosts:\n    bar:")

        ansible_cfg = Path("ansible.cfg")
        ansible_cfg.write_text("[defaults]\ninventory = inventory.yml")

        assert get_default_inventory_path() == inventory


class TestEnumerateVariableFiles:
    def test_none(self, tmp_path: Path) -> None:
        assert enumerate_variables_files(tmp_path, "nope") == []

    def test_single_file_invalid_extension_ignored(self, tmp_path: Path) -> None:
        (tmp_path / "foo.__yml").touch()
        assert enumerate_variables_files(tmp_path, "foo") == []

    @pytest.mark.parametrize(
        "extension",
        [
            "",
            ".yml",
            ".yaml",
            ".json",
        ],
    )
    def test_single_file(self, tmp_path: Path, extension: str) -> None:
        file = tmp_path / f"foo{extension}"
        file.touch()
        assert enumerate_variables_files(tmp_path, "foo") == [file]

    def test_directory(self, tmp_path: Path) -> None:
        foo = tmp_path / f"foo"
        foo.mkdir()

        a = foo / "a"
        b = foo / "b.yml"
        c = foo / "c.yaml"
        d = foo / "d.json"
        nope = foo / "nope.__yml"

        subdir = foo / "subdir"
        subdir.mkdir()

        e = subdir / "e"

        for file in [a, b, c, d, e]:
            file.touch()

        assert enumerate_variables_files(tmp_path, "foo") == sorted([a, b, c, d, e])


class TestLoadAnsibleInventory:
    def test_empty(self, tmp_path: Path) -> None:
        inventory_file = tmp_path / "inventory.yml"
        inventory_file.write_text("all:")

        inventory = load_ansible_inventory([inventory_file], [])
        assert inventory.files == [inventory_file]
        assert inventory.hosts == {}

        assert set(inventory.groups) == {"all"}
        for group in inventory.groups.values():
            assert group.hosts == set()

    def test_just_yaml(self, tmp_path: Path) -> None:
        inventory_file = tmp_path / "inventory.yml"
        inventory_file.write_text(
            dedent(
                """
                    # Demonstrate host and group variables
                    web:
                      hosts:
                        web-1:
                          number: 1
                        web-2:
                          number: 2
                        web-3:
                          number: 3
                      vars:
                        url: http://www.example.com/
                    # Some more groups
                    mail:
                      hosts:
                        mail-1:
                        mail-2:
                        mail-3:
                    db:
                      hosts:
                        db-1:
                        db-2:
                        db-3:
                    # Demonstrate nesting groups
                    frontend:
                      children:
                        web:
                        mail:
                      vars:
                        front: end
                """
            )
        )

        inventory = load_ansible_inventory([inventory_file], [])
        assert inventory.files == [inventory_file]

        assert set(inventory.hosts) == {
            "web-1",
            "web-2",
            "web-3",
            "mail-1",
            "mail-2",
            "mail-3",
            "db-1",
            "db-2",
            "db-3",
        }

        # Web hosts
        for i in range(1, 4):
            host_name = f"web-{i}"
            assert inventory.hosts[host_name].name == host_name
            assert inventory.hosts[host_name].files == []
            assert inventory.hosts[host_name].vars == {
                "number": i,
                "front": "end",
                "url": "http://www.example.com/",
            }
            assert inventory.hosts[host_name].host_vars == {"number": i}
            assert inventory.hosts[host_name].groups == {"web", "frontend", "all"}

        # Mail hosts
        for i in range(1, 4):
            host_name = f"mail-{i}"
            assert inventory.hosts[host_name].name == host_name
            assert inventory.hosts[host_name].files == []
            assert inventory.hosts[host_name].vars == {"front": "end"}
            assert inventory.hosts[host_name].host_vars == {}
            assert inventory.hosts[host_name].groups == {"mail", "frontend", "all"}

        # DB hosts
        for i in range(1, 4):
            host_name = f"db-{i}"
            assert inventory.hosts[host_name].name == host_name
            assert inventory.hosts[host_name].files == []
            assert inventory.hosts[host_name].vars == {}
            assert inventory.hosts[host_name].groups == {"db", "all"}

        assert set(inventory.groups) == {"all", "web", "mail", "db", "frontend"}

        for group_name, group in inventory.groups.items():
            assert group.name == group_name
            assert group.files == []

        # 'all' group
        assert inventory.groups["all"].children == {"db", "frontend", "ungrouped"}
        assert inventory.groups["all"].group_vars == {}
        assert inventory.groups["all"].hosts == set(inventory.hosts)

        # 'web' group
        assert inventory.groups["web"].children == set()
        assert inventory.groups["web"].group_vars == {"url": "http://www.example.com/"}
        assert inventory.groups["web"].hosts == {"web-1", "web-2", "web-3"}

        # 'mail' group
        assert inventory.groups["mail"].children == set()
        assert inventory.groups["mail"].group_vars == {}
        assert inventory.groups["mail"].hosts == {"mail-1", "mail-2", "mail-3"}

        # 'db' group
        assert inventory.groups["db"].children == set()
        assert inventory.groups["db"].group_vars == {}
        assert inventory.groups["db"].hosts == {"db-1", "db-2", "db-3"}

        # 'frontend' group
        assert inventory.groups["frontend"].children == {"web", "mail"}
        assert inventory.groups["frontend"].group_vars == {"front": "end"}
        assert inventory.groups["frontend"].hosts == {
            "web-1",
            "web-2",
            "web-3",
            "mail-1",
            "mail-2",
            "mail-3",
        }

    def test_with_files(self, tmp_path: Path) -> None:
        inventory_file = tmp_path / "inventory.yml"
        inventory_file.write_text(
            dedent(
                """
                    # Demonstrate host and group variables
                    web:
                      hosts:
                        web-1:
                          foo: bar
                          inventory: true
                      vars:
                        bar: foo
                        inventory: true
                """
            )
        )

        (tmp_path / "host_vars").mkdir()
        (tmp_path / "host_vars" / "web-1").mkdir()
        web_1_vars_1 = tmp_path / "host_vars" / "web-1" / "vars_1.yaml"
        web_1_vars_2 = tmp_path / "host_vars" / "web-1" / "vars_2.yaml"

        web_1_vars_1.write_text("foo: baz\nquo: 1\nfile_1: true")
        web_1_vars_2.write_text("foo: qux\nquo: 2\nfile_2: true")

        (tmp_path / "group_vars").mkdir()
        group_vars = tmp_path / "group_vars" / "web.yml"
        group_vars.write_text("bar: baz\nfile: true")

        inventory = load_ansible_inventory([inventory_file], [])

        assert inventory.hosts["web-1"].files == [web_1_vars_1, web_1_vars_2]
        assert inventory.hosts["web-1"].host_vars == {
            "inventory": True,
            "file_1": True,
            "file_2": True,
            # Higher-numbered file wins
            "foo": "qux",
            "quo": 2,
        }

        assert inventory.groups["web"].files == [group_vars]
        assert inventory.groups["web"].group_vars == {
            "inventory": True,
            "file": True,
            # File wins
            "bar": "baz",
        }

    def test_multiple_inventories(self, tmp_path: Path) -> None:
        inventory_a = tmp_path / "a"
        inventory_b = tmp_path / "b"

        inventory_a.mkdir()
        inventory_b.mkdir()

        # Inventory A
        inventory_file_a = inventory_a / "inventory.yml"
        inventory_file_a.write_text(
            dedent(
                """
                    # Demonstrate host and group variables
                    web:
                      hosts:
                        web-1:
                          foo: bar
                          inventory: a
                        web-2:
                          foo: qux
                          inventory: a
                      vars:
                        bar: foo
                        inventory: a
                """
            )
        )

        (inventory_a / "host_vars").mkdir()
        host_vars_a = inventory_a / "host_vars" / "web-1.yml"
        host_vars_a.write_text("host: var")

        (inventory_a / "group_vars").mkdir()
        group_vars_a = inventory_a / "group_vars" / "web.yml"
        group_vars_a.write_text("group: var")

        # Inventory B
        inventory_file_b = inventory_b / "inventory.yml"
        inventory_file_b.write_text(
            dedent(
                """
                    web:
                      hosts:
                        web-1:
                          foo: bar
                          inventory: b  # Different
                        # web-2 missing
                      vars:
                        bar: foo
                        inventory: b  # Different
                """
            )
        )

        (inventory_b / "host_vars").mkdir()
        host_vars_b = inventory_b / "host_vars" / "web-1.yml"
        host_vars_b.write_text("host: var")

        (inventory_b / "group_vars").mkdir()
        group_vars_b = inventory_b / "group_vars" / "web.yml"
        group_vars_b.write_text("group: var")

        inventory = load_ansible_inventory([inventory_file_a, inventory_file_b], [])

        assert inventory.hosts["web-1"].files == [host_vars_a, host_vars_b]
        assert inventory.hosts["web-1"].host_vars == {
            "foo": "bar",
            "inventory": "b",
            "host": "var",
        }
        assert inventory.hosts["web-2"].files == []
        assert inventory.hosts["web-2"].host_vars == {
            "foo": "qux",
            "inventory": "a",
        }

        assert inventory.groups["web"].files == [group_vars_a, group_vars_b]
        assert inventory.groups["web"].group_vars == {
            "bar": "foo",
            "inventory": "b",
            "group": "var",
        }

    def test_extra_vars(self, tmp_path: Path) -> None:
        inventory_file = tmp_path / "inventory.yml"
        inventory_file.write_text(
            dedent(
                """
                    web:
                      hosts:
                        web-1:
                          a: 1
                          b: 2
                """
            )
        )

        (tmp_path / "c.yml").write_text("c: 3")

        inventory = load_ansible_inventory(
            [inventory_file], ["a=ONE", f"@{tmp_path / 'c.yml'}"]
        )

        assert inventory.hosts["web-1"].vars == {
            "a": "ONE",
            "b": 2,
            "c": 3,
        }
        assert inventory.hosts["web-1"].host_vars == {
            "a": 1,
            "b": 2,
        }
        assert inventory.groups["web"].group_vars == {}


def test_evaluate_host_vars(tmp_path: Path) -> None:
    inventory_file = tmp_path / "inventory.yml"
    inventory_file.write_text(
        dedent(
            """
                web:
                  hosts:
                    web-1:
                      foo: "you know, bar is '{{ bar }}'"
                      a: 1
                      b: 2
                  vars:
                    bar: 123
            """
        )
    )

    (tmp_path / "c.yml").write_text("c: 3")
    extra_vars = ["a=ONE", f"@{tmp_path / 'c.yml'}"]

    inventory = load_ansible_inventory([inventory_file], extra_vars)

    # Variables not expanded in inventory
    assert inventory.hosts["web-1"].vars == {
        "foo": "you know, bar is '{{ bar }}'",
        "bar": 123,
        "a": "ONE",
        "b": 2,
        "c": 3,
    }

    host_vars = evaluate_host_vars(inventory, extra_vars, "web-1")

    # Should include all variables we set
    assert host_vars["bar"] == 123

    # And should have evaluated any templates
    assert host_vars["foo"] == "you know, bar is '123'"

    # Should have extra-vars applied
    assert host_vars["a"] == "ONE"
    assert host_vars["b"] == 2
    assert host_vars["c"] == 3

    # And should include built-in Ansible facts
    assert host_vars["inventory_hostname"] == "web-1"
