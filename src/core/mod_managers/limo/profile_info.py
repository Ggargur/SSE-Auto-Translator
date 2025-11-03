"""
Copyright (c) Cutleast
"""

from typing import Literal, override

from ..instance_info import InstanceInfo
from ..mod_manager import ModManager


class ProfileInfo(InstanceInfo):
    """
    Class for identifying an limo instance and profile.
    """

    instance_path: str
    """The path of the instance."""

    mod_manager: Literal[ModManager.Limo]

    @override
    def get_mod_manager(self) -> ModManager:
        return self.mod_manager
