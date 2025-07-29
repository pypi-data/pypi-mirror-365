"""
Routines for implementing various interactive terminal UI features.
"""

from typing import TypeVar, Iterable, Sequence

import os
import sys
import select
import platform
from copy import deepcopy
import string
import subprocess
from pathlib import Path

import yaml
from fzy import tui as fzy  # Also re-exported

# Unix only
try:
    import fcntl
    import termios
except ImportError:
    pass

# Windows only
try:
    import msvcrt
except ImportError:
    pass


def get_keypress_unix() -> str:
    """Capture a single keypress (under a Unix-like OS)."""
    fd = sys.stdin.fileno()

    old_attr = termios.tcgetattr(fd)
    old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)

    new_attr = deepcopy(old_attr)

    # Disable canonical mode (i.e. receive input as soon as its ready rather
    # than waiting for a whole line)
    new_attr[3] = new_attr[3] & ~termios.ICANON

    # Don't display characters as they're typed
    new_attr[3] = new_attr[3] & ~termios.ECHO

    # Switch to non-blocking mode (to allow us to read a whole keypress from
    # the file buffer without having to know how long it is)
    new_flags = old_flags | os.O_NONBLOCK

    try:
        # Apply terminal/IO options
        termios.tcsetattr(fd, termios.TCSANOW, new_attr)
        fcntl.fcntl(fd, fcntl.F_SETFL, new_flags)

        # Read keypress
        select.select([sys.stdin], [], [])
        return sys.stdin.read()
    finally:
        # Restore terminal/IO options
        termios.tcsetattr(fd, termios.TCSAFLUSH, old_attr)
        fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)


def get_keypress_windows() -> str:
    """Capture a single keypress (under Windows)."""
    return msvcrt.getch()  # type: ignore


def get_keypress() -> str:
    """Capture a single keypress."""
    if platform.system() == "Windows":
        return get_keypress_windows()
    else:
        return get_keypress_unix()


T = TypeVar("T")


def choice(
    choices: dict[str, T],
    prompt: str = "> ",
    default: T | None = None,
    case_sensitive: bool = False,
) -> T:
    """
    Display an interactive multiple-choice prompt. The user must specify the
    first letter of each of the provided choices (which must not be ambiguous).

    The returned value is the dictionary value for the corresponding choice.

    If escape, Ctrl+C or Ctrl+D are encountered, KeyboardInterrupt is raised.
    """
    # Sanity check
    if len({c[0] for c in choices}) != len(choices):
        raise ValueError("Choices must have distinct first characters.")

    # Enumerate choices
    for choice, value in choices.items():
        letter = choice[0]
        if choice[1] == " ":
            choice = choice[2:]

        if value == default:
            print(f" \033[1m[{letter}]\033[0m {choice} \033[2m(default)\033[0m")
        else:
            print(f" \033[1m[{letter}]\033[0m {choice}")

    # Normalise case if case-insensitive
    choices = {
        c[0] if case_sensitive else c[0].casefold(): v for c, v in choices.items()
    }

    # Wait for valid choice to be made
    while True:
        print(f"\033[1;34m{prompt}\033[0m", end="", flush=True)

        try:
            key = get_keypress()
        except KeyboardInterrupt:
            print()
            raise KeyboardInterrupt()

        if not case_sensitive:
            key = key.casefold()

        if key in choices:  # Letter chosen
            print(key)
            return choices[key]
        elif key in ("\n", "\r") and default is not None:  # Left empty
            print()
            return default
        elif key in ("\x1B", "\x04"):  # Escape/Ctrl+D
            print()
            raise KeyboardInterrupt()

        if key in string.printable:
            print(key)
        else:
            print()
        print(f"Invalid choice, please pick one of {', '.join(map(repr, choices))}")


class FzfError(Exception):
    """Thrown if fzf fails for some reason."""


def fzf(
    input_lines: Iterable[str],
    prompt: str = "> ",
    history_file: Path | None = None,
) -> str | None:
    """
    Run fzf, starting it immediately and then iterating over the iterator
    returned by get_input_lines to obtian input for fzf.

    Returns the selected value, or None if nothing selected.

    If interrupted with keyboard interrupt or escape, raises KeyboardInterrupt.
    """
    args = [
        "fzf",
        "--prompt",
        prompt,
    ]
    if history_file is not None:
        # Check history file is writable
        try:
            with history_file.open("a"):
                pass
            args.extend(["--history", str(history_file)])
        except (FileNotFoundError, PermissionError):
            # Ignore the history file if we can't write to it
            pass

    try:
        with subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        ) as proc:
            assert proc.stdin is not None
            assert proc.stdout is not None
            try:
                for line in input_lines:
                    proc.stdin.write(line + "\n")
                proc.stdin.close()
            except BrokenPipeError:
                # FZF exited already
                pass

            output = list(proc.stdout)
    except FileNotFoundError:
        raise FzfError("The 'fzf' command is not installed.")

    if proc.returncode == 0:
        return output[0].rstrip()
    elif proc.returncode == 1:
        return None
    elif proc.returncode == 130:  # Ctrl+C / Escape
        raise KeyboardInterrupt()
    else:
        raise FzfError(f"fzf exited with status {proc.returncode}")


def editor(*files: Path) -> None:
    """Edit some files using the system editor."""
    print("Starting editor...")
    subprocess.run([os.environ.get("EDITOR", "nano")] + list(map(str, files)))


def yaml_file_has_leading_document_marker(yaml_string: str) -> bool:
    """
    Returns True iff the provided document has a leading `---` document marker
    and False otherwise.
    """
    docs_before_marker_added = max(1, len(list(yaml.safe_load_all(yaml_string))))
    docs_after_marker_added = len(list(yaml.safe_load_all("---\n" + yaml_string)))

    return docs_before_marker_added != docs_after_marker_added


def concatenate_yaml_files(files: Sequence[Path]) -> str:
    """
    Concatenate a series of YAML files, inserting document dividers between
    each file when they don't already exist.

    Iff multiple files are provided, adds a comment to the start of each file
    indicating its filename.
    """
    yaml_string = ""

    for i, file in enumerate(files):
        document = file.read_text()

        if i != 0:
            yaml_string += "\n\n"

        if len(files) > 1:
            yaml_string += f"# {file}\n"

        if i != 0 and not yaml_file_has_leading_document_marker(document):
            yaml_string += "---\n"

        yaml_string += document

    return yaml_string


def fzy_files(*files: Path) -> None:
    """Display a set of YAML documents with the fzy YAML fuzzy search tool."""
    fzy(concatenate_yaml_files(files))
