"""
Test gw DOS parser, returning to an object.
Execute tests from exciting_tools directory:
pytest --capture=tee-sys
"""

import numpy as np
import pytest

from excitingtools.exciting_obj_parsers.gw_eigenvalues import parse_obj_gw_dos
from excitingtools.utils.test_utils import MockFile


@pytest.fixture
def gw_dos_mock(tmp_path) -> MockFile:
    """Mock TDOS.OUT data for 15 energy and DOS value pairs"""
    dos_str = """-0.5000000000  0.000000000
    -0.4949748744  0.000000000
    -0.4899497487  0.000000000
    -0.4849246231  0.000000000
    -0.4798994975  0.000000000
    -0.4748743719  0.000000000
    -0.4698492462  0.000000000
    -0.4648241206  0.000000000
    -0.4597989950  0.000000000
    -0.4547738693  0.000000000
    -0.4497487437  0.1025457101E-01
    -0.4447236181  0.1050068072
    -0.4396984925  0.3502961458
    -0.4346733668  0.6899275378
    -0.4296482412  1.164919267
    """
    dos_file = tmp_path / "TDOS.OUT"
    dos_file.write_text(dos_str)
    return MockFile(dos_file, dos_str)


def test_parse_obj_gw_dos(gw_dos_mock):
    """Test that the parser correctly returns to the DOS object."""
    data = parse_obj_gw_dos(gw_dos_mock.file)

    ref_energies = np.array(
        [
            -0.5000000000,
            -0.4949748744,
            -0.4899497487,
            -0.4849246231,
            -0.4798994975,
            -0.4748743719,
            -0.4698492462,
            -0.4648241206,
            -0.4597989950,
            -0.4547738693,
            -0.4497487437,
            -0.4447236181,
            -0.4396984925,
            -0.4346733668,
            -0.4296482412,
        ]
    )
    ref_dos = np.array(
        [
            0.000000000,
            0.000000000,
            0.000000000,
            0.000000000,
            0.000000000,
            0.000000000,
            0.000000000,
            0.000000000,
            0.000000000,
            0.000000000,
            0.1025457101e-01,
            0.1050068072,
            0.3502961458,
            0.6899275378,
            1.164919267,
        ]
    )

    assert np.allclose(data.energy, ref_energies)
    assert np.allclose(data.dos, ref_dos)
