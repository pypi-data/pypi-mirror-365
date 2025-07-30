"""Ground state file parsers.

All functions in this module could benefit from refactoring.
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Union

import numpy as np

from excitingtools.parser_utils.erroneous_file_error import ErroneousFileError
from excitingtools.parser_utils.parser_decorators import set_return_values, xml_root

path_type = Union[Path, str]


@set_return_values
def parse_info_out(name: path_type) -> dict:  # noqa: PLR0912, PLR0915
    """
    Parser exciting INFO.OUT into a dictionary.
    In:
        name     string     path of the file to parse
    Out:
        info     dict       contains the content of the file to parse
    """
    lines = Path(name).read_text().split("\n")

    nscl = []
    nini = []
    nstr = []  # For Structure-optimization module
    nopt = []  # For Optimization step
    is_already_converged = None

    # Get line numbers for SCF iteration blocks
    for i, line in enumerate(lines):
        # stores the number of the first and last line of every iteration into a list
        if (
            ("SCF iteration number" in line)
            or ("Hybrids iteration number" in line)
            or ("Reached self-consistent loops maximum" in line)
        ):
            nscl.append(i)
        if (
            ("Convergency criteria checked for the last" in line)
            or ("Self-consistent loop stopped" in line)
            or ("Convergence target is reached" in line)
        ):
            nscl.append(i)
        # stores the number of the first and last line of the initialization into a list
        if "Starting initialization" in line:
            nini.append(i + 2)
        if "Ending initialization" in line:
            nini.append(i - 2)

        # stores the number of the first and last line of Structure-optimization module into a list
        if "Structure-optimization module started" in line:
            nstr.append(i + 2)
            is_already_converged = False
        if "Force convergence target achieved" in line:
            nstr.append(i - 2)
            is_already_converged = False
        if "Maximum force target reached already at the initial configuration" in line:
            nstr.append(i - 2)
            is_already_converged = True

        # stores the number of the first line of every optimization step into a list
        if "Optimization step" in line:
            nopt.append(i)

    calculation_failed = True
    for line in reversed(lines):
        if ("EXCITING" in line) and ("stopped" in line):
            calculation_failed = False
            break

    if calculation_failed:
        raise ErroneousFileError()

    INFO = {}
    INFO["initialization"] = {}
    ini = []
    inits = {}
    k = 0
    speci = 0  # variable to detect different species in INFO.OUT

    unit = None
    # loops through all lines of the initialization
    for i in range(nini[0], nini[1]):
        # stores the lines, which have the format "variable : value" into a list
        if ":" in lines[i]:
            lines[i] = lines[i].split(":")
            ini.append(lines[i])
            if ini[k][0][1] != " " and speci != 0:  # if indentation stops, species part is ended
                speci = 0

            ini[k][0] = ini[k][0].strip()
            ini[k][1] = ini[k][1].strip()
            if ("Lattice vectors" in ini[k][0]) or ("Reciprocal lattice vectors" in ini[k][0]):
                ini[k][1] = []
                lines[i + 1] = lines[i + 1].split()
                lines[i + 2] = lines[i + 2].split()
                lines[i + 3] = lines[i + 3].split()
                for j in range(3):
                    ini[k][1].append(lines[i + 1][j])
                    ini[k][1].append(lines[i + 2][j])
                    ini[k][1].append(lines[i + 3][j])
                if " " in ini[k][1]:
                    ini[k][1] = ini[k][1].split()

            # initialize species subdict if key Species is found:
            if ini[k][0] == "Species":
                speci = ini[k][1][0]
                speci_name = ini[k][1][3:-1]
                inits.update({"Species " + speci: {"Species symbol": speci_name}})

            # stores variable-value pairs in a dictionary, in species subdict if necessary
            if speci != 0:
                if ini[k][0][:16] == "atomic positions":
                    split_key = ini[k][0].split()
                    unit = split_key[2][1:-1]
                    inits["Species " + speci].update({"Atomic positions": {}})
                else:
                    try:
                        key_name = "Atom " + str(int(ini[k][0]))
                        inits["Species " + speci]["Atomic positions"].update({key_name: ini[k][1]})
                    except ValueError:
                        inits["Species " + speci].update({ini[k][0]: ini[k][1]})
            else:
                inits.update({ini[k][0]: ini[k][1]})
            k = k + 1
        # type of mixing is stored in the dictionary too
        if "mixing" in lines[i]:
            lines[i] = lines[i].strip()
            inits.update({"mixing": lines[i]})
    inits.update({"units": {"positions": unit}})

    INFO["initialization"] = inits

    INFO["scl"] = {}

    # loops through all scl's
    for j in range(len(nscl) - 1):
        scls = {}
        scl = []
        k = 0
        # loops through all lines of the scl
        for i in range(nscl[j], nscl[j + 1]):
            # stores the lines, which have the format "variable : value" into a list
            match = re.match(r"\s*(\w.+?\S)\s*(?:\(target\))?\s*:\s*(-?\d+\.\d+(?:E-?\d+)?)", lines[i])
            if match:
                scl.append([match.group(1), match.group(2)])
                # stores variable-value pairs in a dictionary
                scls.update({scl[k][0]: scl[k][1]})
                k = k + 1
        INFO["scl"][str(j + 1)] = scls

    if is_already_converged is not None:
        INFO["str_opt"] = {}
        # Define the necessary data
        checks = [
            "Maximum force",
            "Center of mass",
            "Total torque",
            "Number of total scf iterations",
            "Total atomic forces",
            "Total energy",
            "Atomic positions",
        ]

        # store the number of atoms
        num_of_atoms = int(INFO["initialization"]["Total number of atoms per unit cell"])
        items = {}
        optimization_step = 0

        if not is_already_converged:
            # loop over the structure-optimization module
            i = nstr[0]
            while i < nstr[-1]:
                line = lines[i]
                # note the beginning of each optimization step
                if i in nopt:
                    optimization_step = nopt.index(i)
                    items = {}
                    if optimization_step == 0:
                        items["Number of total scf iterations"] = len(INFO["scl"])
                # stores the lines, which have the format "variable : value" into a list
                elif ":" in line:
                    item, values = re.split(":", line, maxsplit=2)

                    # to check if the variable is necessary
                    item_is_imp = False
                    for check in checks:
                        if check.casefold() in item.casefold():
                            item = check
                            item_is_imp = True
                            break

                    if item_is_imp:
                        items[item] = {}
                    else:
                        i = i + 1
                        continue  # ignore the data

                    # Check if the item has values for each atom like Atomic positions
                    if values == "":  # The values start from next line
                        for j in range(1, num_of_atoms + 1):
                            i = i + 1  # skipping the lines for the next iteration
                            atom, values = re.split(":", lines[i], maxsplit=2)
                            values = values.split()[:3]
                            if len(values) == 1:
                                values = values[0]
                            items[item][j] = values  # storing these in the format {j : values} for each atom
                    else:
                        values = re.findall(r"[-+]?\d*\.\d+|\d+", values)
                        if len(values) == 1:
                            values = values[0]
                        items[item] = values
                if optimization_step is not None:
                    INFO["str_opt"][optimization_step] = items
                i = i + 1
        else:
            #  Maximum force target reached already at the initial configuration

            items["Number of total scf iterations"] = len(INFO["scl"])

            i = nscl[-1]
            while i < nstr[-1]:
                line = lines[i]

                # stores the lines, which have the format "variable : value" into a list
                if ":" in line:
                    item, values = re.split(":", line, maxsplit=2)

                    # to check if the variable is necessary
                    item_is_imp = False
                    for check in checks:
                        if check.casefold() in item.casefold():
                            item = check
                            item_is_imp = True
                            break

                    if item_is_imp:
                        items[item] = {}
                    else:
                        i = i + 1
                        continue  # ignore the data

                    # Check if the item has values for each atom like Atomic positions
                    if values == "":  # The values start from next line
                        for j in range(1, num_of_atoms + 1):
                            i = i + 1  # skipping the lines for the next iteration
                            atom, values = re.split(":", lines[i], maxsplit=2)
                            values = values.split()[:3]
                            if len(values) == 1:
                                values = values[0]
                            items[item][j] = values  # storing these in the format {j : values} for each atom
                    else:
                        values = re.findall(r"[-+]?\d*\.\d+|\d+", values)
                        if len(values) == 1:
                            values = values[0]
                        items[item] = values
                if optimization_step is not None:
                    INFO["str_opt"][optimization_step] = items
                i = i + 1
    return INFO


@set_return_values
def parse_info_xml(file: path_type) -> dict:
    """
    Parser exciting info.xml into a python dictionary.
    In:
        file     string     path of the file to parse
    Out:
        info     dict       contains the content of the file to parse
    """
    try:
        root = ET.parse(file)
    except AttributeError:
        raise ErroneousFileError

    info = root.find("groundstate").attrib

    excitingRun = []
    i = 0
    for node in root.find("groundstate").find("scl").iter("iter"):
        excitingRun.append(node.attrib)
        excitingRun[i]["energies"] = node.find("energies").attrib
        excitingRun[i]["charges"] = node.find("charges").attrib
        atomic_charge = []
        species = []
        for atom_nr, atoms in enumerate(node.find("charges").iter("atom")):
            if atom_nr == 0:
                species_old = atoms.get("species")
            if atoms.get("species") == species_old:
                species.append({"muffin-tin": atoms.get("muffin-tin")})
            else:
                species_old = atoms.get("species")
                atomic_charge.append(species)
                species = [{"muffin-tin": atoms.get("muffin-tin")}]
                atomic_charge.append(species)
                excitingRun[i]["charges"]["atomic"] = atomic_charge
                excitingRun[i]["timing"] = node.find("timing").attrib
        if node.find("moments") is not None:
            moments = {
                "momtot": node.find("moments").find("momtot").attrib,
                "interstitial": node.find("moments").find("momtot").attrib,
                "mommttot": node.find("moments").find("interstitial").attrib,
            }
            excitingRun[i]["moments"] = moments
            atom_nr = 0
            atomic_moment = []
            species = []
            for atoms in node.find("moments").iter("atom"):
                if atom_nr == 0:
                    species_old = atoms.get("species")
                atom_nr += 1
                if atoms.get("species") == species_old:
                    species.append(atoms.find("mommt").attrib)
                else:
                    species_old = atoms.get("species")
                    atomic_moment.append(species)
                    species = [atoms.find("mommt").attrib]
                    atomic_moment.append(species)
                    excitingRun[i]["moments"]["atomic"] = atomic_moment
        i = i + 1
    info["scl"] = {}
    for item in excitingRun:  # converts list of scl-iterations into a dictionary
        name = item["iteration"]
        info["scl"][name] = item

    return info


@set_return_values
def parse_atoms(file: path_type) -> dict:
    """
    Parser exciting atoms.xml into a python dictionary.
    In:
        file     string     path of the file to parse
    Out:
        info     dict       contains the content of the file to parse
    """

    root = ET.parse(file)
    atoms = {}
    atoms["Hamiltonian"] = root.find("Hamiltonian").attrib
    atom = []
    i = 0
    for node in root.findall("atom"):
        atom.append(node.attrib)

        states = node.find("spectrum")
        spectrum = [state.attrib for state in states.findall("state")]

        atom[i]["NumericalSetup"] = node.find("NumericalSetup").attrib
        atom[i]["spectrum"] = {}
        j = 0
        for item in spectrum:  # converts list of states into a dictionary
            name = str(j)
            atom[i]["spectrum"][name] = item
            j = j + 1
        i = i + 1
    atoms["atom"] = {}
    for item in atom:  # converts list of atoms into a dictionary
        name = item["chemicalSymbol"]
        atoms["atom"][name] = item

    return atoms


@set_return_values
@xml_root
def parse_eigval(root) -> dict:
    """Parse eigenvalues from eigval.xml file.

    :param root: XML file name, XML string or ElementTree.Element as input.
    :return: dict output: Parsed data.
    """
    eigval = root.attrib

    kpts = []
    for node in root.findall("kpt"):
        kpt = node.attrib
        state = []
        for subnode in node:
            state.append(subnode.attrib)
            kpt["state"] = {}  # converts list of states into a dictionary
        for item in state:
            name = item["ist"]
            kpt["state"][name] = item
            kpts.append(kpt)
            eigval["kpt"] = {}
    for item in kpts:  # converts list of kpts into a dictionary
        name = item["ik"]
        eigval["kpt"][name] = item

    return eigval


@set_return_values
def parse_evalcore(file: path_type) -> dict:
    """
    Parser exciting evalcore.xml into a python dictionary.
    In:
        file     string     path of the file to parse
    Out:
        info     dict       contains the content of the file to parse
    """

    root = ET.parse(file).getroot()
    evalcore = root.attrib

    speciess = []
    for node in root.findall("species"):
        species = node.attrib
        atoms = []
        for subnode in node:
            atom = subnode.attrib
            states = []
            for subnode1 in subnode:
                state = subnode1.attrib
                states.append(state)
            atom["state"] = {}
            for item in states:  # converts list of states into a dictionary
                name = item["ist"]
                atom["state"][name] = item
            atoms.append(atom)
            species["atom"] = {}
            for item in atoms:  # converts list of atoms into a dictionary
                name = item["ia"]
                species["atom"][name] = item
        speciess.append(species)
    evalcore["species"] = {}
    for item in speciess:  # converts list of species into a dictionary
        name = item["chemicalSymbol"]
        evalcore["species"][name] = item

    return evalcore


@set_return_values
def parse_geometry(file: path_type) -> dict:
    """
    Parser exciting geometry.xml into a python dictionary.
    In:
        file     string     path of the file to parse
    Out:
        info     dict       contains the content of the file to parse
    """

    root = ET.parse(file).getroot()
    structure = root.find("structure").attrib
    crystal = root.find("structure").find("crystal").attrib
    geometry = {"structure": structure}
    structure["crystal"] = crystal
    speciess = []
    for node in root.find("structure").findall("species"):
        species = node.attrib
        atoms = []
        for subnode in node:
            atom = subnode.attrib
            atoms.append(atom)
            species["atom"] = {}
        i = 1
        for item in atoms:
            name = str(i)
            species["atom"][name] = item["coord"].split()
            i = i + 1
        speciess.append(species)
    structure["species"] = {}
    j = 1
    for item in speciess:
        name = str(j)
        structure["species"][name] = item
        j = j + 1

    basevects = []
    for node in root.find("structure").find("crystal").findall("basevect"):
        basevect = node.text
        basevects.append(basevect)
        structure["crystal"]["basevect"] = {}
        k = 1
    for item in basevects:
        name = str(k)
        structure["crystal"]["basevect"][name] = item
        k = k + 1
    return geometry


@set_return_values
def parse_linengy(name: path_type) -> dict:
    """
    Parser for: LINENGY.OUT

    :param name: path of the file to parse
    :returns: dictionary containing parsed file
    """

    linengy = {}

    with open(file=name) as fid:
        lines = fid.readlines()

    apw_line = []
    lo_line = []

    for i, line in enumerate(lines):
        if "APW functions" in line:
            apw_line.append(i)
        if "local-orbital functions" in line:
            lo_line.append(i)

    apw_line.append(len(lines))

    for i in range(len(lo_line)):
        linengy[str(i)] = {}

        apw = [lines[j].split(":")[1].strip() for j in range(apw_line[i], lo_line[i]) if "l =" in lines[j]]
        linengy[str(i)]["apw"] = apw

        lo = [lines[j].split(":")[1].strip() for j in range(lo_line[i], apw_line[i + 1]) if "l =" in lines[j]]
        linengy[str(i)]["lo"] = lo

    return linengy


@set_return_values
def parse_lo_recommendation(name: path_type) -> dict:
    """
    Parser for: LO_RECOMMENDATION.OUT

    :param name: path of the file to parse
    :returns: dictionary containing parsed file
    """
    with open(file=name) as fid:
        lines = fid.readlines()

    n_species = int(lines[2].split(":")[1])
    n_l_channels = int(lines[3].split(":")[1])
    n_nodes = int(lines[4].split(":")[1])

    lo_recommendation = {"n_species": n_species, "n_l_channels": n_l_channels, "n_nodes": n_nodes}

    blocks = lines[6:]
    block_size = n_nodes + 3
    n_blocks = n_l_channels * n_species

    for iblock in range(n_blocks):
        offset = iblock * block_size
        matches = re.findall(r":\s(.*?)(?:,|$)", blocks[offset + 0])
        species, l = matches[0], int(matches[1])
        # Package (node, n, energy) as one likes
        if species not in lo_recommendation:
            lo_recommendation.update({species: {}})
        lo_recommendation[species].update({l: np.loadtxt(blocks[offset + 2 : offset + n_nodes + 2]).tolist()})

    return lo_recommendation
