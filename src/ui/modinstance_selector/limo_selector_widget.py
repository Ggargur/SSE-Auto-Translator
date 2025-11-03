"""
Copyright (c) Cutleast
"""

from pathlib import Path
from typing import override

from cutleast_core_lib.ui.widgets.browse_edit import BrowseLineEdit
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QFileDialog, QGridLayout, QLabel

from core.mod_managers.mod_manager import ModManager
from core.mod_managers.limo.profile_info import ProfileInfo
from core.mod_managers.limo.limo_api import LimoApi

from .base_selector_widget import BaseSelectorWidget


class LimoSelectorWidget(BaseSelectorWidget[ProfileInfo, LimoApi]):
    """
    Class for selecting instances from Limo.
    """

    __instance_dropdown: QComboBox
    __portable_path_entry: BrowseLineEdit
    __profile_dropdown: QComboBox
    __glayout: QGridLayout

    @override
    @staticmethod
    def get_mod_manager() -> ModManager:
        return ModManager.Limo

    @override
    def _init_ui(self) -> None:
        self.__glayout = QGridLayout()
        self.__glayout.setContentsMargins(0, 0, 0, 0)
        self.__glayout.setColumnStretch(0, 1)
        self.__glayout.setColumnStretch(1, 3)
        self.__glayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.__glayout)

        instance_label = QLabel(self.tr("Instance:"))
        self.__glayout.addWidget(instance_label, 0, 0)

        self.__instance_dropdown = QComboBox()
        self.__instance_dropdown.installEventFilter(self)
        self.__instance_dropdown.addItem(self.tr("Please select..."))
        self.__instance_dropdown.addItems(self._instance_names)
        self.__instance_dropdown.addItem("Portable")
        self.__instance_dropdown.currentTextChanged.connect(
            lambda _: self.changed.emit()
        )
        self.__instance_dropdown.currentTextChanged.connect(
            lambda _: self.__update_profile_dropdown()
        )
        self.__glayout.addWidget(self.__instance_dropdown, 0, 1)

        portable_path_label = QLabel(self.tr("Portable path:"))
        self.__glayout.addWidget(portable_path_label, 1, 0)

        self.__portable_path_entry = BrowseLineEdit()
        self.__portable_path_entry.setFileMode(QFileDialog.FileMode.Directory)
        self.__portable_path_entry.textChanged.connect(lambda _: self.changed.emit())
        self.__portable_path_entry.textChanged.connect(
            lambda _: self.__update_profile_dropdown()
        )
        self.__portable_path_entry.setDisabled(True)
        self.__glayout.addWidget(self.__portable_path_entry, 1, 1)

    @override
    def _update(self) -> None:
        self.__instance_dropdown.clear()
        self.__instance_dropdown.addItem(self.tr("Please select..."))
        self.__instance_dropdown.addItems(self._instance_names)
        self.__instance_dropdown.addItem("Portable")
        self.__portable_path_entry.setText("")
        self.__update_profile_dropdown()

    def __update_profile_dropdown(self) -> None:
        self.__portable_path_entry.setDisabled(False)

        self.changed.emit()

    @override
    def validate(self) -> bool:
        valid: bool = (
            self.__instance_dropdown.currentIndex() > 0
            and (
                self.__instance_dropdown.currentText() != "Portable"
                or Path(self.__portable_path_entry.text() + "/lmm_mods.json").is_file()
            )
        )

        return valid

    @override
    def get_instance(self) -> ProfileInfo:
        instance_path: Path = self.__portable_path_entry.getPath()

        if not (instance_path / "lmm_mods.json").is_file():
            raise ValueError(
                f"Invalid instance: {instance_path!r}! Please select a valid Limo instance!"
            )

        return ProfileInfo(
            instance_path=instance_path,
            mod_manager=ModManager.Limo,
        )

    @override
    def set_instance(self, instance_data: ProfileInfo) -> None:
        self.__instance_dropdown.setCurrentText(instance_data.display_name)
        self.__portable_path_entry.setPath(instance_data.instance_path)
        self.changed.emit()

    @override
    def reset(self) -> None:
        self.__instance_dropdown.setCurrentIndex(0)
        self.__portable_path_entry.setText("")
        self.changed.emit()
