"""Wrapping HDFS commands."""

from pathlib import Path
import subprocess as sp
import pandas as pd
from loguru import logger
from ..shell import to_frame
from ..filesystem import count_path


class Hdfs:
    """A class abstring the hdfs command."""

    def __init__(self, bin: str = "/apache/hadoop/bin/hdfs"):
        self._bin = bin

    def ls(
        self, path: str, dir_only: bool = False, recursive: bool = False
    ) -> pd.DataFrame:
        """Return the results of hdfs dfs -ls /hdfs/path as a DataFrame.

        :param path: A HDFS path.
        :param dir_only: If true, list directories only.
        :param recursive: If True, list content of the HDFS path recursively.
        :return: The result of hdfs dfs -ls as a pandas DataFrame.
        """
        cols = [
            "permissions",
            "replicas",
            "userid",
            "groupid",
            "bytes",
            "mdate",
            "mtime",
            "path",
        ]
        cmd = f"{self._bin} dfs -ls "
        if dir_only:
            cmd += "-d "
        if recursive:
            cmd += "-R "
        cmd += path
        logger.info("Running command: {}. Might take a while.", cmd)
        frame = to_frame(cmd, split=r" +", skip=() if dir_only else [0], header=cols)
        frame.bytes = frame.bytes.astype(int)
        frame.mtime = pd.to_datetime(frame.mdate + " " + frame.mtime)
        frame.drop("mdate", axis=1, inplace=True)
        return frame

    def count(self, path: str) -> pd.DataFrame:
        """Return the results of hdfs dfs -count -q -v /hdfs/path as a DataFrame.

        :param path: A HDFS path.
        :return: The result of hdfs dfs -count as a pandas DataFrame.
        """
        cmd = f"{self._bin} dfs -count -q -v {path}"
        logger.info("Running command: {}. Might take a while.", cmd)
        frame = to_frame(cmd, split=r" +", header=0)
        frame.columns = frame.columns.str.lower()
        return frame

    def du(self, path: str, depth: int = 1) -> pd.DataFrame:
        """Get the size of HDFS paths.

        :param path: A HDFS path.
        :param depth: The depth (by default 1) of paths to calculate sizes for.
            Note that any depth less than 1 is treated as 1.
        :return: Disk usage of the HDFS path as a pandas DataFrame.
        """
        index = len(path.rstrip("/"))
        if depth > 1:
            paths = self.ls(path, recursive=True).path
            frames = [
                self._du_helper(path)
                for path in paths
                if path[index:].count("/") + 1 == depth
            ]
            return pd.concat(frames, ignore_index=True)
        return self._du_helper(path)

    def _du_helper(self, path: str) -> pd.DataFrame:
        cmd = f"{self._bin} dfs -du {path}"
        logger.info("Running command: {}. Might take a while.", cmd)
        frame = to_frame(cmd, split=r" +", header=["bytes", "path"])
        frame.bytes = frame.bytes.astype(int)
        return frame

    def exists(self, path: str) -> bool:
        """Check if a HDFS path exist.

        :param path: A HDFS path.
        :return: True if the HDFS path exists and False otherwise.
        """
        cmd = f"{self._bin} dfs -test -e {path}"
        logger.info("Running command: {}. Might take a while.", cmd)
        try:
            sp.run(cmd, shell=True, check=True)
            return True
        except sp.CalledProcessError:
            return False

    def remove(self, path: str) -> None:
        """Remove a HDFS path.
        :param path: A HDFS path.
        """
        cmd = f"{self._bin} dfs -rm -r {path}"
        logger.info("Running command: {}. Might take a while.", cmd)
        sp.run(cmd, shell=True, check=True)

    def num_partitions(self, path: str) -> int:
        """Get the number of partitions of a HDFS path.

        :param path: A HDFS path.
        :return: The number of partitions under the HDFS path.
        """
        cmd = f"{self._bin} dfs -ls {path}/part-* | wc -l"
        logger.info("Running command: {}. Might take a while.", cmd)
        return int(sp.check_output(cmd, shell=True))

    def get(
        self, hdfs_path: str, local_dir: str | Path = "", is_file: bool = False
    ) -> None:
        """Download data from HDFS into a local directory.

        :param hdfs_path: The HDFS path (can be both a file or a directory) to copy.
        :param local_dir: The local directory to copy HDFS files into.
        :param is_file: A boolean indicator of whether the HDFS path is a file or a directory.
        """
        if isinstance(local_dir, str):
            local_dir = Path(local_dir)
        local_dir.mkdir(parents=True, exist_ok=True)
        if is_file:
            cmd = f"{self._bin} dfs -get {hdfs_path} {local_dir}"
        else:
            cmd = f"{self._bin} dfs -get {hdfs_path}/* {local_dir}"
        logger.info("Running command: {}. Might take a while.", cmd)
        sp.run(cmd, shell=True, check=True)
        print(
            f"Content of the HDFS path {hdfs_path} has been fetch into the local directory {local_dir}"
        )

    def count_path(self, path: str) -> pd.Series:
        """Count frequence of paths and their parent paths.

        :param path: An iterable collection of paths.
        :return: Frequency of paths as a pandas Series.
        """
        frame = self.ls(path, recursive=True)
        return count_path(frame.path)

    def mkdir(self, path: str) -> None:
        """Create a HDFS path.

        :param path: The HDFS path to create.
        """
        cmd = f"{self._bin} dfs -mkdir -p {path}"
        logger.info("Running command: {}. Might take a while.", cmd)
        sp.run(cmd, shell=True, check=True)
        logger.info(f"The HDFS path {path} has been created.")

    def put(
        self,
        local_path: str | Path,
        hdfs_path: str,
        create_hdfs_path: bool = False,
    ) -> None:
        """Copy data from local to HDFS.
        :param local_path: A local path to copy to HDFS.
        :param hdfs_path: The HDFS path/directory to copy data into.
        :param create_hdfs_path: If true, create the HDFS path if not exists.
        """
        if create_hdfs_path:
            self.mkdir(hdfs_path)
        cmd = f"{self._bin} dfs -put -f {local_path} {hdfs_path}"
        logger.info("Running command: {}. Might take a while.", cmd)
        sp.run(cmd, shell=True, check=True)
        logger.info(
            f"The local path {local_path} has been uploaded into the HDFS path {hdfs_path}"
        )

    def fetch_partition_names(
        self, path: str, extension: str = ".parquet"
    ) -> list[str]:
        """Get Parquet partition names (with the parent directory) under a HDFS path.

        :param path: A HDFS path.
        :param extension: Return partitions with the specified file extension.
        :return: A list of the partition names (with the parent directory).
        """
        paths = self.ls(path).path
        return [path for path in paths if path.endswith(extension)]

    def rm(self, path: str, recursive: bool = True, skip_trash: bool = False) -> bool:
        """Remove a HDFS path.

        :param path: A HDFS path to remove.
        :param recursive: If true, use the option -r.
        :param skip_trash: If true, use the option -skipTrash.
        :return: True if the path is removed successfully and false otherwise.
        """
        flag_skip_trash = "-skipTrash" if skip_trash else ""
        flag_recursive = "-r" if recursive else ""
        cmd = f"{self._bin} dfs -rm {flag_recursive} {flag_skip_trash} {path}"
        logger.info("Running command: {}. Might take a while.", cmd)
        proc = sp.run(cmd, shell=True)  # pylint: disable=W1510
        return proc.returncode == 0

    def rm_robust(
        self, path: str, skip_trash: bool = False, user: str = ""
    ) -> list[str]:
        """Remove a HDFS path in a robust way.
            If removing a directory fails,
            the method continues to remove its subfiles and subdirs
            insteadd of throwing an exception.

        :param path: A HDFS path to remove.
        :param skip_trash: If true, use the option -skipTrash.
        :param user: If specified, remove only paths belong to the user.
        :return: A list of HDFS paths that are successfully removed.
        """
        if user:
            frame = self.ls(path, dir_only=True)
            frame = frame[frame.userid == user]
            if frame.empty:
                return []
        if self.rm(path, recursive=True, skip_trash=skip_trash):
            return [path]
        frame = self.ls(path)
        if user:
            frame = frame[frame.userid == user]
        paths_removed = []
        # remove files
        for file in frame[~frame.permissions.str.startswith("d")].path:
            if self.rm(file, skip_trash=skip_trash):
                paths_removed.append(file)
        for p in frame[frame.permissions.str.startswith("d")].path:
            paths_removed.extend(self.rm_robust(p, skip_trash=skip_trash, user=user))
        return paths_removed
