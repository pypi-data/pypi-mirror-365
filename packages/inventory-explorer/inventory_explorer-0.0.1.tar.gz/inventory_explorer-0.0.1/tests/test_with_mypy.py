from pathlib import Path
from subprocess import run


def test_with_mypy() -> None:
    run(
        [
            "mypy",
            str(Path(__file__).parent.parent / "inventory_explorer"),
            str(Path(__file__).parent.parent / "tests"),
        ],
        check=True,
    )
