"""VXCNN.DAT Parser."""

import re
from pathlib import Path
from typing import Union

import numpy as np

from excitingtools.dataclasses.data_structs import NumberOfStates
from excitingtools.exciting_dict_parsers.gw_eigenvalues_parser import n_states_from_file

path_type = Union[Path, str]


def vkl_from_vxc(file_string: str) -> dict:
    """Extract vkl (k-points in fractional coordinates) from VXCNN.DAT.

    Each k-point header is defined like:
     ik=   1    vkl=  0.0000  0.0000  0.0000

    k-indices are not extracted as they are always contiguous,
    with indexing starting at 1.

    :param str file_string: File string.
    :return dict vkl: k-points in fractional coordinates.
    """
    raw_data: list = re.findall(r"\s*ik= .*$", file_string, flags=re.MULTILINE)
    vkl = {}
    for ik, line in enumerate(raw_data):
        vkl[ik + 1] = [float(k) for k in line.split()[-3:]]
    return vkl


def parse_vxnn_vectors(full_file_name: path_type, vkl: dict, n_states: int) -> dict:
    """Parse VXC diagonal matrix elements from VXCNN.DAT.

    The routine exploits the repeating file structure:

     first_state       last_state        n_kpt : index of first band, index of last band, number of k-points
     ik=   1    vkl=  0.0000  0.0000  0.0000
        1       -2.908349       -0.000000
        2       -2.864103        0.000000
        3       -2.864103       -0.000000
        .
        n_states

     ik=   2    vkl=  0.0000  0.0000  0.5000
        1       -2.908349        0.000000
        2       -2.864100       -0.000000
        3       -2.864100        0.000000
        .
        n_states

    :param str full_file_name: Path + file name
    :param dict vkl: Dictionary of vkl (k-points?)
    :param int n_states: Total number of occupied plus empty states
     Note, this is constant per q-point.

    :return dict data: Parsed VXC diagonal matrix elements, per k-point.
    """
    # File formatting
    header_size = 1
    blank_line = 1
    skip_lines_first_pass = 2

    data = {}

    # When first reading the file, skip the first 2 lines
    skip_lines = skip_lines_first_pass

    # Must iterate lowest to highest, else data won't match k-points
    for ik in range(1, len(vkl) + 1):
        vxc_vector = np.loadtxt(full_file_name, skiprows=skip_lines, max_rows=n_states)
        # Ignore first column (state index)
        data[ik] = vxc_vector[:, 1:]
        skip_lines += n_states + (header_size + blank_line)

    return data


def n_states_from_vxcnn(file_string: str) -> NumberOfStates:
    return n_states_from_file(file_string, n_header=2)


def parse_vxcnn(full_file_name: path_type) -> dict:
    """Parser for VXCNN.DAT.

    :param str full_file_name: Path + file name
    :return dict data: Parsed k-points (labelled as vkl) and the diagonal elements of
     Vxc, per k-point.
    """
    try:
        with open(full_file_name) as f:
            file_string = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"{full_file_name} does not exist")

    data_first_line = file_string.splitlines()[0].split()
    first_state, last_state, n_kpoints = (int(x) for x in data_first_line[:3])
    states = n_states_from_vxcnn(file_string)
    assert states.first_state == first_state, "first_state given in the 1st line incompatible with the rest of the file"
    assert states.last_state == last_state, "last_state given in the 1st line incompatible with the rest of the file"
    vkl = vkl_from_vxc(file_string)
    assert n_kpoints == len(vkl), "n_kpoints given in the 1st line incompatible with the rest of the file"
    v_xc = parse_vxnn_vectors(full_file_name, vkl, states.n_states)
    assert len(vkl) == len(v_xc), "Should be a vector of Vxc_NN for each k-point"

    # Repackage Vxc vectors with their respective k-points
    data = {}
    for ik in range(1, len(vkl) + 1):
        data[ik] = {"vkl": vkl[ik], "v_xc_nn": v_xc[ik]}

    return data
