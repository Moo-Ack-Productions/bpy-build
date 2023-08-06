from pathlib import Path
from typing import Dict, List
from attrs import define, field, Attribute

"""
Context of the build environment, from settings to 
actions to paths, etc.
"""


# Must be ignored to pass Mypy as this has
# an expression of Any, likely due to how
# attrs works
@define  # type: ignore
class BuildContext:
    """
    Path of the addon source. By default, it is
    assumed to be at the root of the current working
    directory.
    """

    addon_path: Path = field(default=Path("."))
    build_name: str = field(default="")
    install_versions: List[float] = field(default=[])
    actions: Dict[str, str] = field(default={})

    """
    Validator for install_versions since isinstance doesn't 
    support generics. This iterates through all versions defined 
    and checks to see if they're a float. In the future, we may also
    check to see if the version itself is valid.
    """

    @install_versions.validator
    def install_versions_check(self, _: Attribute, value: List[float]) -> None:
        for ver in value:
            if not isinstance(ver, float):
                raise ValueError(
                    f"Expected a list of floats for install_versions!, found {ver}"
                )

    """
    Validator for actions since isinstance doesn't 
    support generics. This iterates through all key-value 
    pairs defined in actions and checks to see if they are 
    strings.
    """

    @actions.validator
    def action_check(self, _: Attribute, value: Dict[str, str]) -> None:
        for key in value:
            if not isinstance(key, str):
                raise ValueError(
                    f"Expected a dictionary of strings to strings, found {key} as a key!"
                )
            if not isinstance(value[key], str):
                raise ValueError(
                    f"Expected a dictionary of strings to strings, found {value[key]} as a value!"
                )
