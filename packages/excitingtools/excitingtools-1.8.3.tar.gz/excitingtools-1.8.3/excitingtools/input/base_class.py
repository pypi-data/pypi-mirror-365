"""Base class for exciting input classes."""

import importlib
import re
import warnings
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Iterator, Type, TypeVar, Union
from xml.etree import ElementTree

import numpy as np

from excitingtools.exciting_dict_parsers.input_parser import parse_element_xml
from excitingtools.utils import valid_attributes as all_valid_attributes
from excitingtools.utils.dict_utils import check_valid_keys
from excitingtools.utils.serialization_utils import deserialize_object, special_serialization_attrs
from excitingtools.utils.utils import flatten_list, list_to_str

path_type = Union[str, Path]
ExcitingInputType = TypeVar("ExcitingInputType", bound="AbstractExcitingInput")


class AbstractExcitingInput(ABC):
    """Base class for exciting inputs.

    name: Used as tag for the xml subelement
    """

    name: str = "ABSTRACT"  # not directly used, need a value here because of the dynamic class list

    @abstractmethod
    def __init__(self, **kwargs): ...

    def __repr__(self) -> str:
        return f"{self.__class__.__module__}.{self.__class__.__name__}({self.to_xml_str()})"

    def __str__(self) -> str:
        return self.to_xml_str()

    @abstractmethod
    def to_xml(self) -> ElementTree:
        """Convert class attributes to XML ElementTree."""

    def to_xml_str(self) -> str:
        """Convert attributes to XML tree string."""
        return ElementTree.tostring(self.to_xml(), encoding="unicode", method="xml")

    def as_dict(self) -> dict:
        """Convert attributes to dictionary."""
        serialise_attrs = special_serialization_attrs(self)
        inp_d = parse_element_xml(self.to_xml())
        return {**serialise_attrs, **inp_d}

    @classmethod
    def from_xml(cls: Type[ExcitingInputType], xml_string: path_type) -> ExcitingInputType:
        """Initialise class instance from XML-formatted string.

        Example Usage
        --------------
        xs_input = ExcitingXSInput.from_xml(xml_string)
        """
        return cls(**parse_element_xml(xml_string, tag=cls.name))

    @classmethod
    def from_dict(cls: Type[ExcitingInputType], d: dict) -> ExcitingInputType:
        """Recreates class instance from dictionary."""
        # Keep backward compatibility with version 1.7.x and prior
        if "xml_string" in d:
            return cls.from_xml(d["xml_string"])
        return deserialize_object(cls, d)


class ExcitingXMLInput(AbstractExcitingInput, ABC):
    """Base class for exciting inputs, with exceptions being title, plan, qpointset, kstlist and etCoeffComponents,
    because they are not passed as a dictionary."""

    # Convert python data to string, formatted specifically for exciting
    _attributes_to_input_str = {
        int: lambda x: str(x),
        np.int64: lambda x: str(x),
        np.float64: lambda x: str(x),
        float: lambda x: str(x),
        bool: lambda x: str(x).lower(),
        str: lambda x: x,
        list: list_to_str,
        tuple: list_to_str,
        np.ndarray: list_to_str,
    }

    def __init__(self, **kwargs):
        """Initialise class attributes with kwargs.

        Rather than define all options for a given method, pass as kwargs and directly
        insert as class attributes.

        Valid attributes, subtrees and mandatory attributes are taken automatically from
        the parsed schema, see [valid_attributes.py](excitingtools/utils/valid_attributes.py).
        """
        valid_attributes, valid_subtrees, mandatory_keys, multiple_children = self.get_valid_attributes()

        # check the keys
        missing_mandatory_keys = mandatory_keys - set(kwargs.keys())
        if missing_mandatory_keys:
            raise ValueError(f"Missing mandatory arguments: {missing_mandatory_keys}")
        check_valid_keys(kwargs.keys(), valid_attributes | set(valid_subtrees), self.name)

        # initialise the subtrees
        subtree_class_map = self._class_dict_excitingtools()
        subtrees = set(kwargs.keys()) - valid_attributes
        single_subtrees = subtrees - multiple_children
        multiple_subtrees = subtrees - single_subtrees
        for subtree in single_subtrees:
            kwargs[subtree] = self._initialise_subelement_attribute(subtree_class_map[subtree], kwargs[subtree])
        for subtree in multiple_subtrees:
            kwargs[subtree] = [
                self._initialise_subelement_attribute(subtree_class_map[subtree], x) for x in kwargs[subtree]
            ]
        # check attribute types
        attributes = set(kwargs.keys()) - subtrees
        for attribute in attributes:
            self._check_attribute_type(attribute, kwargs[attribute])

        # Set attributes from kwargs
        self.__dict__.update(kwargs)

    def __setattr__(self, name: str, value: Any):
        """Overload the attribute setting in python with instance.attr = value to check for validity in the schema.

        :param name: name of the attribute
        :param value: new value, can be anything
        """
        valid_attributes, valid_subtrees, _, multiple_children = self.get_valid_attributes()
        check_valid_keys({name}, valid_attributes | set(valid_subtrees), self.name)
        subtree_class_map = self._class_dict_excitingtools()

        # check attribute type
        if name in valid_attributes:
            self._check_attribute_type(name, value)
        # If value is a dictionary, we convert it to the expected input class
        elif isinstance(value, dict):
            value = subtree_class_map[name](**value)
        # Handle subtrees that can occur multiple times
        elif isinstance(value, list) and name in multiple_children:
            value = [self._initialise_subelement_attribute(subtree_class_map[name], x) for x in value]
        # if we enter this branch, we expect a valid ExcitingElementInput object
        elif not isinstance(value, subtree_class_map[name]):
            raise TypeError(
                f"Expected {subtree_class_map[name]} for {name}, but got {type(value)}!\n"
                f"Alternatively you can pass a (possible empty) dictionary."
            )

        super().__setattr__(name, value)

    def __delattr__(self, name: str):
        mandatory_keys = list(self.get_valid_attributes())[2]
        if name in mandatory_keys:
            warnings.warn(f"Attempt to delete mandatory attribute '{name}' was prevented.")
        else:
            super().__delattr__(name)

    def get_valid_attributes(self) -> Iterator:
        """Extract the valid attributes, valid subtrees, mandatory attributes and multiple children
        from the parsed schema.

        :return: valid attributes, valid subtrees, mandatory attributes and multiple children
        """
        yield set(getattr(all_valid_attributes, f"{self.name}_attribute_types", set()))
        yield getattr(all_valid_attributes, f"{self.name}_valid_subtrees", [])
        yield set(getattr(all_valid_attributes, f"{self.name}_mandatory_attributes", set()))
        yield set(getattr(all_valid_attributes, f"{self.name}_multiple_children", set()))

    @staticmethod
    def _class_dict_excitingtools() -> Dict[str, Type[AbstractExcitingInput]]:
        """Find all exciting input classes in own module and excitingtools. Return dict with name and class."""
        excitingtools_namespace_content = importlib.import_module("excitingtools").__dict__
        input_class_namespace_content = importlib.import_module("excitingtools.input.input_classes").__dict__
        all_contents = {**excitingtools_namespace_content, **input_class_namespace_content}.values()
        class_list = [cls for cls in all_contents if isinstance(cls, type) and issubclass(cls, AbstractExcitingInput)]
        return {cls.name: cls for cls in class_list}

    @staticmethod
    def _initialise_subelement_attribute(xml_class, element):
        """Initialize given elements to the ExcitingXSInput constructor. If element is already ExcitingXMLInput class
        object, nothing happens. Else the class constructor of the given XMLClass is called. For a passed
        dictionary the dictionary is passed as kwargs.
        """
        if isinstance(element, xml_class):
            return element
        if isinstance(element, dict):
            # assume kwargs
            return xml_class(**element)
        # Assume the element type is valid for the class constructor
        return xml_class(element)

    def get_attribute_types(self) -> Dict:
        """Extract the expected types of the valid attributes from the parsed schema.

        :return: dictionary associating the attribute name with its expected type and number of expected values or its
        valid choices.
        """
        return getattr(all_valid_attributes, f"{self.name}_attribute_types", {})

    def _check_attribute_type(self, name: str, value: Any):
        """Check if the given attribute name and value are compatible. Raises TypeError or ValueError if a mismatch is
        detected.

        :param name: name of the attribute
        :param value: value, which should be assigned to the attribute
        """
        expected_type, further_info = self.get_attribute_types()[name]
        if expected_type is float:
            # if we expect a float, we also expect int
            expected_type = (int, float, np.integer, np.floating)
        elif expected_type is int:
            expected_type = (int, np.integer)
        if isinstance(further_info, int) and further_info > 1 and not isinstance(value, (list, tuple, np.ndarray)):
            raise TypeError(f"Expected a list, tuple or ndarray for attribute {name} but got {type(value)}!")
        if isinstance(value, (list, tuple, np.ndarray)):
            if not (isinstance(further_info, int) and further_info > 1):
                raise TypeError(f"Expected a single value for attribute {name}, but found a list or tuple!")
            if len(value) != further_info:
                raise ValueError(
                    f"Expected a list of length {further_info} for attribute {name} but got one of length {len(value)}!"
                )
            for i, v in enumerate(value):
                if not isinstance(v, expected_type):
                    raise TypeError(
                        f"Expected all elements of the list to be of type {expected_type} but found {type(v)}"
                        f" at index {i}!"
                    )
            # if all asserts passes we are done and the list value is valid
            return
        if not isinstance(value, expected_type):
            raise TypeError(f"Expected value for {name} to be of type {expected_type} but found {type(value)}!")
        if isinstance(further_info, list) and value not in further_info:
            raise ValueError(f"{value} is not a valid choice for {name}!\nValid choices are: {', '.join(further_info)}")

    def to_xml(self) -> ElementTree:
        """Put class attributes into an XML tree, with the element given by self.name.

        Example ground state XML subtree:
           <groundstate vkloff="0.5  0.5  0.5" ngridk="2 2 2" mixer="msec" </groundstate>

        Note, kwargs preserve the order of the arguments, however the order does not appear to be
        preserved when passed to (or perhaps converted to string) with xml.etree.ElementTree.tostring.

        :return ElementTree.Element sub_tree: sub_tree element tree, with class attributes inserted.
        """
        valid_attributes, valid_subtrees, _, _ = self.get_valid_attributes()

        attributes = {
            key: self._attributes_to_input_str[type(value)](value)
            for key, value in vars(self).items()
            if key in valid_attributes
        }
        xml_tree = ElementTree.Element(self.name, **attributes)

        subtrees = {key: self.__dict__[key] for key in set(vars(self).keys()) - set(attributes.keys())}
        ordered_subtrees = flatten_list([subtrees[x] for x in valid_subtrees if x in subtrees])
        for subtree in ordered_subtrees:
            xml_tree.append(subtree.to_xml())

        # Seems to want this operation on a separate line
        xml_tree.text = " "

        return xml_tree


def query_exciting_version(exciting_root: path_type) -> dict:
    """Query the exciting version.

    Inspect version.inc, which is constructed at compile-time.

    Assumes version.inc has this structure:
     #define GITHASH "1a2087b0775a87059d53"
     #define GITHASH2 "5d01a5475a10f00d0ad7"
     #define COMPILERVERSION "GNU Fortran (MacPorts gcc9 9.3.0_4) 9.3.0"
     #define VERSIONFROMDATE /21,12,01/

    Also checks the src/mod_misc.F90 file for the major exciting version.

    :param exciting_root: exciting root directory.
    :return version: Build and version details
    """
    exciting_root = Path(exciting_root)
    version_inc = exciting_root / "src/version.inc"
    assert version_inc.exists(), f"{version_inc} cannot be found. This file generated when the code is built"

    with open(version_inc) as fid:
        all_lines = fid.readlines()

    git_hash_part1 = all_lines[0].split()[-1][1:-1]
    git_hash_part2 = all_lines[1].split()[-1][1:-1]
    compiler_parts = all_lines[2].split()[2:]
    compiler = " ".join(s for s in compiler_parts).strip()

    mod_misc = exciting_root / "src/mod_misc.F90"
    major_version = re.search(r"character\(40\) :: versionname = '(NEON)'", mod_misc.read_text())[1]

    return {"compiler": compiler[1:-1], "git_hash": git_hash_part1 + git_hash_part2, "major": major_version}
