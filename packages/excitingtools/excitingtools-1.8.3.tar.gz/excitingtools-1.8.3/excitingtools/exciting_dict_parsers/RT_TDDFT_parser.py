"""
Parsers for real-time TDDFT output files
"""

from pathlib import Path
from typing import List, Union
from xml.etree.ElementTree import ParseError

import numpy as np

from excitingtools.parser_utils.grep_parser import grep

path_type = Union[Path, str]


def parse_nexc(name: path_type, skiprows=1):
    """
    Parser for N_EXCITATIONS.OUT
    """
    try:
        data = np.genfromtxt(name, skip_header=skiprows)
    except Exception:
        raise ParseError
    out = {
        "Time": data[:, 0],
        "number_electrons_GroundState": data[:, 1],
        "number_electrons_ExcitedState": data[:, 2],
        "sum": data[:, 3],
    }

    return out


def parse_jind(name: path_type, skiprows=0):
    """
    Parser for CURRENT.OUT
    """
    try:
        data = np.genfromtxt(name, skip_header=skiprows)
    except Exception:
        raise ParseError
    out = {"Time": data[:, 0], "Jx": data[:, 1], "Jy": data[:, 2], "Jz": data[:, 3]}

    return out


def parse_etot(name: path_type):
    """
    Parser for TOTENERGY_RTTDDFT.OUT
    """
    try:
        data = np.genfromtxt(name, skip_header=1)
    except Exception:
        raise ParseError
    out = {
        "Time": data[:, 0],
        "ETOT": data[:, 1],
        "Madelung": data[:, 2],
        "Eigenvalues-Core": data[:, 3],
        "Eigenvalues-Valence": data[:, 4],
        "Exchange": data[:, 5],
        "Correlation": data[:, 6],
        "XC-potential": data[:, 7],
        "Coulomb pot. energy": data[:, 8],
    }

    return out


def parse_eigval_screenshots(name: path_type) -> dict:
    """
    Parser for EIGVAL_*.OUT.
    """

    def get_k_point_blocks(name: path_type, fortran_index=False) -> List[dict]:
        """
        Parse the k point blocks.

        For a file:
        line 0   ik =       1
        line 1    1     -0.357413438539
                  .
        line 35   35      8.032537750481
        line 36
        line 37  ik =       2
        line 38   1     -0.280187464596
                  .
        line 75   38      8.808472531393

        The parsed k-point block lines correspond to:
          k_blocks[0]['start'] = line 0   i.e.   ik =       1
          k_blocks[0]['end']   = line 35  i.e.   35      8.032537750481
          k_blocks[1]['start'] = line 37  i.e.   ik =       2
          k_blocks[1]['end']   = line 75  i.e.   38      8.808472531393


        Default line indexing starts at 0.
        """

        # Lines for which a new k-point block starts
        raw_k_point_lines = grep("ik", name, options={"n": ""}).splitlines()
        k_point_lines = [int(line.split(":")[0]) for line in raw_k_point_lines]

        if fortran_index:
            offset = 1
        else:
            # Python indexing
            offset = 0
            k_point_lines = [int(i) - 1 for i in k_point_lines]

        with open(name) as file:
            n_lines = len(file.readlines()) + offset

        k_blocks = []
        k_start = 0 + offset
        for ik in k_point_lines[1:]:
            k_end = ik - 2
            k_blocks.append({"start": k_start, "end": k_end})
            k_start = k_end + 2

        # Account for final k-block
        k_blocks.append({"start": k_start, "end": n_lines - 2})

        return k_blocks

    k_blocks = get_k_point_blocks(name)

    # Parse file
    with open(name) as f:
        file = f.readlines()

    data = {}
    kpoints = []
    for indices in k_blocks:
        kpoint = {}
        ik = int(file[indices["start"]].split()[-1])
        eigenvalues = [float(file[i].split()[-1]) for i in range(indices["start"] + 1, indices["end"] + 1)]
        kpoint["ik"] = ik
        kpoint["eigenvalues"] = eigenvalues
        kpoints.append(kpoint)

    data["kpoints"] = kpoints

    return data


def parse_proj_screenshots(name: path_type) -> dict:
    """
    Parser for PROJECTION_COEFFS_*.OUT.

    Effectively the same code as parse_eigval_screenshots, but the whitespace
    between blocks differs by 1.
    """

    raw_k_point_lines = grep("ik", name, options={"n": ""}).splitlines()
    k_point_lines = [int(line.split(":")[0]) - 1 for line in raw_k_point_lines]
    with open(name) as file:
        last_line = len(file.readlines())

    k_blocks = []
    k_start = 0
    for ik in k_point_lines[1:]:
        k_end = ik
        k_blocks.append([k_start, k_end])
        k_start = k_end
    k_blocks.append([k_end, last_line])

    # Parse file
    with open(name) as f:
        file = f.readlines()

    data = {"ik": [], "projection": []}
    for i in k_blocks:
        start = i[0]
        end = i[1]
        ik = int(file[start].split()[-1])
        projection = [[float(x) for x in file[j].split()] for j in range(start + 1, end)]
        data["ik"].append(ik)
        data["projection"].append(np.asarray(projection))
    return data


def parse_occupations(file_name: path_type) -> dict:
    """
    Parser for OCCSV_TXT_*.OUT
    """

    with open(file_name) as f:
        lines = f.readlines()

    data = {"ik": [], "occupations": []}
    for line in lines:
        if "ik" in line:
            ik = int(line.split()[-1])
            data["ik"].append(ik)
            aux = []
        elif not line.split():
            data["occupations"].append(np.array(aux))
        else:
            aux.append(float(line.split()[1]))
    return data


def parse_atom_position_velocity_force(name: path_type) -> dict:
    """Parser for ATOM_????.OUT
    :param str name: name of file to parse
    :return dict out: each dict key corresponds to time, position (3 columns), velocity (3 columns), total force (3 columns).
    The 3 columns refer to the x, y, z components
    """
    try:
        data = np.genfromtxt(name, skip_header=0)
    except Exception:
        raise ParseError
    out = {
        "Time": data[:, 0],
        "x": data[:, 1],
        "y": data[:, 2],
        "z": data[:, 3],
        "vx": data[:, 4],
        "vy": data[:, 5],
        "vz": data[:, 6],
        "Fx": data[:, 7],
        "Fy": data[:, 8],
        "Fz": data[:, 9],
    }

    return out


def parse_force(name: path_type, skiprows=0):
    """
    Parser for X_????.OUT, where X can be:
    - FCR: core corrections to forces
    - FEXT: external forces (due to e.g. an electric field)
    - FHF: Hellman-Feynman term of forces
    - FVAL: valence corrections to forces
    """
    try:
        data = np.genfromtxt(name, skip_header=skiprows)
    except Exception:
        raise ParseError
    out = {"Time": data[:, 0], "Fx": data[:, 1], "Fy": data[:, 2], "Fz": data[:, 3]}

    return out
