#!/usr/bin/env python3
"""Filesystem related util functions."""

from collections import namedtuple
from typing import Iterable, Callable
import itertools
import os
import sys
import re
import shutil
import math
from pathlib import Path
import subprocess as sp
from itertools import chain
import tempfile
from tqdm import tqdm
import pandas as pd
from loguru import logger
import dulwich.porcelain

HOME = Path.home()
PosixPathPair = namedtuple("PosixPathPair", ["prefix", "base"])


def copy_if_exists(src: str, dst: str | Path = HOME) -> bool:
    """Copy a file.
    No exception is thrown if the source file does not exist.

    :param src: The path of the source file.
    :param dst: The path of the destination file.
    :return: True if a copy if made, vice versa.
    """
    if not os.path.exists(src):
        return False
    try:
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False


def link_if_exists(
    src: str, dst: str | Path = HOME, target_is_directory: bool = True
) -> bool:
    """Make a symbolic link of a file.
    No exception is thrown if the source file does not exist.

    :param src: The path of the source file.
    :param dst: The path of the destination file.
    :param target_is_directory: Whether the target is a directory.
    :return: True if a symbolic link is created, vice versa.
    """
    if not os.path.exists(src):
        return False
    if os.path.exists(dst):
        shutil.rmtree(dst)
    try:
        os.symlink(src, dst, target_is_directory=target_is_directory)
        return True
    except Exception:
        return False


def count_path(
    paths: Iterable[str],
    weights: Iterable[int | float] | None = None,
) -> pd.Series:
    """Count frequence of paths and their parent paths.

    :param paths: An iterable collection of paths.
    :param weights: Weights of paths.
    :return: A pandas Series with paths as index and frequencies of paths as value.
    """

    def _count_path_helper(path: str, weight: int | float, freq: dict) -> None:
        fields = path.rstrip("/").split("/")[:-1]
        path = ""
        for field in fields:
            path = path + field + "/"
            freq[path] = freq.get(path, 0) + weight

    freq = {}
    if weights is None:
        weights = itertools.repeat(1)
    for path, weight in zip(paths, weights):
        _count_path_helper(path, weight, freq)
    return pd.Series(freq, name="count")


def zip_subdirs(root: str | Path) -> None:
    """Compress subdirectories into zip files.

    :param root: The root directory whose subdirs are to be zipped.
    """
    if isinstance(root, str):
        root = Path(root)
    for path in root.iterdir():
        if path.is_dir() and not path.name.startswith("."):
            file = path.with_suffix(".zip")
            print(f"{path} -> {file}")
            sp.run(f"zip -qr {file} {path} &", shell=True, check=True)


def flatten_dir(dir_: str | Path) -> None:
    """Flatten a directory,
    i.e., move files in immediate subdirectories into the current directory.

    :param dir_: The directory to flatten.
    """
    if isinstance(dir_, str):
        dir_ = Path(dir_)
    for path in dir_.iterdir():
        if path.is_dir():
            _flatten_dir(path)
            path.rmdir()


def _flatten_dir(dir_: Path) -> None:
    """Helper method of flatten_dir.

    :param dir_: A directory to flatten.
    """
    for path in dir_.iterdir():
        path.rename(path.parent.parent / path.name)


def split_dir(dir_: str | Path, batch_size: int, wildcard: str = "*") -> None:
    """Split files in a directory into sub-directories.
    This function is for the convenience of splitting a directory
    with a large number of files into smaller directories
    so that those subdirs can zipped (into relatively smaller files) and uploaded to cloud quickly.

    :param dir_: The root directory whose files are to be splitted into sub-directories.
    :param wildcard: A wild card pattern specifying files to be included.
    :param batch_size: The number files that each subdirs should contain.
    """
    if isinstance(dir_, str):
        dir_ = Path(dir_)
    files = sorted(dir_.glob(wildcard))
    num_batch = math.ceil(len(files) / batch_size)
    nchar = len(str(num_batch))
    for batch_idx in tqdm(range(num_batch)):
        _split_dir_1(dir_ / f"{batch_idx:0>{nchar}}", files, batch_idx, batch_size)


def _split_dir_1(
    desdir: Path, files: list[Path], batch_idx: int, batch_size: int
) -> None:
    """Helper method of split_dir.

    :param desdir: The destination directory to save subset of files.
    :param files: A list of Path objects.
    :param batch_idx: The batch index (0-based).
    :param batch_size: The size of the batch.
    """
    desdir.mkdir(exist_ok=True)
    for path in files[(batch_idx * batch_size) : ((batch_idx + 1) * batch_size)]:
        path.rename(desdir / path.name)


def find_images(root_dir: str | Path | list[str | Path]) -> list[Path]:
    """Find all PNG images in a (sequence) of dir(s) or its/their subdirs.

    :param root_dir: A (list) of dir(s).
    :return: A list of Path objects to PNG images.
    """
    if isinstance(root_dir, (str, Path)):
        root_dir = [root_dir]
    images = []
    for path in root_dir:
        if isinstance(path, str):
            path = Path(path)
        images.extend(path.glob("**.png"))
    return images


def find_data_tables(
    root: str | Path,
    filter_: Callable = lambda _: True,
    extensions: Iterable[str] = (),
    patterns: Iterable[str] = (),
) -> set[str]:
    """Find keywords which are likely data table names.

    :param root: The root directory or a GitHub repo URL in which to find data table names.
    :param filter_: A function for filtering identified keywords (via regular expressions).
        By default, all keywords identified by regular expressions are kept.
    :param extensions: Addtional text file extensions to use.
    :param patterns: Addtional regular expression patterns to use.
    :return: A set of names of data tables.
    """
    if isinstance(root, str):
        if re.search(r"(git@|https://).*\.git", root):
            with tempfile.TemporaryDirectory() as tempdir:
                dulwich.porcelain.clone(root, tempdir)
                logger.info(
                    "The repo {} is cloned to the local directory {}.", root, tempdir
                )
                return find_data_tables(tempdir, filter_=filter_)
        root = Path(root)
    if root.is_file():
        return _find_data_tables_file(root, filter_, patterns)
    extensions = {
        ".sql",
        ".py",
        ".ipy",
        ".ipynb",
        ".scala",
        ".java",
        ".txt",
        ".json",
    } | set(extensions)
    paths = (
        path
        for path in Path(root).glob("**/*")
        if path.suffix.lower() in extensions and path.is_file()
    )
    return set(
        chain.from_iterable(
            _find_data_tables_file(path, filter_, patterns) for path in paths
        )
    )


def _find_data_tables_file(file, filter_, patterns) -> set[str]:
    if isinstance(file, str):
        file = Path(file)
    text = file.read_text(encoding="utf-8").lower()
    patterns = {
        r"from\s+(\w+)\W*\s*",
        r"from\s+(\w+\.\w+)\W*\s*",
        r"join\s+(\w+)\W*\s*",
        r"join\s+(\w+\.\w+)\W*\s*",
        r"table\((\w+)\)",
        r"table\((\w+\.\w+)\)",
        r'"table":\s*"(\w+)"',
        r'"table":\s*"(\w+\.\w+)"',
    } | set(patterns)
    tables = chain.from_iterable(re.findall(pattern, text) for pattern in patterns)
    mapping = str.maketrans("", "", "'\"\\")
    tables = (table.translate(mapping) for table in tables)
    return set(table for table in tables if filter_(table))


def find_data_tables_sql(sql: str, filter_: Callable | None = None) -> set[str]:
    """Find keywords which are likely data table names in a SQL string.

    :param sql: A SQL query.
    :param filter_: A function for filtering identified keywords (via regular expressions).
        By default, all keywords identified by regular expressions are kept.
    :return: A set of names of data tables.
    """
    sql = sql.lower()
    pattern = r"(join|from)\s+(\w+(\.\w+)?)(\s|$)"
    tables = (pms[1] for pms in re.findall(pattern, sql))
    if filter_ is None:
        return set(tables)
    return set(table for table in tables if filter_(table))


def is_empty(dir_: str | Path, filter_: Callable | None = lambda _: True) -> bool:
    """Check whether a directory is empty.

    :param dir_: The directory to check.
    :param filter_: A filtering function (default True always) to limit the check to sub files/dirs.
    :return: True if the specified directory is empty and False otherwise.
    """
    if isinstance(dir_, str):
        dir_ = Path(dir_)
    paths = dir_.glob("**/*")
    return not any(True for path in paths if filter_(path))


def _ignore(path: Path) -> bool:
    path = path.resolve()
    if path.is_file() and path.name.startswith("."):
        return True
    if path.is_dir() and path.name in (
        ".jukit",
        ".ipynb_checkpoints",
        ".mypy_cache",
        ".pytest_cache",
        ".mtj.tmp",
        "__pycache__",
    ):
        return True
    return False


def remove_ess_empty(path: str | Path, ignore: Callable = _ignore) -> list[Path]:
    """Remove essentially empty directories under a path.

    :param path: The path to the directory to check.
    :param ignore: A bool function which returns True on files/directories to ignore.
    :return: A list of Path objects which failed to be removed.
    """
    fail = []
    for p in find_ess_empty(path, ignore=ignore):
        try:
            if p.is_file() or p.is_symlink():
                p.unlink()
            else:
                shutil.rmtree(p)
        except PermissionError:
            fail.append(p)
    return fail


def find_ess_empty(path: str | Path, ignore: Callable = _ignore) -> list[Path]:
    """Find essentially empty sub directories under a directory.

    :param path: The path to the directory to check.
    :param ignore: A bool function which returns True on files/directories to ignore.
    :return: A list of directories which are essentially empty.
    """
    if isinstance(path, str):
        path = Path(path)
    ess_empty = {}
    ess_empty_dir = []
    _find_ess_empty(
        path=path, ignore=ignore, ess_empty=ess_empty, ess_empty_dir=ess_empty_dir
    )
    return ess_empty_dir


def _find_ess_empty(
    path: Path, ignore: Callable, ess_empty: dict[Path, bool], ess_empty_dir: list[Path]
):
    if is_ess_empty(path=path, ignore=ignore, ess_empty=ess_empty):
        ess_empty_dir.append(path)
        return
    for p in path.iterdir():
        if p.is_dir():
            _find_ess_empty(
                path=p, ignore=ignore, ess_empty=ess_empty, ess_empty_dir=ess_empty_dir
            )


def is_ess_empty(
    path: Path, ignore: Callable = _ignore, ess_empty: dict[Path, bool] | None = None
):
    """Check if a directory is essentially empty.

    :param path: The path to the directory to check.
    :param ignore: A bool function which returns True on files/directories to ignore.
    :param ess_empty: A dictionary caching essentially empty paths.
    :raises FileNotFoundError: If the given path does not exist.
    :return: True if the directory is essentially empty and False otherwise.
    """
    if isinstance(path, str):
        path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"The file {path} does not exist!")
    if not os.access(path, os.R_OK):
        return False
    if path.is_symlink():
        return True
    path = path.resolve()
    if ess_empty is None:
        ess_empty = {}
    if path in ess_empty:
        return ess_empty[path]
    if ignore(path):
        return True
    for p in path.iterdir():
        if ignore(p):
            continue
        if p.is_file():
            return False
        if not is_ess_empty(p, ignore=ignore, ess_empty=ess_empty):
            ess_empty[path] = False
            return False
    ess_empty[path] = True
    return True


def append_lines(
    path: Path,
    lines: str | Iterable[str],
    exist_skip: bool = True,
) -> None:
    """Update a text file using regular expression substitution.

    :param path: A Path object to the file to be updated.
    :param lines: A (list of) line(s) to append.
        Note that "\\n" is automatically added to the end of each line to append.
    :param exist_skip: Skip if lines to append already exists in the file.
    """
    if isinstance(path, str):
        path = Path(path)
    text = path.read_text(encoding="utf-8")
    if not isinstance(lines, str):
        lines = "\n".join(lines)
    if not exist_skip or lines not in text:
        text += lines
    path.write_text(text, encoding="utf-8")


def replace_patterns(
    path: Path,
    pattern: str | Iterable[str],
    repl: str | Iterable[str],
    regex: bool = True,
) -> None:
    """Update a text file by replacing patterns with specified substitutions.

    :param path: A Path object to the file to be updated.
    :param pattern: A (list of) patterns to replace.
    :param repl: A (list of) replacements.
        or a function to map patterns to replacements.
    :param regex: If true, treat patterns as regular expression pattern;
        otherwise, perform exact matches.
    """
    if isinstance(path, str):
        path = Path(path)
    text = path.read_text(encoding="utf-8")
    if isinstance(pattern, str):
        pattern = [pattern]
    if isinstance(repl, str):
        repl = [repl]
    if regex:
        for p, r in zip(pattern, repl):
            text = re.sub(p, r, text)
    else:
        for p, r in zip(pattern, repl):
            text = text.replace(p, r)
    path.write_text(text, encoding="utf-8")


def get_files(dir_: str | Path, exts: str | list[str]) -> Iterable[Path]:
    """Get files with the specified file extensions.

    :param dir_: The path to a directory.
    :param exts: A (list of) file extensions (e.g., .txt).
    :yield: A generator of Path objects.
    """
    if isinstance(dir_, str):
        dir_ = Path(dir_)
    if isinstance(exts, str):
        exts = [exts]
    yield from _get_files(dir_, exts)


def _get_files(dir_: Path, exts: list[str]) -> Iterable[Path]:
    for path in dir_.iterdir():
        if path.is_file():
            if path.suffix.lower() in exts:
                yield path
        else:
            yield from _get_files(path, exts)


def has_header(
    files: str | Path | list[str | Path], num_files_checking: int = 5
) -> bool:
    """Check whether the files have headers.

    :param files: the list of files to check.
    :param num_files_checking: the number of non-empty files to use to decide whether there are header lines.
    :return: True if the files have headers and False otherwise.
    """
    # i: file index
    for i in range(len(files)):
        with open(files[i], "r", encoding="utf-8") as fin:
            first_line = fin.readline()
            if first_line:
                possible_header = first_line
                break
    # k: current number of non-empty files
    k = 1
    for j in range(i, len(files)):
        if k >= num_files_checking:
            break
        with open(files[j], "r", encoding="utf-8") as fin:
            first_line = fin.readline()
            if first_line:
                k += 1
                if first_line != possible_header:
                    return False
    return True


def _merge_with_headers(
    files: str | Path | list[str | Path], output: str | Path = ""
) -> None:
    """Merge files with headers. Keep only one header.

    :param files: A list of files
        or the path to a directory containing a list of files to merge.
    :param output: output files for merging the files.
    """
    with open(output, "wb") if output else sys.stdout.buffer as out:
        with open(files[0], "rb") as fin0:
            for line in fin0:
                out.write(line)
        for file in files[1:]:
            with open(file, "rb") as fin:
                fin.readline()
                for line in fin:
                    out.write(line)


def _merge_without_header(
    files: str | Path | list[str | Path], output: str | Path = ""
) -> None:
    """Merge files without header.

    :param files: A list of files
        or the path to a directory containing a list of files to merge.
    :param output: output files for merging the files.
    """
    with open(output, "wb") if output else sys.stdout.buffer as fout:
        for file in files:
            with open(file, "rb") as fin:
                for line in fin:
                    fout.write(line)
                fout.write(b"\n")


def merge(
    files: str | Path | list[str | Path],
    output: str = "",
    num_files_checking: int = 5,
) -> None:
    """Merge files. If there are headers in files, keep only one header in the single merged file.

    :param files: A list of files
        or the path to a directory containing a list of files to merge.
    :param output: output files for merging the files.
    :param num_files_checking: number of files for checking whether there are headers in files.
    """
    if isinstance(files, str):
        files = Path(files)
    if isinstance(files, Path):
        files = list(files.iterdir())
    if num_files_checking <= 0:
        num_files_checking = 5
    num_files_checking = min(num_files_checking, len(files))
    if has_header(files, num_files_checking):
        _merge_with_headers(files, output)
        return
    _merge_without_header(files, output)


def dedup_header(file: str | Path, output: str | Path = "") -> None:
    """Dedup headers in a file (due to the hadoop getmerge command).
    Only the header on the first line is kept and headers (identical line to the first line)
    on other lines are removed.

    :param file: The path to the file to be deduplicated.
    :param output: The path of the output file.
        If empty, then output to the standard output.
    """
    with (
        open(file, "rb") as fin,
        open(output, "wb") if output else sys.stdout.buffer as fout,
    ):
        header = fin.readline()
        fout.write(header)
        for line in fin:
            if line != header:
                fout.write(line)


def select(
    path: str | Path,
    columns: str | list[str],
    delimiter: str,
    output: str = "",
):
    """Select fields by name from a delimited file (not necessarily well structured).

    :param path: To path to a file (containing delimited values in each row).
    :param columns: A list of columns to extract from the file.
    :param delimiter: The delimiter of fields.
    :param output: The path of the output file.
        If empty, then output to the standard output.
    """
    if isinstance(path, str):
        path = Path(path)
    if isinstance(columns, str):
        columns = [columns]
    with path.open("r", encoding="utf-8") as fin:
        header = fin.readline().split(delimiter)
        index = []
        columns_full = []
        for idx, field in enumerate(header):
            if field in columns:
                index.append(idx)
                columns_full.append(field)
        with open(output, "w", encoding="utf-8") if output else sys.stdout as fout:
            fout.write(delimiter.join(columns_full) + "\n")
            for line in fin:
                fields = line.split(delimiter)
                fout.write(delimiter.join([fields[idx] for idx in index]) + "\n")


def prune_json(input: str | Path, output: str | Path = ""):
    """Prune fields (value_counts) from a JSON file.

    :param input: The path to a JSON file to be pruned.
    :param output: The path to output the pruned JSON file.
    """
    logger.info("Pruning the JSON fiel at {}...", input)
    if isinstance(input, str):
        input = Path(input)
    if isinstance(output, str):
        if output:
            output = Path(output)
        else:
            output = input.with_name(input.stem + "_prune.json")
    skip = False
    with (
        input.open("r", encoding="utf-8") as fin,
        output.open("w", encoding="utf-8") as fout,
    ):
        for line in fin:
            line = line.strip()
            if line == '"value_counts": {':
                skip = True
                continue
            if skip:
                if line in ("}", "},"):
                    skip = False
            else:
                fout.write(line)
    logger.info("The pruned JSON file is written to {}.", output)


def _filter_num(path: str | Path, pattern: str, num_lines: int):
    if isinstance(path, str):
        path = Path(path)
    results = []
    res = []
    count = 0
    for line in path.open(encoding="utf-8"):
        if count > 0:
            res.append(line)
            count -= 1
            continue
        if re.search(pattern, line):
            if res:
                results.append(res)
            res = []
            res.append(line)
            count = num_lines
    if res:
        results.append(res)
    return results


def _filter_sp(path: str | Path, pattern: str, sub_pattern: str):
    if isinstance(path, str):
        path = Path(path)
    results = []
    res = []
    sub = False
    for line in path.open(encoding="utf-8"):
        if sub:
            if re.search(sub_pattern, line):
                res.append(line)
            else:
                sub = False
        if re.search(pattern, line):
            if res:
                results.append(res)
            res = []
            res.append(line)
            sub = True
    if res:
        results.append(res)
    return results


def filter(
    path: str | Path, pattern: str, sub_pattern: str = "", num_lines: int = 0
) -> list[list[str]]:
    """Filter lines from a file.
    A main regex pattern is used to identify main rows.
    For each matched main row,
    a sub regex pattern or a fixed number of lines can be provided.
    If a sub regex pattern is provided,
    then lines matching the sub regex pattern following a main line are kept together with the main line.
    If a fixed number of lines is provided, e.g., ``num_lines=k``,
    then ``k`` additional lines after a main line are kept together with the main line.

    :param path: Path to a text file from which to filter lines.
    :param pattern: The main regex pattern.
    :param sub_pattern: The sub regex pattern (defaults to "", i.e., no sub pattern by default).
    :param num_lines: The num of additional lines (0 by default) to keep after a main line.
    :return: A list of list of lines.
    """
    if sub_pattern:
        return _filter_sp(path, pattern=pattern, sub_pattern=sub_pattern)
    return _filter_num(path, pattern=pattern, num_lines=num_lines)


def trace_dir_upwards(path: str | Path, name: str) -> PosixPathPair:
    """Find the parent directory with the specified name.

    Args:
        path: A local path contains `/name/`.
        name: The base name (stem) of the parent directory.

    Returns:
        A PosixPathPair which contains the parent directory
        and the relative path to this parent directory.
    """

    def _trace_dir_upwards(path: Path) -> Path:
        while (stem := path.stem) != name:
            if not stem:
                raise ValueError(f"The path {path} does not contain /{name}/!")
            path = path.parent
        return path

    if isinstance(path, str):
        path = Path(path)
    prefix = _trace_dir_upwards(path)
    return PosixPathPair(prefix, path.relative_to(prefix))
