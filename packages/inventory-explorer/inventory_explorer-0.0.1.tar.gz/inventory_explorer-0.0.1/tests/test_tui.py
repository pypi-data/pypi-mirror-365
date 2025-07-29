import pytest

from pathlib import Path
from textwrap import dedent

from inventory_explorer.tui import (
    yaml_file_has_leading_document_marker,
    concatenate_yaml_files,
)


@pytest.mark.parametrize(
    "src, exp",
    [
        ("", False),
        ("a: 123", False),
        ("a: 123\n...", False),
        ("---\na: 123", True),
        ("---\na: 123\n...", True),
        ("---\na: 123\n---\nb: 321", True),
    ],
)
def test_yaml_file_has_leading_document_marker(src: str, exp: bool) -> None:
    assert yaml_file_has_leading_document_marker(src) == exp


class TestConcatenateYamlFiles:
    def test_no_files(self) -> None:
        assert concatenate_yaml_files([]) == ""

    @pytest.mark.parametrize(
        "content",
        [
            "",
            "# Empty!",
            "a: 123",
            "a: 123\nb: 321",
        ],
    )
    def test_one_file(self, content: str, tmp_path: Path) -> None:
        f = tmp_path / "f.yml"
        f.write_text(content)
        assert concatenate_yaml_files([f]) == content

    def test_multiple_files(self, tmp_path: Path) -> None:
        # Single line, no trailing newline
        foo = tmp_path / "foo.yml"
        foo.write_text("foo: 123")

        # Multiple lines, comments and with trailing newline
        bar = tmp_path / "bar.yml"
        bar.write_text(
            dedent(
                """
                    bar:
                      - 1  # One
                      - 2  # Two
                      - 3  # Three!
                """
            ).lstrip()
        )

        # Multiple documents
        baz = tmp_path / "baz.yml"
        baz.write_text(
            dedent(
                """
                    ---
                    baz: 1

                    ---
                    baz: 2

                    ---
                    baz: 3
                """
            ).lstrip()
        )

        # Empty!
        qux = tmp_path / "qux.yml"
        qux.write_text("")

        assert concatenate_yaml_files([foo, bar, baz, qux]) == (
            dedent(
                f"""
                    # {foo}
                    foo: 123

                    # {bar}
                    ---
                    bar:
                      - 1  # One
                      - 2  # Two
                      - 3  # Three!


                    # {baz}
                    ---
                    baz: 1

                    ---
                    baz: 2

                    ---
                    baz: 3


                    # {qux}
                    ---
                """
            ).lstrip()
        )
