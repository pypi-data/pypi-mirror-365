from __future__ import annotations

from usethis._config import usethis_config
from usethis._integrations.file.pyproject_toml.io_ import (
    PyprojectTOMLManager,
)
from usethis._integrations.file.pyproject_toml.valid import ensure_pyproject_validity
from usethis._integrations.uv.errors import UVSubprocessFailedError
from usethis._integrations.uv.link_mode import ensure_symlink_mode
from usethis._subprocess import SubprocessFailedError, call_subprocess


def call_uv_subprocess(args: list[str], change_toml: bool) -> str:
    """Run a subprocess using the uv command-line tool.

    Returns:
        str: The output of the subprocess.

    Raises:
        UVSubprocessFailedError: If the subprocess fails.
    """
    if usethis_config.disable_uv_subprocess:
        msg = "The `disable_uv_subprocess` option is set."
        raise UVSubprocessFailedError(msg)

    is_pyproject_toml = (usethis_config.cpd() / "pyproject.toml").exists()

    if change_toml and args[0] in {
        "lock",
        "add",
        "remove",
        "sync",
        "export",
        "tree",
        "run",
    }:
        ensure_symlink_mode()

    if is_pyproject_toml and change_toml:
        if PyprojectTOMLManager().is_locked():
            ensure_pyproject_validity()
            PyprojectTOMLManager().write_file()
            PyprojectTOMLManager()._content = None
        else:
            with PyprojectTOMLManager():
                ensure_pyproject_validity()

    if usethis_config.frozen and args[0] in {
        # Note, not "lock", for which the --frozen flags has quite a different effect
        "add",
        "remove",
        "sync",
        "export",
        "tree",
        "run",
    }:
        new_args = ["uv", args[0], "--frozen", *args[1:]]
    else:
        new_args = ["uv", *args]

    if usethis_config.offline:
        new_args = [*new_args[:2], "--offline", *new_args[2:]]

    if usethis_config.subprocess_verbose:
        new_args = [*new_args[:2], "--verbose", *new_args[2:]]
    elif args[:2] != ["python", "list"]:
        new_args = [*new_args[:2], "--quiet", *new_args[2:]]

    try:
        output = call_subprocess(
            new_args, cwd=usethis_config.cpd() if args[0] != "init" else None
        )
    except SubprocessFailedError as err:
        raise UVSubprocessFailedError(err) from None

    if change_toml and PyprojectTOMLManager().is_locked():
        PyprojectTOMLManager().read_file()

    return output
