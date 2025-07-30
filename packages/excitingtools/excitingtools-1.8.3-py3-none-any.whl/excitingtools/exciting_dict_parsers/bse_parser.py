"""Parsers for BSE output files."""

import re
from pathlib import Path
from typing import Optional, Union

import numpy as np

path_type = Union[Path, str]


def numpy_gen_from_txt(name: path_type, skip_header: Optional[int] = 0) -> np.ndarray:
    """Numpy genfromtxt, dressed in try/expect.

    Not worth generalising, as would need to support genfromtxt's API.

    :param name: File name.
    :param skip_header: Optional number of header lines to skip.
    :return data: Parsed data.
    """
    try:
        data = np.genfromtxt(name, skip_header=skip_header)
    except ValueError:
        raise ValueError(f"Failed to parse {name}")
    return data


def parse_EPSILON_NAR(name: path_type) -> dict:
    """Parser for:
    EPSILON_NAR_BSE-singlet-TDA-BAR_SCR-full_OC.OUT.xml,
    EPSILON_NAR_FXCMB1_OC_QMT001.OUT.xml,
    EPSILON_NAR_NLF_FXCMB1_OC_QMT001.OUT.xml,
    LOSS_NAR_FXCMB1_OC_QMT001.OUT.xml
    """
    data = numpy_gen_from_txt(name, skip_header=14)
    out = {
        "frequency": data[:, 0],
        "real_oscillator_strength": data[:, 1],
        "imag_oscillator_strength": data[:, 2],
        "real_oscillator_strength_kkt": data[:, 3],
    }
    return out


def parse_LOSS_NAR(name: path_type):
    """Parser for:
    LOSS_NAR_FXCMB1_OC_QMT001.OUT.xml,
    LOSS_NAR_NLF_FXCMB1_OC_QMT001.OUT.xml
    """
    data = numpy_gen_from_txt(name, skip_header=14)
    out = {"frequency": data[:, 0], "real_oscillator_strength": data[:, 1], "imag_oscillator_strength": data[:, 2]}

    return out


def parse_EXCITON_NAR_BSE(name: path_type):
    """Parser for EXCITON_NAR_BSE-singlet-TDA-BAR_SCR-full_OC.OUT"""
    data = numpy_gen_from_txt(name, skip_header=14)
    out = {}
    out["state"] = data[:, 0]
    out["energy"] = data[:, 1]
    out["energy_shifted"] = data[:, 2]
    out["abs_oscillator_strength"] = data[:, 3]
    out["real_oscillator_strength"] = data[:, 4]
    out["imaginary_oscillator_strength"] = data[:, 5]

    return out


def parse_infoxs_out(name: path_type, parse_timing: bool = False) -> dict:
    """
    Parser for INFOXS.OUT file. Parses only the started and stopped tasks.
    Searches for lines like:
        'EXCITING <version> started for task <taskname> (<tasknumber>)'
    and
        'EXCITING <version> stopped for task <tasknumber>'
    See example file: exciting/test/test_farm/BSE/PBE_SOL-LiF/ref/INFOXS.OUT
    If a started task is found, it gets stored with name, number and status.
    If the task is found to be finished afterward, the status finished is set to True.

    For success, the last started tasks has to be finished after that (in the file).
    Last finished task is the last task if calculation was successful, the first task before
    that which finshed (in reversed order), else None if no task finished.
    :param name: path of the file to parse
    :param parse_timing: parse also timing information for the tasks. By default this is set to
                         False. If the task has not finished None is returned as timing.
    :returns: dictionary containing parsed file
    """
    with open(name) as file:
        lines = file.readlines()

    tasks = []
    current_task = -1

    lines = "\n".join(lines)
    all_tasks = re.findall(
        r"EXCITING .* (started) for task (.*) \( ?(\d+)\)|EXCITING .* stopped for task .* (\d+)", lines
    )
    last_finished_task = None

    for task in all_tasks:
        if task[0] == "started":
            tasks.append({"name": task[1], "number": int(task[2]), "finished": False})
            current_task += 1
        else:
            # asserts shouldn't happen with Exciting:
            assert tasks, "No tasks started!"
            assert tasks[current_task]["number"] == int(task[3]), "Wrong task stopped."
            tasks[current_task]["finished"] = True
            last_finished_task = tasks[current_task]["name"]

    success = tasks[-1]["finished"]

    if parse_timing:
        times = parse_times(lines)
        finished_tasks = [task for task in tasks if task["finished"]]
        assert len(times["cpu_time"]) == len(finished_tasks), (
            "Numbers of finished tasks and parsed times are not the same."
        )

        for index, task in enumerate(finished_tasks):
            for key in times:
                task[key] = float(times[key][index])

    return {"tasks": tasks, "success": success, "last_finished_task": last_finished_task}


def parse_times(infoxs_string: str) -> dict:
    """Parse the run times in INFOXS.OUT for each task.
    :param infoxs_string: String that contains the INFOXS.OUT file.
    :returns: dictionary containing a list of run times for each measurement.
    """
    cpu_times = re.findall(r"CPU time \s*: ([\d\.\d]+) sec", infoxs_string)
    wall_times = re.findall(r"wall time \s*: ([\d\.\d]+) sec", infoxs_string)
    cpu_times_cum = re.findall(r"CPU time \s* \(cumulative\) \s*: ([\d\.\d]+) sec", infoxs_string)
    wall_times_cum = re.findall(r"wall time \(cumulative\) \s*: ([\d\.\d]+) sec", infoxs_string)

    assert len(cpu_times) == len(wall_times), "Numbers of parsed timings are not consistent."
    assert len(cpu_times) == len(cpu_times_cum), "Numbers of parsed timings are not consistent."
    parsed_times = {"cpu_time": cpu_times, "wall_time": wall_times, "cpu_time_cum": cpu_times_cum}
    if not wall_times_cum:
        return parsed_times

    assert len(cpu_times) == len(wall_times_cum), "Numbers of parsed timings are not consistent."
    return {**parsed_times, "wall_time_cum": wall_times_cum}


def parse_fastBSE_absorption_spectrum_out(name: path_type) -> dict:
    """Parser for fastBSE_absorption_spectrum.out file.

    :param name: path of the file to parse
    :returns: dictionary containing parsed file
    """

    n_lines_description = 6
    description = ""
    with open(name) as file:
        for _ in range(n_lines_description):
            description += file.readline()

    try:
        energy_unit = float(re.findall(r"# Energy unit:\s*(.*) *Hartree", description)[0])
    except IndexError:
        raise RuntimeError("Could match regular expression for energy unit. Has the file header changed?")

    try:
        broadening = float(re.findall(r"# Broadening:\s*(.*) energy unit", description)[0])
    except IndexError:
        raise RuntimeError("Could match regular expression for broadening. Has the file header changed?")

    data = numpy_gen_from_txt(name, n_lines_description)

    return {"energy_unit": energy_unit, "broadening": broadening, "frequency": data[:, 0], "imag_epsilon": data[:, 1:4]}


def parse_fastBSE_exciton_energies_out(name: path_type) -> dict:
    """Parser for fastBSE_exciton_energies.out and fastBSE_gauss_quadrature_energies.out files.

    :param name: path of the file to parse
    :returns: dictionary containing parsed file
    """

    n_lines_description = 8
    description = ""
    with open(name) as file:
        for _ in range(n_lines_description):
            description += file.readline()

    try:
        energy_unit = float(re.findall(r"# Energy unit:\s*(.*) *Hartree", description)[0])
    except IndexError:
        raise RuntimeError("Could match regular expression for energy unit. Has the file header changed?")

    try:
        ip_band_gap = float(re.findall(r"# IP band gap:\s*(.*) energy unit", description)[0])
    except IndexError:
        raise RuntimeError("Could match regular expression for ip band gap. Has the file header changed?")

    return {
        "energy_unit": energy_unit,
        "ip_band_gap": ip_band_gap,
        "exciton_energies": numpy_gen_from_txt(name, n_lines_description),
    }


def parse_fastBSE_oscillator_strength_out(name: path_type) -> dict:
    """Parser for fastBSE_gauss_quadrature_oscillator_strengths.out.out file.

    :param name: path of the file to parse
    :returns: dictionary containing parsed file
    """

    return {"oscillator_strength": numpy_gen_from_txt(name, 5)}
