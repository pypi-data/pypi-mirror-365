"""Binary runner and results classes."""

from __future__ import annotations

import enum
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from excitingtools.base import ECTObject


class RunnerCode(enum.Enum):
    """Runner codes.
    By default, the initial value starts at 1.
    """

    time_out = enum.auto()


@dataclass
class SubprocessRunResults:
    """Results returned from subprocess.run()"""

    stdout: str
    stderr: str
    return_code: int | RunnerCode
    process_time: Optional[float] = None

    @property
    def success(self) -> bool:
        """Determine the run success by evaluating the return code."""
        return self.return_code == 0


class BinaryRunner(ECTObject):
    """Class to execute a subprocess."""

    path_type = Union[str, Path]

    def __init__(
        self,
        binary: path_type,
        run_cmd: List[str] | str = "",
        omp_num_threads: int = 1,
        time_out: int = 60,
        directory: path_type = "./",
        args: Optional[List[str]] = None,
    ):
        """Initialise class.

        :param str binary: Binary name prepended by full path, or just binary name (if present in $PATH).
         No check for existence here as it could live on a remote worker (see run() doc)
        :param Union[List[str], str] run_cmd: Run commands sequentially as a list. For example:
          * For serial: []
          * For MPI:   ['mpirun', '-np', '2']
        or as a string. For example"
          * For serial: ""
          * For MPI: "mpirun -np 2"
        :param omp_num_threads: Number of OMP threads.
        :param time_out: Number of seconds before a job is defined to have timed out.
        :param args: Optional arguments for the binary.
        """
        self.binary = Path(binary).as_posix()
        self.directory = Path(directory).as_posix()
        self.run_cmd = run_cmd
        self.omp_num_threads = omp_num_threads
        self.time_out = time_out
        self.args = args or []

        if isinstance(run_cmd, str):
            self.run_cmd = run_cmd.split()
        elif not isinstance(run_cmd, list):
            raise ValueError("Run commands expected in a str or list. For example ['mpirun', '-np', '2']")

        self._check_mpi_processes()

        if omp_num_threads <= 0:
            raise ValueError("Number of OMP threads must be > 0")

        if time_out <= 0:
            raise ValueError("time_out must be a positive integer")

    def _check_mpi_processes(self):
        """Check whether mpi is specified and if yes that the number of MPI processes specified is valid."""
        # Search if MPI is specified:
        try:
            i = self.run_cmd.index("-np")
        except ValueError:
            # .index will return ValueError if 'np' not found. This corresponds to serial and omp calculations.
            return
        try:
            mpi_processes = int(self.run_cmd[i + 1])
        except IndexError:
            raise ValueError("Number of MPI processes must be specified after the '-np'")
        except ValueError:
            raise ValueError("Number of MPI processes should be an int")
        if mpi_processes <= 0:
            raise ValueError("Number of MPI processes must be > 0")

    def get_execution_list_and_env(self) -> Tuple[List[str], Dict[str, str]]:
        """Prepares the execution list and the environment for running the binary.

        :return: the execution list and the environment dictionary for use with subprocess.run(...) or
        subprocess.Popen(...).
        """
        binary = Path(self.binary)
        if not binary.is_file():
            binary = shutil.which(self.binary)
            if not binary:
                raise FileNotFoundError(f"{self.binary} binary is not present in the current directory nor in $PATH")

        if not Path(self.directory).is_dir():
            raise OSError(f"Run directory does not exist: {self.directory}")

        execution_list = self.run_cmd + [Path(binary).as_posix()] + self.args
        my_env = {**os.environ, "OMP_NUM_THREADS": str(self.omp_num_threads)}
        return execution_list, my_env

    def run(self) -> SubprocessRunResults:
        """Run a binary.

        First check for the binary and the run directory. Binary can be relative or absolute path to the
        binary file. Alternatively, the binary name could exist at a different location, therefore check $PATH.

        Then executes the binary with given run command and args.
        Special handling is performed if the execution reached the time limit.

        :return: the run results with output and error message, runner code and run time
        """
        execution_list, my_env = self.get_execution_list_and_env()

        time_start: float = time.time()
        try:
            result = subprocess.run(
                execution_list,
                cwd=self.directory,
                env=my_env,
                capture_output=True,
                encoding="utf-8",
                timeout=self.time_out,
                check=False,
            )
            total_time = time.time() - time_start
            return SubprocessRunResults(result.stdout, result.stderr, result.returncode, total_time)

        except subprocess.TimeoutExpired as timed_out:
            output = timed_out.output.decode("utf-8") if timed_out.output else ""
            error = "BinaryRunner: Job timed out. \n\n"
            if timed_out.stderr:
                error += timed_out.stderr.decode("utf-8")
            return SubprocessRunResults(output, error, RunnerCode.time_out, self.time_out)
