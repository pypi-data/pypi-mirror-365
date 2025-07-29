"""Easy development with uv managed Python projects."""

from typing import Iterable
from pathlib import Path
import os
import shutil
import subprocess as sp
import toml
from loguru import logger
import pathspec
from .filesystem import replace_patterns
from . import git

DIST = "dist"
README = "README.md"
TOML = "pyproject.toml"


def _project_dir() -> Path:
    """Get the root directory of the uv managed Python project.

    :return: The root directory of the uv managed Python project.
    :raises RuntimeError: Raises RuntimeError if the current directory is not under a uv managed Python project.
    """
    path = Path.cwd()
    while path.parent != path:
        if (path / TOML).is_file():
            return path
        path = path.parent
    return Path()


def _project_name(proj_dir: Path) -> str:
    """Get the name of the uv managed Python project.

    :param proj_dir: The root directory of the uv managed Python project.
    :return: The name of the project.
    """
    return toml.load(proj_dir / TOML)["project"]["name"]


def _project_version(proj_dir: Path) -> str:
    """Get the version of the uv managed Python project.

    :param proj_dir: The root directory of the uv managed Python project.
    :return: Version of the uv managed Python project.
    """
    return toml.load(proj_dir / TOML)["project"]["version"]


def _update_version_readme(ver: str, proj_dir: Path) -> None:
    """Update the version information in README.md.

    :param ver: The new version.
    :param proj_dir: The root directory of the  project.
    """
    replace_patterns(proj_dir / README, pattern=r"\d+\.\d+\.\d+", repl=f"{ver}")


def _update_version_toml(ver: str, proj_dir: Path) -> None:
    """Update the version information in the TOML file.

    :param ver: The new version.
    :param proj_dir: The root directory of the uv managed Python project.
    """
    replace_patterns(
        proj_dir / TOML, pattern=r"version = .\d+\.\d+\.\d+.", repl=f'version = "{ver}"'
    )


def _update_version_init(ver: str, proj_dir: Path) -> None:
    """Update the version information in the file __init__.py.

    :param ver: The new version.
    :param proj_dir: The root directory of uv managed Python project.
    """
    pkg = _project_name(proj_dir)
    for path in (proj_dir / pkg).glob("**/*.py"):
        replace_patterns(
            path,
            pattern=r"__version__ = .\d+\.\d+\.\d+.",
            repl=f'__version__ = "{ver}"',
        )


def _update_version(ver: str, proj_dir: Path) -> None:
    """Update versions in files.

    :param ver: The new version.
    :param proj_dir: The root directory of the uv managed Python project.
    """
    if ver:
        _update_version_init(ver=ver, proj_dir=proj_dir)
        _update_version_toml(ver, proj_dir=proj_dir)
        _update_version_readme(ver=ver, proj_dir=proj_dir)
        sp.run(["git", "diff"], check=True)


def version(
    ver: str = "",
    commit: bool = False,
    proj_dir: Path | None = None,
) -> None:
    """List or update the version of the uv managed Python package.

    :param ver: The new version to use.
        If empty, then the current version of the package is printed.
    :param commit: Whether to commit changes.
    :param proj_dir: The root directory of the uv managed Python project.
    """
    if proj_dir is None:
        proj_dir = _project_dir()
    if ver:
        _update_version(ver=ver, proj_dir=proj_dir)
        if commit:
            repo = git.Repo(root=proj_dir)
            repo.add()
            repo.commit(message="bump up version")
            repo.push()
    else:
        print(_project_version(proj_dir))


def add_tag_release(
    proj_dir: str | Path | None = None, tag: str = "", branch_release: str = "main"
) -> None:
    """Add a tag to the latest commit on the release branch for releasing.
    The tag is decided based on the current version of the project.

    :param proj_dir: The root directory of the uv managed Python project.
    :param tag: The tag (defaults to the current version of the package) to use.
    :param branch_release: The branch for releasing.
    :raises ValueError: If the tag to create already exists.
    """
    if proj_dir is None:
        proj_dir = _project_dir()
    if not tag:
        tag = "v" + _project_version(proj_dir)
    repo = git.Repo(proj_dir)
    if tag.encode() in repo.tag():
        raise ValueError(
            f"The tag {tag} already exists! Please merge new changes to the {branch_release} branch first."
        )
    branch_old = repo.active_branch()
    # add tag to the release branch
    repo.checkout(branch=branch_release)
    repo.pull(branch=branch_release)
    repo.tag(tag=tag)
    repo.push(branch=tag)
    # switch back to the old branch
    repo.checkout(branch=branch_old)


def format_code(
    commit: bool = False,
    proj_dir: Path | None = None,
    files: Iterable[Path | str] = (),
) -> None:
    """Format code.

    :param commit: If true (defaults to False),
        commit code formatting changes automatically.
    :param proj_dir: The root directory of the uv managed Python project.
    :param files: An iterable of Python scripts to format.
        If empty, then the whole project is formatted.
    """
    cmd = "uv run ruff format "
    if files:
        cmd += " ".join(f"'{file}'" for file in files)
    else:
        if proj_dir is None:
            proj_dir = _project_dir()
        cmd += str(proj_dir)
    logger.info("Formatting code using ruff ...")
    sp.run(cmd, shell=True, check=False, stdout=sp.PIPE)
    if commit:
        repo = git.Repo(proj_dir)
        repo.add()
        repo.commit(message="format code")
        repo.push()
        repo.status()


def _lint_code(proj_dir: Path | None, linter: str | list[str]):
    funcs = {
        "ruff": _lint_code_ruff,
        "pytype": _lint_code_pytype,
    }
    if isinstance(linter, str):
        linter = [linter]
    for lint in linter:
        funcs[lint](proj_dir)


def _lint_code_pytype(proj_dir: Path | None):
    logger.info("Linting code using pytype ...")
    if not proj_dir:
        proj_dir = _project_dir()
    pkg = _project_name(proj_dir)
    cmd = f"uv run pytype {proj_dir / pkg} {proj_dir / 'tests'}"
    try:
        sp.run(cmd, shell=True, check=True)
    except sp.CalledProcessError:
        logger.error("Please fix errors: {}", cmd)


def _lint_code_ruff(proj_dir: Path | None):
    logger.info("Linting code using ruff ...")
    if not proj_dir:
        proj_dir = _project_dir()
    pkg = _project_name(proj_dir)
    cmd = f"uv run ruff check {proj_dir / pkg}"
    try:
        sp.run(cmd, shell=True, check=True)
    except sp.CalledProcessError:
        logger.error("Please fix errors: {}", cmd)


def _lint_code_flake8(proj_dir: Path | None):
    logger.info("Linting code using flake8 ...")
    if not proj_dir:
        proj_dir = _project_dir()
    pkg = _project_name(proj_dir)
    cmd = f"PATH={proj_dir}/.venv/bin:$PATH flake8 {proj_dir / pkg}"
    try:
        sp.run(cmd, shell=True, check=True)
    except sp.CalledProcessError:
        logger.error("Please fix errors: {}", cmd)


def _lint_code_darglint(proj_dir: Path | None):
    logger.info("Linting docstring using darglint ...")
    if not proj_dir:
        proj_dir = _project_dir()
    pkg = _project_name(proj_dir)
    cmd = f"PATH={proj_dir}/.venv/bin:$PATH darglint {proj_dir / pkg}"
    try:
        sp.run(cmd, shell=True, check=True)
    except sp.CalledProcessError:
        logger.error("Please fix errors: {}", cmd)


def build_package(
    proj_dir: Path | None = None,
    linter: str | Iterable[str] = ("ruff", "pytype"),
    test: bool = True,
) -> None:
    """Build the package using uv.

    :param proj_dir: The root directory of the uv managed Python project.
    :param linter: A linter or an iterable of linters.
    :param test: Whether to run test suits (using pytest).
    :raises FileNotFoundError: If the command uv is not found.
    """
    if not shutil.which("uv"):
        raise FileNotFoundError("The command uv is not found!")
    if proj_dir is None:
        proj_dir = _project_dir()
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    _lint_code(proj_dir=proj_dir, linter=linter)
    format_code(proj_dir=proj_dir)
    if test:
        logger.info("Running unit tests...")
        sp.run(f"cd '{proj_dir}' && uv run pytest", shell=True, check=True)
    logger.info("Building the package...")
    sp.run(f"cd '{proj_dir}' && uv build", shell=True, check=True)


def clean(proj_dir: Path | None = None, ignore: str | Path | None = None) -> None:
    """Remove non-essential files from the current project.

    :param proj_dir: The root directory of the uv managed Python project.
    :param ignore: The full path to a GitIgnore file.
    """
    if proj_dir is None:
        proj_dir = _project_dir()
    if ignore is None:
        ignore = proj_dir / ".gitignore"
    elif isinstance(ignore, str):
        ignore = Path(ignore)
    if not ignore.is_file():
        return
    logger.info("Use the GitIgnore file: {}", ignore)
    with ignore.open("r", encoding="utf-8") as fin:
        patterns = [line.strip() for line in fin]
    spec = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, patterns)
    _clean(proj_dir, spec)


def _clean(path: Path, spec: pathspec.PathSpec) -> None:
    if spec.match_file(path):
        if path.is_file():
            try:
                path.unlink()
            except Exception:
                logger.error("Failed to remove the file: {}", path)
        else:
            try:
                shutil.rmtree(path)
            except Exception:
                logger.error("Failed to remove the directory: {}", path)
        return
    if path.is_dir():
        for p in path.iterdir():
            _clean(p, spec)
