"""
Copyright (c) Cutleast
"""

from pathlib import Path
from typing import Optional, override

from cutleast_core_lib.ui.widgets.loading_dialog import LoadingDialog

from core.mod_instance.mod import Mod
from core.mod_instance.mod_instance import ModInstance
from core.translation_provider.mod_id import ModId
from core.utilities.leveldb import LevelDB

from ..exceptions import InstanceNotFoundError
from ..mod_manager_api import ModManagerApi
from .profile_info import ProfileInfo
from .lmm_mods import LmmMods, InstalledMod


class LimoApi(ModManagerApi[ProfileInfo]):
    """
    Class to load instances and modlists from Limo.
    """

    db_path: Path
    __level_db: LevelDB

    def __init__(self) -> None:
        super().__init__()

    @override
    def get_instance_names(self) -> list[str]:
        return []

    @override
    def load_instance(
        self, instance_data: ProfileInfo, ldialog: Optional[LoadingDialog] = None
    ) -> ModInstance:
        instance_path: Path = instance_data.instance_path

        instance_name: str = instance_path.name

        lmm_mods_path: Path = instance_path / "lmm_mods.json"

        if not lmm_mods_path.is_file:
            raise InstanceNotFoundError(f"{instance_path}")

        self.log.info(f"Loading instance {instance_name!r}!")
        if ldialog is not None:
            ldialog.updateProgress(
                text1=self.tr("Loading mods from {0}...").format(instance_name)
            )

        mods: list[Mod] = self._load_mods(instance_data, ldialog)

        display_name: str = instance_name

        instance = ModInstance(display_name=display_name, mods=mods)

        self.log.info(f"Loaded {instance_name} with {len(mods)} mod(s).")

        return instance

    @override
    def _load_mods(
        self, instance_data: ProfileInfo, ldialog: Optional[LoadingDialog] = None
    ) -> list[Mod]:
        instance_name: str = instance_data.display_name
        profile_name: str = instance_data.profile
        instance_path: Path = instance_data.instance_path

        lmm_mods_path: Path = instance_path / "lmm_mods.json"
        mods_dir: Path = instance_path

        lmm_mods: LmmMods = LmmMods.from_json(lmm_mods_path)
        mods: list[Mod] = []

        installedMods: list[InstalledMod] = lmm_mods.get_enabled_loadorder()

        for m, installedMod in enumerate(installedMods):
            if ldialog is not None:
                ldialog.updateProgress(
                    text1=self.tr("Loading mods from {0} > {1}...").format(
                        instance_name, profile_name
                    )
                    + f" ({m}/{len(installedMods)})",
                    value1=m,
                    max1=len(installedMods),
                    show2=True,
                    text2=installedMod,
                )

            mod_id: int = installedMod.id
            mod_path: Path = mods_dir / mod_id
            version: Optional[str] = installedMod.version

            mod = Mod(
                name=installedMod.name,
                path=mod_path,
                modfiles=[],
                mod_id=self.installed_mod_to_mod_id(
                    installed=installedMod, instance_path=mod_path
                ),
                version=version,
                mod_type=Mod.Type.Regular,
            )
            mods.append(mod)

        self.log.info(f"Loaded {len(mods)} mod(s) from {instance_name}.")

        return mods

    def installed_mod_to_mod_id(installed: InstalledMod, instance_path: Path) -> ModId:
        return ModId(
            mod_id=installed.id,
            file_id=installed.id,
            nm_id=installed.modid,
            nm_game_id="skyrimspecialedition", # placeholder
            installation_file_name=instance_path.resolve(),
        )
