import pytest

from typing import Any

from pathlib import Path
from textwrap import dedent

from inventory_explorer.aliases import (
    Alias,
    read_aliases_file,
    expand_aliases,
)


@pytest.fixture
def aliases_file(tmp_path: Path, monkeypatch: Any) -> Path:
    monkeypatch.chdir(tmp_path)
    aliases_file = tmp_path / "inventory-explorer-aliases.yml"
    return aliases_file


class TestReadAliasesFile:
    def test_no_file(self, aliases_file: Path) -> None:
        assert read_aliases_file() == {}

    def test_empty_file(self, aliases_file: Path) -> None:
        aliases_file.write_text("{}")
        assert read_aliases_file() == {}

    def test_short_form(self, aliases_file: Path) -> None:
        aliases_file.write_text("foo: bar/inventory.yml")
        assert read_aliases_file() == {
            "foo": Alias(name="foo", inventory_files=[Path("bar/inventory.yml")])
        }

    def test_list_form(self, aliases_file: Path) -> None:
        aliases_file.write_text("foo: [bar/inventory.yml, baz/inventory.yml]")
        assert read_aliases_file() == {
            "foo": Alias(
                name="foo",
                inventory_files=[Path("bar/inventory.yml"), Path("baz/inventory.yml")],
            )
        }

    def test_long_form(self, aliases_file: Path) -> None:
        aliases_file.write_text(
            dedent(
                """
                    foo:
                      inventory_files:
                        - foo/inventory.yml
                      extra_vars:
                        - a=b
                """
            )
        )
        assert read_aliases_file() == {
            "foo": Alias(
                name="foo",
                inventory_files=[Path("foo/inventory.yml")],
                extra_vars=["a=b"],
            ),
        }

    def test_multiple_aliases(self, aliases_file: Path) -> None:
        aliases_file.write_text("foo: foo/inventory.yml\nbar: bar/inventory.yml")
        assert read_aliases_file() == {
            "foo": Alias(
                name="foo",
                inventory_files=[Path("foo/inventory.yml")],
            ),
            "bar": Alias(
                name="bar",
                inventory_files=[Path("bar/inventory.yml")],
            ),
        }

    @pytest.mark.parametrize(
        "content",
        [
            # Not valid YAML
            ":",
            # type errors
            "null",
            "foo: null",
            "foo: {wut: null}",
            "foo: [null]",
            "foo: {inventory_files: nope}",
            "foo: {inventory_files: [null]}",
            "foo: {extra_vars: nope}",
            "foo: {extra_vars: [null]}",
        ],
    )
    def test_malformed(self, aliases_file: Path, content: str, capsys: Any) -> None:
        aliases_file.write_text(content)

        # Should just return nothing
        assert read_aliases_file() == {}

        # But should also print an error
        _out, err = capsys.readouterr()
        assert err.startswith("Error loading inventory-explorer-aliases.yml:")


def test_expand_inventory_file_aliases() -> None:
    aliases = {
        "foo": Alias(
            name="foo",
            inventory_files=[Path("foo_1/inventory.ini"), Path("foo_2/inventory.ini")],
            extra_vars=["foo=bar", "@baz.yml"],
        ),
        # Not used
        "nope": Alias(
            name="nope",
            inventory_files=[Path("nope.ini")],
            extra_vars=["nope=naww"],
        ),
    }
    inventory_files, extra_vars = expand_aliases(
        [Path("a"), Path("foo"), Path("bar")], aliases
    )

    assert inventory_files == [
        Path("a"),
        Path("foo_1/inventory.ini"),
        Path("foo_2/inventory.ini"),
        Path("bar"),
    ]

    assert extra_vars == [
        "foo=bar",
        "@baz.yml",
    ]
