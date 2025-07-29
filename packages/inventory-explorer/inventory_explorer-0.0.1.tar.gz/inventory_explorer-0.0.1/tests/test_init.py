import pytest

from pathlib import Path

from inventory_explorer import expand_extra_vars_globs


def test_expand_extra_vars_globs(tmp_path: Path) -> None:
    foo = tmp_path / "foo.yml"
    bar_1 = tmp_path / "bar_1.yml"
    bar_2 = tmp_path / "bar_2.yml"
    bar_3 = tmp_path / "bar_3.yml"

    for file in [foo, bar_1, bar_2, bar_3]:
        file.touch()

    assert expand_extra_vars_globs(["a=b", f"@{foo}", f"@{tmp_path}/bar_*.yml"]) == [
        "a=b",
        f"@{foo}",
        f"@{bar_1}",
        f"@{bar_2}",
        f"@{bar_3}",
    ]
