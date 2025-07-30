"""Tests for species file class."""

import pytest

import excitingtools
from excitingtools.species.species_file import SpeciesFile


@pytest.fixture
def species_C():
    """Species file object for carbon."""
    species = {"chemicalSymbol": "C", "mass": 21.16, "name": "carbon", "z": -6.0}
    muffin_tin = {"radialmeshPoints": 250, "radius": 1.45, "rinf": 21.09, "rmin": 1e-05}
    atomic_states = [
        {"core": True, "kappa": 1, "l": 0, "n": 1, "occ": 2.0},
        {"core": False, "kappa": 1, "l": 0, "n": 2, "occ": 2.0},
        {"core": False, "kappa": 1, "l": 1, "n": 2, "occ": 1.0},
        {"core": False, "kappa": 2, "l": 1, "n": 2, "occ": 1.0},
    ]
    basis = {
        "default": [{"searchE": False, "trialEnergy": 0.15, "type": "apw"}],
        "custom": [
            {"l": 0, "n": 2, "searchE": False, "type": "apw"},
            {"l": 1, "n": 2, "searchE": False, "type": "apw"},
        ],
        "lo": [
            {
                "l": 0,
                "wf": [
                    {"matchingOrder": 1, "n": 2, "searchE": False},
                    {"matchingOrder": 2, "n": 2, "trialEnergy": 0.15, "searchE": False},
                ],
            },
            {
                "l": 1,
                "wf": [{"matchingOrder": 0, "n": 3, "searchE": True}, {"matchingOrder": 1, "n": 3, "searchE": False}],
            },
        ],
    }

    species = SpeciesFile(species, muffin_tin, atomic_states, basis)
    return species


def test_class_species_file_to_xml(species_C):
    xml_species_C = species_C.to_xml()
    assert xml_species_C.tag == "spdb", "XML root should be spdb"


def test_class_species_file_species_to_xml(species_C):
    xml_species_C = species_C.to_xml()
    sp_element = xml_species_C.find("sp")
    ref_attribs = {"chemicalSymbol": "C", "mass": "21.16", "name": "carbon", "z": "-6.0"}
    assert sp_element.attrib == ref_attribs, "Mismatch in species attributes."


def test_class_species_file_muffin_tin_to_xml(species_C):
    xml_species_C = species_C.to_xml()
    sp_element = xml_species_C.find("sp")
    muffinTin_element = sp_element.find("muffinTin")
    ref_attribs = {"radialmeshPoints": "250", "radius": "1.45", "rinf": "21.09", "rmin": "1e-05"}
    assert muffinTin_element.attrib == ref_attribs, "Mismatch in muffin-tin attributes."


def test_class_species_file_atomic_states_to_xml(species_C):
    xml_species_C = species_C.to_xml()
    sp_element = xml_species_C.find("sp")
    atomicState_elements = sp_element.findall("atomicState")
    assert atomicState_elements and len(atomicState_elements) == 4

    ref_attribs = [
        {"core": "true", "kappa": "1", "l": "0", "n": "1", "occ": "2.0"},
        {"core": "false", "kappa": "1", "l": "0", "n": "2", "occ": "2.0"},
        {"core": "false", "kappa": "1", "l": "1", "n": "2", "occ": "1.0"},
        {"core": "false", "kappa": "2", "l": "1", "n": "2", "occ": "1.0"},
    ]

    for i, atomicState in enumerate(atomicState_elements):
        assert atomicState.attrib == ref_attribs[i], f"Mismatch in atomic states at index {i}"


def test_class_species_file_basis_to_xml(species_C):
    xml_species_C = species_C.to_xml()
    sp_element = xml_species_C.find("sp")
    basis_element = sp_element.find("basis")

    default_element = basis_element.find("default")
    ref_attribs = {"searchE": "false", "trialEnergy": "0.15", "type": "apw"}
    assert default_element.attrib == ref_attribs, "Mismatch in default attributes."

    custom_elements = basis_element.findall("custom")
    assert len(custom_elements) == 2, f"Expected 2 custom elements, but got {len(custom_elements)}."
    ref_attribs = [
        {"l": "0", "n": "2", "searchE": "false", "type": "apw"},
        {"l": "1", "n": "2", "searchE": "false", "type": "apw"},
    ]
    for i, customState in enumerate(custom_elements):
        assert customState.attrib == ref_attribs[i], f"Mismatch in custom state at index {i}"

    lo_elements = basis_element.findall("lo")
    ref_attribs = {
        "lo": [
            {
                "l": "0",
                "wf": [
                    {"matchingOrder": "1", "n": "2", "searchE": "false"},
                    {"matchingOrder": "2", "n": "2", "trialEnergy": "0.15", "searchE": "false"},
                ],
            },
            {
                "l": "1",
                "wf": [
                    {"matchingOrder": "0", "n": "3", "searchE": "true"},
                    {"matchingOrder": "1", "n": "3", "searchE": "false"},
                ],
            },
        ]
    }
    for i, loState in enumerate(lo_elements):
        wf_elements = loState.findall("wf")
        ref_wf_attribs = ref_attribs["lo"][i]["wf"]
        for j, wfState in enumerate(wf_elements):
            assert wfState.attrib == ref_wf_attribs[j], (
                f"Mismatch in wf attributes at index {j} of loState at index {i}"
            )


def test_check_matching_orders(species_C):
    species_C.basis = {
        "lo": [
            {
                "l": 0,
                "wf": [
                    {"matchingOrder": 1, "n": 2, "searchE": False},
                    {"matchingOrder": 2, "n": 2, "trialEnergy": 0.15, "searchE": False},
                ],
            },
            {
                "l": 3,
                "wf": [
                    {"matchingOrder": 0, "n": 5, "searchE": False},
                    {"matchingOrder": 4, "n": 5, "searchE": False},
                    {"matchingOrder": 3, "n": 3, "searchE": False},
                ],
            },
        ]
    }

    result_dict = species_C.check_matching_orders()
    ref_dict = {0: {2}, 3: {3, 5}}
    assert result_dict == ref_dict, "check_matching_orders failed"


def test_get_helos_from_species(species_C):
    species_C.basis = {
        "lo": [
            {
                "l": 0,
                "wf": [
                    {"matchingOrder": 1, "n": 4, "searchE": False},
                    {"matchingOrder": 2, "n": 2, "trialEnergy": 0.15, "searchE": False},
                ],
            },
            {
                "l": 3,
                "wf": [{"matchingOrder": 2, "n": 6, "searchE": False}, {"matchingOrder": 4, "n": 4, "searchE": False}],
            },
            {
                "l": 1,
                "wf": [{"matchingOrder": 0, "n": 2, "searchE": False}, {"matchingOrder": 1, "n": 2, "searchE": False}],
            },
        ]
    }

    helos_ns_per_l = species_C.get_helos_from_species()
    ref_helos_ns_per_l = {0: {4}, 1: set(), 3: {4, 6}}
    assert helos_ns_per_l == ref_helos_ns_per_l, "get_helos_from_species failed"


def test_get_n_per_l(species_C):
    species_C.basis = {
        "lo": [
            {
                "l": 0,
                "wf": [
                    {"matchingOrder": 1, "n": 4, "searchE": False},
                    {"matchingOrder": 2, "n": 2, "trialEnergy": 0.15, "searchE": False},
                ],
            },
            {
                "l": 3,
                "wf": [{"matchingOrder": 2, "n": 6, "searchE": False}, {"matchingOrder": 4, "n": 4, "searchE": False}],
            },
            {
                "l": 1,
                "wf": [{"matchingOrder": 0, "n": 2, "searchE": False}, {"matchingOrder": 1, "n": 2, "searchE": False}],
            },
        ]
    }

    atomicstate_ns_per_l, lo_ns_per_l = species_C.get_atomicstates_ns_per_l(), species_C.get_lo_ns_per_l()

    ref_lo_ns_per_l = {0: {2, 4}, 1: {2}, 3: {4, 6}}
    assert lo_ns_per_l == ref_lo_ns_per_l, "get_n_per_l: get_lo_ns_per_l failed"

    ref_atomicstate_ns_per_l = {0: {1, 2}, 1: {2}}
    assert atomicstate_ns_per_l == ref_atomicstate_ns_per_l, "get_n_per_l: get_atomicstates_ns_per_l failed"


@pytest.mark.filterwarnings("ignore:HELO skipped for l:")
def test_get_first_helo_n(species_C):
    species_C.basis = {
        "lo": [
            {
                "l": 0,
                "wf": [
                    {"matchingOrder": 1, "n": 4, "searchE": False},
                    {"matchingOrder": 2, "n": 2, "trialEnergy": 0.15, "searchE": False},
                ],
            },
            {
                "l": 3,
                "wf": [{"matchingOrder": 2, "n": 6, "searchE": False}, {"matchingOrder": 4, "n": 4, "searchE": False}],
            },
            {
                "l": 1,
                "wf": [{"matchingOrder": 0, "n": 1, "searchE": False}, {"matchingOrder": 1, "n": 1, "searchE": False}],
            },
        ]
    }

    lO_first_helo_n = species_C.get_first_helo_n(l=0)
    ref_lO_first_helo_n = 5
    assert lO_first_helo_n == ref_lO_first_helo_n, "get_first_helo_n: for l=0 failed"

    l1_first_helo_n = species_C.get_first_helo_n(l=1)
    ref_l1_first_helo_n = 3
    assert l1_first_helo_n == ref_l1_first_helo_n, "get_first_helo_n: for l=1 failed"

    l2_first_helo_n = species_C.get_first_helo_n(l=2)
    ref_l2_first_helo_n = 3
    assert l2_first_helo_n == ref_l2_first_helo_n, "get_first_helo_n: for l=2 failed"

    l3_first_helo_n = species_C.get_first_helo_n(l=3)
    ref_l3_first_helo_n = 8
    assert l3_first_helo_n == ref_l3_first_helo_n, "get_first_helo_n: for l=3 failed"


@pytest.mark.filterwarnings("ignore:HELO skipped for l:")
def test_add_helos(species_C):
    species_C.add_helos(0, 1)
    helo_ns_per_l = species_C.get_helos_from_species()
    ref_helo_ns_per_l = {0: {4}, 1: {3}}
    assert helo_ns_per_l == ref_helo_ns_per_l, "add_helos: for l=0 number=1 failed"

    species_C.add_helos(3, 3)
    helo_ns_per_l = species_C.get_helos_from_species()
    ref_helo_ns_per_l = {0: {4}, 1: {3}, 3: {4, 5, 6}}
    assert helo_ns_per_l == ref_helo_ns_per_l, "add_helos: for l=3 number=3 failed"

    species_C.add_helos(0, 2)
    helo_ns_per_l = species_C.get_helos_from_species()
    ref_helo_ns_per_l = {0: {4, 5, 6}, 1: {3}, 3: {4, 5, 6}}
    assert helo_ns_per_l == ref_helo_ns_per_l, "add_helos: for l=0 number=2 failed"

    species_C.add_helos(1, 2)
    helo_ns_per_l = species_C.get_helos_from_species()
    ref_helo_ns_per_l = {0: {4, 5, 6}, 1: {3, 4, 5}, 3: {4, 5, 6}}
    assert helo_ns_per_l == ref_helo_ns_per_l, "add_helos: for l=1 number=2 failed"


def test_get_valence_semicore_atomicstate_ns_per_l(species_C):
    ref_states = {0: {2}, 1: {2}}
    assert ref_states == species_C.get_atomicstates_ns_per_l(lambda x: not x["core"]), (
        "Failed to get valence/semicore states"
    )

    species_C.atomic_states = [
        {"core": False, "kappa": 1, "l": 0, "n": 1, "occ": 2.0},
        {"core": False, "kappa": 1, "l": 0, "n": 2, "occ": 2.0},
        {"core": False, "kappa": 1, "l": 1, "n": 2, "occ": 1.0},
        {"core": False, "kappa": 2, "l": 1, "n": 2, "occ": 1.0},
    ]
    ref_states = {0: {1, 2}, 1: {2}}
    assert ref_states == species_C.get_atomicstates_ns_per_l(lambda x: not x["core"]), (
        "Failed to get valence/semicore states"
    )


def test_get_valence_and_semicore_atomicstate_ns_per_l(species_C):
    valence_and_semicore_states = species_C.get_valence_and_semicore_atomicstate_ns_per_l()
    ref_valence_and_semicore_states = {0: {"semicore": set(), "valence": {2}}, 1: {"semicore": set(), "valence": {2}}}
    assert ref_valence_and_semicore_states == valence_and_semicore_states, "Failed to get valence and semicore states"

    species_C.atomic_states = [
        {"core": False, "kappa": 1, "l": 0, "n": 1, "occ": 2.0},
        {"core": False, "kappa": 1, "l": 0, "n": 2, "occ": 2.0},
        {"core": False, "kappa": 1, "l": 1, "n": 2, "occ": 1.0},
        {"core": False, "kappa": 2, "l": 1, "n": 2, "occ": 1.0},
    ]
    ref_valence_and_semicore_states = {0: {"semicore": {1}, "valence": {2}}, 1: {"semicore": set(), "valence": {2}}}
    valence_and_semicore_states = species_C.get_valence_and_semicore_atomicstate_ns_per_l()
    assert ref_valence_and_semicore_states == valence_and_semicore_states, "Failed to get valence and semicore states"


def test_add_number_los_for_all_valence_semicore_states(species_C):
    ref_los = [
        {
            "l": 0,
            "wf": [
                {"matchingOrder": 1, "n": 2, "searchE": False},
                {"matchingOrder": 2, "n": 2, "trialEnergy": 0.15, "searchE": False},
            ],
        },
        {"l": 1, "wf": [{"matchingOrder": 0, "n": 3, "searchE": True}, {"matchingOrder": 1, "n": 3, "searchE": False}]},
        {"l": 0, "wf": [{"matchingOrder": 2, "searchE": True, "n": 2}, {"matchingOrder": 3, "searchE": True, "n": 2}]},
        {"l": 1, "wf": [{"matchingOrder": 0, "searchE": True, "n": 2}, {"matchingOrder": 1, "searchE": True, "n": 2}]},
    ]
    species_C.add_number_los_for_all_valence_semicore_states(1, search_e=True)
    assert ref_los == species_C.basis["lo"], "add_number_los_for_all_valence_semicore_states failed"


def test_add_basic_lo_all_semicore_states(species_C):
    species_C.add_basic_lo_all_semicore_states()
    ref_los = [
        {
            "l": 0,
            "wf": [
                {"matchingOrder": 1, "n": 2, "searchE": False},
                {"matchingOrder": 2, "n": 2, "trialEnergy": 0.15, "searchE": False},
            ],
        },
        {"l": 1, "wf": [{"matchingOrder": 0, "n": 3, "searchE": True}, {"matchingOrder": 1, "n": 3, "searchE": False}]},
    ]
    assert ref_los == species_C.basis["lo"], "add_basic_lo_all_semicore_states failed"

    species_C.atomic_states = [
        {"core": False, "kappa": 1, "l": 0, "n": 1, "occ": 2.0},
        {"core": False, "kappa": 1, "l": 0, "n": 2, "occ": 2.0},
        {"core": False, "kappa": 1, "l": 1, "n": 2, "occ": 1.0},
        {"core": False, "kappa": 2, "l": 1, "n": 2, "occ": 1.0},
    ]
    species_C.add_basic_lo_all_semicore_states(search_e=True)
    ref_los = [
        {
            "l": 0,
            "wf": [
                {"matchingOrder": 1, "n": 2, "searchE": False},
                {"matchingOrder": 2, "n": 2, "trialEnergy": 0.15, "searchE": False},
            ],
        },
        {"l": 1, "wf": [{"matchingOrder": 0, "n": 3, "searchE": True}, {"matchingOrder": 1, "n": 3, "searchE": False}]},
        {"l": 0, "wf": [{"matchingOrder": 0, "searchE": True, "n": 2}, {"matchingOrder": 0, "searchE": True, "n": 1}]},
    ]
    assert ref_los == species_C.basis["lo"], "add_basic_lo_all_semicore_states failed"


def test_add_default(species_C):
    species_C.basis = {}
    species_C.basis.setdefault("default", [])
    species_C.add_default(trial_energy=0.2, default_type="lapw", search_e=True)

    ref_default = [{"type": "lapw", "trialEnergy": 0.2, "searchE": True}]
    assert ref_default == species_C.basis["default"], "Adding a default element failed"


def test_add_custom_for_all_valence_states(species_C):
    species_C.basis = {}
    species_C.basis.setdefault("custom", [])
    species_C.add_custom_for_all_valence_states(custom_type="lapw", search_e=True)

    ref_custom = [{"l": 0, "n": 2, "searchE": True, "type": "lapw"}, {"l": 1, "n": 2, "searchE": True, "type": "lapw"}]

    assert ref_custom == species_C.basis["custom"], "Adding a custom element for all valence states failed"


def test_find_highest_matching_order_for_state(species_C):
    max_mO_order = species_C.find_highest_matching_order_for_state(l=0, n=2)
    assert max_mO_order == 2, "Finding the highest matchingOrder failed for l=0, n=2"

    max_mO_order = species_C.find_highest_matching_order_for_state(l=1, n=3)
    assert max_mO_order == 1, "Finding the highest matchingOrder failed for l=1, n=3"

    max_mO_order = species_C.find_highest_matching_order_for_state(l=1, n=2)
    assert max_mO_order == 0, "Finding the highest matchingOrder failed for l=1, n=3"


def test_add_lo_higher_matching_order(species_C):
    species_C.add_lo_higher_matching_order(l=0, n=2, raise_exception=False)
    ref_los = [
        {
            "l": 0,
            "wf": [
                {"matchingOrder": 1, "n": 2, "searchE": False},
                {"matchingOrder": 2, "n": 2, "trialEnergy": 0.15, "searchE": False},
            ],
        },
        {"l": 1, "wf": [{"matchingOrder": 0, "n": 3, "searchE": True}, {"matchingOrder": 1, "n": 3, "searchE": False}]},
        {
            "l": 0,
            "wf": [{"matchingOrder": 2, "searchE": False, "n": 2}, {"matchingOrder": 3, "searchE": False, "n": 2}],
        },
    ]
    assert ref_los == species_C.basis["lo"], "Adding lo for higher matchingOrder failed for l=0, n=2"

    species_C.add_lo_higher_matching_order(l=0, n=2, raise_exception=False)
    assert ref_los == species_C.basis["lo"], "Adding 2 lo's for higher matchingOrder failed for l=0, n=2"

    species_C.add_lo_higher_matching_order(l=1, n=3, raise_exception=False)
    ref_los = [
        {
            "l": 0,
            "wf": [
                {"matchingOrder": 1, "n": 2, "searchE": False},
                {"matchingOrder": 2, "n": 2, "trialEnergy": 0.15, "searchE": False},
            ],
        },
        {"l": 1, "wf": [{"matchingOrder": 0, "n": 3, "searchE": True}, {"matchingOrder": 1, "n": 3, "searchE": False}]},
        {
            "l": 0,
            "wf": [{"matchingOrder": 2, "searchE": False, "n": 2}, {"matchingOrder": 3, "searchE": False, "n": 2}],
        },
        {
            "l": 1,
            "wf": [{"matchingOrder": 1, "searchE": False, "n": 3}, {"matchingOrder": 2, "searchE": False, "n": 3}],
        },
    ]
    assert ref_los == species_C.basis["lo"], "Adding lo for higher matchingOrder failed for l=1, n=3"

    species_C.add_lo_higher_matching_order(l=1, n=2, raise_exception=False, search_e=True)
    ref_los = [
        {
            "l": 0,
            "wf": [
                {"matchingOrder": 1, "n": 2, "searchE": False},
                {"matchingOrder": 2, "n": 2, "trialEnergy": 0.15, "searchE": False},
            ],
        },
        {"l": 1, "wf": [{"matchingOrder": 0, "n": 3, "searchE": True}, {"matchingOrder": 1, "n": 3, "searchE": False}]},
        {
            "l": 0,
            "wf": [{"matchingOrder": 2, "searchE": False, "n": 2}, {"matchingOrder": 3, "searchE": False, "n": 2}],
        },
        {
            "l": 1,
            "wf": [{"matchingOrder": 1, "searchE": False, "n": 3}, {"matchingOrder": 2, "searchE": False, "n": 3}],
        },
        {"l": 1, "wf": [{"matchingOrder": 0, "searchE": True, "n": 2}, {"matchingOrder": 1, "searchE": True, "n": 2}]},
    ]
    assert ref_los == species_C.basis["lo"], "Adding lo for higher matchingOrder failed for l=1, n=2"


def test_add_lo(species_C):
    species_C.add_lo(l=1, ns=(2, 2), matching_orders=(0, 1), raise_exception=False)
    ref_los = [
        {
            "l": 0,
            "wf": [
                {"matchingOrder": 1, "n": 2, "searchE": False},
                {"matchingOrder": 2, "n": 2, "trialEnergy": 0.15, "searchE": False},
            ],
        },
        {"l": 1, "wf": [{"matchingOrder": 0, "n": 3, "searchE": True}, {"matchingOrder": 1, "n": 3, "searchE": False}]},
        {
            "l": 1,
            "wf": [{"matchingOrder": 0, "searchE": False, "n": 2}, {"matchingOrder": 1, "searchE": False, "n": 2}],
        },
    ]
    assert ref_los == species_C.basis["lo"], "Adding lo failed for l=1 for n=2 with m0 = [0, 1]"

    species_C.add_lo(l=0, ns=(2, 2), matching_orders=(3, 4), raise_exception=False)
    assert ref_los == species_C.basis["lo"], "Adding lo failed for l=1 for n=2 with m0 = [3, 4]"

    species_C.add_lo(l=3, ns=(4, 4), matching_orders=(0, 1), raise_exception=False, search_e=True)
    ref_los = [
        {
            "l": 0,
            "wf": [
                {"matchingOrder": 1, "n": 2, "searchE": False},
                {"matchingOrder": 2, "n": 2, "trialEnergy": 0.15, "searchE": False},
            ],
        },
        {"l": 1, "wf": [{"matchingOrder": 0, "n": 3, "searchE": True}, {"matchingOrder": 1, "n": 3, "searchE": False}]},
        {
            "l": 1,
            "wf": [{"matchingOrder": 0, "searchE": False, "n": 2}, {"matchingOrder": 1, "searchE": False, "n": 2}],
        },
        {"l": 3, "wf": [{"matchingOrder": 0, "searchE": True, "n": 4}, {"matchingOrder": 1, "searchE": True, "n": 4}]},
    ]
    assert ref_los == species_C.basis["lo"], "Adding lo failed for l=3 for n=4 with m0 = [0, 1]"


def test_remove_lo(species_C):
    species_C.remove_lo(l=0, ns=(2, 2), matching_orders=(1, 2), raise_exception=False)
    ref_los = [
        {"l": 1, "wf": [{"matchingOrder": 0, "n": 3, "searchE": True}, {"matchingOrder": 1, "n": 3, "searchE": False}]}
    ]
    assert ref_los == species_C.basis["lo"], (
        "Removed lo failed for l=0 for n=2 with m0 = [1, 2] with raise_exception=False"
    )

    species_C.remove_lo(l=1, ns=(3, 3), matching_orders=(0, 1), raise_exception=False)
    ref_los = []
    assert ref_los == species_C.basis["lo"], "Removed lo failed for l=1 for n=3 with m0 = [0, 1]"

    try:
        species_C.remove_lo(l=1, ns=(3, 3), matching_orders=(0, 1), raise_exception=True)
        pytest.fail("Expected ValueError not raised when removing non-existent local orbital")
    except ValueError as e:
        assert str(e) == "Could not remove local orbital.", "Unexpected error message when removing lo"


serialization_ref_dict = {
    "@class": "SpeciesFile",
    "@module": "excitingtools.species.species_file",
    "@version": excitingtools.__version__,
    "atomic_states": [
        {"core": True, "kappa": 1, "l": 0, "n": 1, "occ": 2.0},
        {"core": False, "kappa": 1, "l": 0, "n": 2, "occ": 2.0},
        {"core": False, "kappa": 1, "l": 1, "n": 2, "occ": 1.0},
        {"core": False, "kappa": 2, "l": 1, "n": 2, "occ": 1.0},
    ],
    "basis": {
        "custom": [
            {"l": 0, "n": 2, "searchE": False, "type": "apw"},
            {"l": 1, "n": 2, "searchE": False, "type": "apw"},
        ],
        "default": [{"searchE": False, "trialEnergy": 0.15, "type": "apw"}],
        "lo": [
            {
                "l": 0,
                "wf": [
                    {"matchingOrder": 1, "n": 2, "searchE": False},
                    {"matchingOrder": 2, "n": 2, "searchE": False, "trialEnergy": 0.15},
                ],
            },
            {
                "l": 1,
                "wf": [{"matchingOrder": 0, "n": 3, "searchE": True}, {"matchingOrder": 1, "n": 3, "searchE": False}],
            },
        ],
    },
    "muffin_tin": {"radialmeshPoints": 250, "radius": 1.45, "rinf": 21.09, "rmin": 1e-05},
    "species": {"chemicalSymbol": "C", "mass": 21.16, "name": "carbon", "z": -6.0},
}


def test_as_dict(species_C: SpeciesFile):
    pytest.importorskip("monty", reason="Serialisation requires monty.")
    assert species_C.as_dict() == serialization_ref_dict, "as_dict() test failed"


def test_from_dict(species_C: SpeciesFile):
    pytest.importorskip("monty", reason="Serialisation requires monty.")
    new_species_file = species_C.from_dict(species_C.as_dict())
    assert new_species_file.species == {"chemicalSymbol": "C", "mass": 21.16, "name": "carbon", "z": -6.0}
    assert new_species_file.muffin_tin == {"radialmeshPoints": 250, "radius": 1.45, "rinf": 21.09, "rmin": 1e-05}
    assert new_species_file.atomic_states[0] == {"core": True, "kappa": 1, "l": 0, "n": 1, "occ": 2.0}
    assert set(new_species_file.basis) == {"default", "custom", "lo"}
