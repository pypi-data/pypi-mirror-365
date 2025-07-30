"""Test composition of an exciting input XML.

TODO(Fab/Alex/Dan) Issue 117. Would be nice to assert that the output is valid
    XML * https://lxml.de/validation.html
Also see: https://xmlschema.readthedocs.io/en/latest/usage.html#xsd-declarations

NOTE:
All attribute tests should assert on the XML tree content's as the attribute
order is not preserved by the ElementTree.tostring method. Elements appear to
be fine.
"""

import numpy as np
import pytest

from excitingtools.input.input_classes import (  # pylint: disable=E0611
    ExcitingBSEInput,
    ExcitingGroundStateInput,
    ExcitingKeywordsInput,
    ExcitingLibxcInput,
    ExcitingXSInput,
)
from excitingtools.input.input_xml import ExcitingInputXML
from excitingtools.input.structure import ExcitingStructure


@pytest.fixture
def exciting_structure() -> ExcitingStructure:
    """Initialise an exciting structure."""
    cubic_lattice = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    arbitrary_atoms = [
        {"species": "Li", "position": [0.0, 0.0, 0.0]},
        {"species": "Li", "position": [1.0, 0.0, 0.0]},
        {"species": "F", "position": [2.0, 0.0, 0.0]},
    ]
    crystal_properties = {"stretch": [0.6, 0.7, 0.8]}
    species_properties = {
        "Li": {
            "rmt": 1.2,
            "LDAplusU": {"J": 0.4, "U": 1.3, "l": -2},
            "dfthalfparam": {"ampl": 1.2, "shell": [{"number": 2}, {"number": 3}, {"number": 4}]},
        }
    }

    return ExcitingStructure(
        arbitrary_atoms, cubic_lattice, ".", crystal_properties, species_properties, autormtscaling=0.9
    )


@pytest.fixture
def exciting_input_xml(exciting_structure: ExcitingStructure) -> ExcitingInputXML:
    """Initialises a complete input file."""
    ground_state = ExcitingGroundStateInput(
        rgkmax=8.0,
        do="fromscratch",
        ngridk=[6, 6, 6],
        xctype="GGA_PBE_SOL",
        vkloff=[0, 0, 0],
        tforce=True,
        nosource=False,
    )

    bse_attributes = {"bsetype": "singlet", "xas": True}
    energywindow_attributes = {"intv": [5.8, 8.3], "points": 5000}
    screening_attributes = {"screentype": "full", "nempty": 15}
    plan_input = ["screen", "bse"]
    qpointset_input = [[0, 0, 0], [0.5, 0.5, 0.5]]
    xs = ExcitingXSInput(
        xstype="BSE",
        broad=0.32,
        ngridk=[8, 8, 8],
        BSE=bse_attributes,
        energywindow=energywindow_attributes,
        screening=screening_attributes,
        qpointset=qpointset_input,
        plan=plan_input,
    )
    keywords = ExcitingKeywordsInput("keyword1 keyword2 keyword3")

    return ExcitingInputXML(
        sharedfs=True,
        structure=exciting_structure,
        title="Test Case",
        groundstate=ground_state,
        xs=xs,
        keywords=keywords,
    )


def test_exciting_input_xml_structure_and_gs_and_xs(exciting_input_xml: ExcitingInputXML):  # noqa: PLR0915
    """Test the XML created for a ground state input is valid.
    Test SubTree composition using only mandatory attributes for each XML subtree.
    """
    input_xml_tree = exciting_input_xml.to_xml()

    assert input_xml_tree.tag == "input"
    assert input_xml_tree.keys() == ["sharedfs"]

    subelements = list(input_xml_tree)
    assert len(subelements) == 5

    title_xml = subelements[0]
    assert title_xml.tag == "title"
    assert title_xml.keys() == []
    assert title_xml.text == "Test Case"

    structure_xml = subelements[1]
    assert structure_xml.tag == "structure"
    assert structure_xml.keys() == ["speciespath", "autormtscaling"]
    assert len(list(structure_xml)) == 3

    groundstate_xml = subelements[2]
    assert groundstate_xml.tag == "groundstate"
    assert groundstate_xml.text == " "
    assert groundstate_xml.keys() == ["rgkmax", "do", "ngridk", "xctype", "vkloff", "tforce", "nosource"]
    assert groundstate_xml.get("rgkmax") == "8.0"
    assert groundstate_xml.get("do") == "fromscratch"
    assert groundstate_xml.get("ngridk") == "6 6 6"
    assert groundstate_xml.get("xctype") == "GGA_PBE_SOL"
    assert groundstate_xml.get("vkloff") == "0 0 0"
    assert groundstate_xml.get("tforce") == "true"
    assert groundstate_xml.get("nosource") == "false"

    xs_xml = subelements[3]
    assert xs_xml.tag == "xs"
    assert set(xs_xml.keys()) == {"broad", "ngridk", "xstype"}
    assert xs_xml.get("broad") == "0.32"
    assert xs_xml.get("ngridk") == "8 8 8"
    assert xs_xml.get("xstype") == "BSE"

    xs_subelements = list(xs_xml)
    assert len(xs_subelements) == 5
    valid_tags = {"screening", "BSE", "energywindow", "qpointset", "plan"}
    assert valid_tags == set(xs_subelement.tag for xs_subelement in xs_subelements)

    screening_xml = xs_xml.find("screening")
    assert screening_xml.tag == "screening"
    assert screening_xml.keys() == ["screentype", "nempty"]
    assert screening_xml.get("screentype") == "full"
    assert screening_xml.get("nempty") == "15"

    bse_xml = xs_xml.find("BSE")
    assert bse_xml.tag == "BSE"
    assert bse_xml.keys() == ["bsetype", "xas"]
    assert bse_xml.get("bsetype") == "singlet"
    assert bse_xml.get("xas") == "true"

    energywindow_xml = xs_xml.find("energywindow")
    assert energywindow_xml.tag == "energywindow"
    assert energywindow_xml.keys() == ["intv", "points"]
    assert energywindow_xml.get("intv") == "5.8 8.3"
    assert energywindow_xml.get("points") == "5000"

    qpointset_xml = xs_xml.find("qpointset")
    assert qpointset_xml.tag == "qpointset"
    assert qpointset_xml.items() == []
    qpoints = list(qpointset_xml)
    assert len(qpoints) == 2
    assert qpoints[0].tag == "qpoint"
    assert qpoints[0].items() == []
    valid_qpoints = {"0 0 0", "0.5 0.5 0.5"}
    assert qpoints[0].text in valid_qpoints
    valid_qpoints.discard(qpoints[0].text)
    assert qpoints[1].text in valid_qpoints

    plan_xml = xs_xml.find("plan")
    assert plan_xml.tag == "plan"
    assert plan_xml.items() == []
    doonlys = list(plan_xml)
    assert len(doonlys) == 2
    assert doonlys[0].tag == "doonly"
    assert doonlys[0].items() == [("task", "screen")]
    assert doonlys[1].tag == "doonly"
    assert doonlys[1].items() == [("task", "bse")]

    title_xml = subelements[4]
    assert title_xml.tag == "keywords"
    assert title_xml.keys() == []
    assert title_xml.text == "keyword1 keyword2 keyword3"


def test_attribute_modification(exciting_input_xml: ExcitingInputXML):
    """Test the XML created for a ground state input is valid.
    Test SubTree composition using only mandatory attributes for each XML subtree.
    """
    exciting_input_xml.set_title("New Test Case")
    exciting_input_xml.structure.crystal_properties.scale = 2.3
    exciting_input_xml.groundstate.rgkmax = 9.0
    exciting_input_xml.xs.energywindow.points = 4000
    input_xml_tree = exciting_input_xml.to_xml()

    subelements = list(input_xml_tree)
    assert len(subelements) == 5

    title_xml = subelements[0]
    assert title_xml.tag == "title"
    assert title_xml.text == "New Test Case"

    structure_xml = subelements[1]
    assert structure_xml[0].get("scale") == "2.3"

    groundstate_xml = subelements[2]
    assert groundstate_xml.get("rgkmax") == "9.0"

    xs_xml = subelements[3]
    xs_subelements = list(xs_xml)
    assert len(xs_subelements) == 5

    energywindow_xml = xs_xml.find("energywindow")
    assert energywindow_xml.get("points") == "4000"


ref_dict = {
    "groundstate": {
        "do": "fromscratch",
        "ngridk": [6, 6, 6],
        "nosource": False,
        "rgkmax": 8.0,
        "tforce": True,
        "vkloff": [0, 0, 0],
        "xctype": "GGA_PBE_SOL",
    },
    "keywords": "keyword1 keyword2 keyword3",
    "sharedfs": True,
    "structure": {
        "atoms": [
            {"position": [0.0, 0.0, 0.0], "species": "Li"},
            {"position": [1.0, 0.0, 0.0], "species": "Li"},
            {"position": [2.0, 0.0, 0.0], "species": "F"},
        ],
        "autormtscaling": 0.9,
        "crystal_properties": {"stretch": [0.6, 0.7, 0.8]},
        "lattice": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
        "species_path": ".",
        "species_properties": {
            "F": {},
            "Li": {
                "LDAplusU": {"J": 0.4, "U": 1.3, "l": -2},
                "dfthalfparam": {"ampl": 1.2, "shell": [{"number": 2}, {"number": 3}, {"number": 4}]},
                "rmt": 1.2,
            },
        },
    },
    "title": "Test Case",
    "xs": {
        "BSE": {"bsetype": "singlet", "xas": True},
        "broad": 0.32,
        "energywindow": {"intv": [5.8, 8.3], "points": 5000},
        "ngridk": [8, 8, 8],
        "plan": ["screen", "bse"],
        "qpointset": [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]],
        "screening": {"nempty": 15, "screentype": "full"},
        "xstype": "BSE",
    },
}


@pytest.mark.usefixtures("mock_env_jobflow_missing")
def test_as_dict(exciting_input_xml: ExcitingInputXML):
    dict_representation = exciting_input_xml.as_dict()
    assert set(dict_representation.keys()) == {"groundstate", "structure", "sharedfs", "keywords", "xs", "title"}
    assert dict_representation == ref_dict


@pytest.mark.usefixtures("mock_env_jobflow")
def test_as_dict_jobflow(exciting_input_xml: ExcitingInputXML):
    dict_representation = exciting_input_xml.as_dict()
    assert dict_representation.pop("@class") == "ExcitingInputXML"
    assert dict_representation.pop("@module") == "excitingtools.input.input_xml"
    assert dict_representation == ref_dict


@pytest.mark.usefixtures("mock_env_jobflow_missing")
def test_from_dict(exciting_input_xml: ExcitingInputXML):
    new_input_xml = ExcitingInputXML.from_dict(exciting_input_xml.as_dict())
    assert new_input_xml.title.title == "Test Case"  # pylint: disable=no-member
    assert new_input_xml.groundstate.ngridk == [6, 6, 6]  # pylint: disable=no-member


@pytest.mark.usefixtures("mock_env_jobflow")
def test_from_dict_jobflow(exciting_input_xml: ExcitingInputXML):
    new_input_xml = ExcitingInputXML.from_dict(exciting_input_xml.as_dict())
    assert new_input_xml.title.title == "Test Case"  # pylint: disable=no-member


def test_missing_structure():
    with pytest.raises(ValueError, match="Missing mandatory arguments: {'structure'}"):
        ExcitingInputXML(title="Test Case", groundstate=ExcitingGroundStateInput())


def test_from_gs_dict(exciting_structure):
    input_xml = ExcitingInputXML(structure=exciting_structure, title="Test Case", groundstate={"rgkmax": 7.0})
    assert input_xml.title.title == "Test Case"  # pylint: disable=no-member
    assert input_xml.groundstate.rgkmax == 7.0  # pylint: disable=no-member
    assert input_xml.structure.speciespath == "."  # pylint: disable=no-member


def test_from_xml():
    input_str = """<?xml version='1.0' encoding='utf-8'?>
    <input>
        <title>BN (B3)</title>
        <structure speciespath="speciespath" autormt="true">
            <crystal scale="6.816242132875">
                <basevect>0. 0.5 0.5</basevect>
                <basevect>0.5 0. 0.5</basevect>
                <basevect>0.5 0.5 0. </basevect>
            </crystal>
            <species speciesfile="B.xml">
                <atom coord="0. 0. 0." />
            </species>
            <species speciesfile="N.xml">
                <atom coord="0.25 0.25 0.25" />
            </species>
        </structure>
        <groundstate outputlevel="high" ngridk="10 10 10" rgkmax="7.0" maxscl="200" do="fromscratch" xctype="GGA_PBE">
        </groundstate>
    </input>"""
    input_xml = ExcitingInputXML.from_xml(input_str)
    assert input_xml.title.title == "BN (B3)"

    assert input_xml.structure.speciespath == "speciespath"
    assert input_xml.structure.autormt is True
    assert input_xml.structure.species == ["B", "N"]
    np.testing.assert_allclose(input_xml.structure.positions, [[0.0] * 3, [0.25] * 3])
    np.testing.assert_allclose(input_xml.structure.lattice, np.full((3, 3), 0.5) - 0.5 * np.eye(3))
    assert input_xml.structure.crystal_properties.scale == pytest.approx(6.816242132875)

    assert input_xml.groundstate.outputlevel == "high"
    assert input_xml.groundstate.ngridk == [10, 10, 10]
    assert input_xml.groundstate.rgkmax == pytest.approx(7.0)
    assert input_xml.groundstate.maxscl == 200
    assert input_xml.groundstate.do == "fromscratch"
    assert input_xml.groundstate.xctype == "GGA_PBE"


def test_dict_assignment(exciting_input_xml):
    # test simple dict assignment
    groundstate = exciting_input_xml.groundstate
    assert not hasattr(groundstate, "libxc")
    groundstate.libxc = {"exchange": "XC_GGA_X_PBE", "correlation": "XC_GGA_C_PBE"}
    assert hasattr(groundstate, "libxc")
    assert isinstance(groundstate.libxc, ExcitingLibxcInput)

    # test nested dict assignment
    del exciting_input_xml.xs
    assert not hasattr(exciting_input_xml, "xs")
    exciting_input_xml.xs = {"xstype": "BSE", "BSE": {"bsetype": "singlet", "xas": True}}
    assert hasattr(exciting_input_xml, "xs")
    assert isinstance(exciting_input_xml.xs, ExcitingXSInput)
    assert hasattr(exciting_input_xml.xs, "BSE")
    assert isinstance(exciting_input_xml.xs.BSE, ExcitingBSEInput)
    assert exciting_input_xml.xs.BSE.bsetype == "singlet"
    assert exciting_input_xml.xs.BSE.xas

    # test assignment to list of subtrees
    li_properties = exciting_input_xml.structure.species_properties["Li"]
    li_properties.dfthalfparam = {"cut": 0, "shell": [{"number": 1}, {"number": 2}]}
    assert hasattr(li_properties, "dfthalfparam")
    assert li_properties.dfthalfparam.name == "dfthalfparam"
    assert li_properties.dfthalfparam.cut == 0
    assert hasattr(li_properties.dfthalfparam, "shell")
    shell = li_properties.dfthalfparam.shell
    assert isinstance(shell, list)
    assert len(shell) == 2
    assert shell[0].name == "shell"
    assert shell[0].number == 1
    assert shell[1].name == "shell"
    assert shell[1].number == 2


def test_input_validation(exciting_input_xml):
    groundstate = exciting_input_xml.groundstate
    # check if we can assign different type of lists to ngridk
    groundstate._check_attribute_type("ngridk", [10, 10, 10])
    groundstate._check_attribute_type("ngridk", (10, 10, 10))
    groundstate._check_attribute_type("ngridk", np.array([10, 10, 10]))
    # check floating point value accepts integers
    groundstate._check_attribute_type("vkloff", [10, 10, 10])
    groundstate._check_attribute_type("vkloff", [10, 10.0, 10])
    groundstate._check_attribute_type("vkloff", (10, 10, 10))
    groundstate._check_attribute_type("vkloff", np.array([10, 10, 10]))
    # check TypeErrors are thrown
    with pytest.raises(
        TypeError, match="Expected a list, tuple or ndarray for attribute ngridk but got <class 'int'>!"
    ):
        groundstate._check_attribute_type("ngridk", 10)
    with pytest.raises(
        TypeError,
        match=r"Expected all elements of the list to be of type \(<class 'int'>, <class 'numpy.integer'>\) but found "
        r"<class 'numpy.float64'> at index 0!",
    ):
        groundstate._check_attribute_type("ngridk", np.array([10.0, 10, 10]))
    with pytest.raises(
        TypeError,
        match=r"Expected all elements of the list to be of type \(<class 'int'>, <class 'numpy.integer'>\) but found "
        r"<class 'float'> at index 0!",
    ):
        groundstate._check_attribute_type("ngridk", [10.0, 10, 10])
    with pytest.raises(
        TypeError, match="Expected value for xctype to be of type <class 'str'> but found <class 'int'>!"
    ):
        groundstate._check_attribute_type("xctype", 10)
    with pytest.raises(TypeError, match="Expected a single value for attribute xctype, but found a list or tuple!"):
        groundstate._check_attribute_type("xctype", [10, 10, 10])
    # check ValueError is thrown if list has wrong length
    with pytest.raises(ValueError, match="Expected a list of length 3 for attribute ngridk but got one of length 2!"):
        groundstate._check_attribute_type("ngridk", [10, 10])
    # check ValueError is thrown if wrong choice is used
    with pytest.raises(ValueError, match=r"LDA_PBE is not a valid choice for xctype!\nValid choices are: (\w+(, )?)+"):
        groundstate._check_attribute_type("xctype", "LDA_PBE")
    # check boolean values
    groundstate._check_attribute_type("ExplicitKineticEnergy", True)
    groundstate._check_attribute_type("ExplicitKineticEnergy", False)
    with pytest.raises(
        TypeError,
        match="Expected value for ExplicitKineticEnergy to be of type <class 'bool'> but found <class 'str'>!",
    ):
        groundstate._check_attribute_type("ExplicitKineticEnergy", "true")

    # check assignment to element
    groundstate.libxc = {"exchange": "XC_GGA_X_PBE"}
    groundstate.libxc = ExcitingLibxcInput(exchange="XC_GGA_X_PBE")
    with pytest.raises(
        TypeError,
        match="Expected <class 'excitingtools.input.input_classes.ExcitingLibxcInput'> for libxc, "
        "but got <class 'str'>!",
    ):
        groundstate.libxc = "foo"
