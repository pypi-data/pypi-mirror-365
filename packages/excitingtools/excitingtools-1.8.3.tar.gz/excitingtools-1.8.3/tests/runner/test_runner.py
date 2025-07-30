"""Tests for the binary runner."""

import importlib
import shutil
from pathlib import Path
from typing import Any
from unittest import mock

import pytest

import excitingtools.base
from excitingtools.runner.runner import BinaryRunner

mock_binary = "false_exciting_binary"


@pytest.mark.xfail(shutil.which(mock_binary) is not None, reason="Binary name exists.")
def test_no_binary():
    my_runner = BinaryRunner(mock_binary, "./", 1, 1)
    with pytest.raises(
        FileNotFoundError, match=rf"{mock_binary} binary is not present in the current directory nor in \$PATH"
    ):
        my_runner.run()


@pytest.fixture
def exciting_smp(tmp_path: Path) -> str:
    binary = tmp_path / "exciting_smp"
    binary.touch()
    return binary.as_posix()


def test_no_run_dir(exciting_smp: str):
    my_runner = BinaryRunner(exciting_smp, "./", 1, 1, "non_existent_dir")
    with pytest.raises(OSError, match="Run directory does not exist: non_existent_dir"):
        my_runner.run()


def test_false_run_cmd(exciting_smp: str):
    false_run_cmd: Any = 3
    with pytest.raises(ValueError, match="Run commands expected in a str or list. For example ['mpirun', '-np', '2']"):
        BinaryRunner(exciting_smp, false_run_cmd, 1, 1)


@pytest.fixture
def exciting_mpismp(tmp_path: Path) -> str:
    binary = tmp_path / "exciting_mpismp"
    binary.touch()
    return binary.as_posix()


def test_false_mpi_command_smaller_than_zero(exciting_mpismp: str):
    with pytest.raises(ValueError, match="Number of MPI processes must be > 0"):
        BinaryRunner(exciting_mpismp, ["mpirun", "-np", "-1"], 1, 1)


def test_false_mpi_command_no_int(exciting_mpismp: str):
    with pytest.raises(ValueError, match="Number of MPI processes should be an int"):
        BinaryRunner(exciting_mpismp, ["mpirun", "-np", "no_int"], 1, 1)


def test_false_mpi_command_no_number_given(exciting_mpismp: str):
    with pytest.raises(ValueError, match="Number of MPI processes must be specified after the '-np'"):
        BinaryRunner(exciting_mpismp, ["mpirun", "-np"], 1, 1)


def test_false_omp(exciting_smp: str):
    with pytest.raises(ValueError, match="Number of OMP threads must be > 0"):
        BinaryRunner(exciting_smp, [""], -1, 1)


def test_false_timeout(exciting_smp: str):
    with pytest.raises(ValueError, match="time_out must be a positive integer"):
        BinaryRunner(exciting_smp, [""], 1, -1)


@pytest.fixture
def runner(tmp_path: Path, exciting_mpismp: str) -> BinaryRunner:
    """Produces a runner with binary and run dir mocked up."""
    run_dir = tmp_path / "ab/de"
    run_dir.mkdir(parents=True)
    return BinaryRunner(exciting_mpismp, ["mpirun", "-np", "3"], 4, 260, run_dir.as_posix(), [">", "std.out"])


def test_as_dict_jobflow(tmp_path: Path, runner: BinaryRunner):
    pytest.importorskip("monty", reason="Serialisation requires monty.")
    assert runner.as_dict() == {
        "@class": "BinaryRunner",
        "@module": "excitingtools.runner.runner",
        "@version": excitingtools.__version__,
        "args": [">", "std.out"],
        "binary": (tmp_path / "exciting_mpismp").as_posix(),
        "directory": (tmp_path / "ab/de").as_posix(),
        "omp_num_threads": 4,
        "run_cmd": ["mpirun", "-np", "3"],
        "time_out": 260,
    }


def test_from_dict(tmp_path: Path, runner):
    pytest.importorskip("monty", reason="Serialisation requires monty.")
    new_runner = BinaryRunner.from_dict(runner.as_dict())
    assert new_runner.binary == (tmp_path / "exciting_mpismp").as_posix()
    assert new_runner.time_out == 260


def test_runner_without_monty():
    with mock.patch("importlib.util.find_spec", return_value=None):
        importlib.reload(excitingtools.base.serialisation)
        importlib.reload(excitingtools.base)  # as it comes from the __init__
        new_runner_module = importlib.reload(excitingtools.runner.runner)

    my_runner = new_runner_module.BinaryRunner("abc")
    assert not hasattr(my_runner, "as_dict")  # Should not be an MSONable


def test_runner_explicitly_no_monty(monkeypatch):
    pytest.importorskip("monty", reason="Serialisation requires monty.")
    monkeypatch.setenv("USE_MONTY", "false")

    importlib.reload(excitingtools.base.serialisation)  # reload as the env var has changed
    importlib.reload(excitingtools.base)  # as it comes from the __init__
    new_runner_module = importlib.reload(excitingtools.runner.runner)

    my_runner = new_runner_module.BinaryRunner("abc")
    assert not hasattr(my_runner, "as_dict")  # Should not be an MSONable


def test_run_with_bash_command(tmp_path: Path):
    """Produces a runner with binary and run dir mocked up.
    Test a simple echo command.
    """
    run_dir = tmp_path / "ab/de"
    run_dir.mkdir(parents=True)
    binary = tmp_path / "hello"
    binary.touch()
    runner = BinaryRunner(binary.as_posix(), ["echo"], 1, 60, run_dir.as_posix())
    run_results = runner.run()
    assert run_results.success
    assert run_results.stderr == ""
    assert run_results.stdout == binary.as_posix() + "\n"


def test_timeout_with_bash_command(tmp_path: Path):
    """Produces a runner with binary and run dir mocked up.

    Test a simple sleep command to get a timeout.
    """
    from excitingtools.runner.runner import RunnerCode  # needed as the runner was reloaded
    # the mocking from the other test clashes with that test here, since the runner module was reloaded and
    # the isinstance check fails. I don't fully understand how and if the original imported BinaryRunner
    # changes upon mocking that was imported at the top of the file

    time_out = 1
    binary = tmp_path / "sleep.sh"
    binary.write_text(f"sleep {time_out + 0.1}")
    runner = BinaryRunner(binary.as_posix(), ["sh"], 1, time_out, tmp_path.as_posix())
    run_results = runner.run()
    assert not run_results.success
    assert run_results.stderr == "BinaryRunner: Job timed out. \n\n"
    assert run_results.stdout == ""
    assert run_results.process_time == time_out
    assert isinstance(run_results.return_code, RunnerCode)
    assert run_results.return_code == RunnerCode.time_out
