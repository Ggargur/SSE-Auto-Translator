from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
import json

@dataclass
class Condition:
    condition_type: str
    invert: bool
    search_string: str
    use_regex: bool


@dataclass
class AutoTag:
    conditions: List[Condition]
    expression: str
    mod_ids: List[int]
    name: str


@dataclass
class LoadOrderEntry:
    enabled: bool
    id: int


@dataclass
class Profile:
    conflict_groups: List[List[int]]
    loadorder: List[LoadOrderEntry]


@dataclass
class Deployer:
    deploy_mode: int
    dest_path: str
    enable_unsafe_sorting: bool
    name: str
    source_path: str
    type: str
    profiles: Optional[List[Profile]] = None


@dataclass
class InstalledMod:
    id: int
    install_time: int
    installer: str
    local_source: str
    name: Optional[str] = None
    version: Optional[str] = None
    enabled: Optional[bool] = None
    modid: Optional[int] = None
    modtype: Optional[str] = None
    url: Optional[str] = None

@dataclass
class LmmMods:
    auto_tags: List[AutoTag]
    command: str
    deployers: List[Deployer]
    installed_mods: List[InstalledMod]

    @staticmethod
    def from_json(path: Path) -> "LmmMods":
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Parse auto_tags
        auto_tags = [
            AutoTag(
                conditions=[Condition(**cond) for cond in tag["conditions"]],
                expression=tag["expression"],
                mod_ids=tag["mod_ids"],
                name=tag["name"],
            )
            for tag in data.get("auto_tags", [])
        ]

        # Parse deployers
        deployers = []
        for dep in data.get("deployers", []):
            profiles = None
            if "profiles" in dep:
                profiles = [
                    Profile(
                        conflict_groups=p["conflict_groups"],
                        loadorder=[LoadOrderEntry(**entry) for entry in p["loadorder"]],
                    )
                    for p in dep["profiles"]
                ]
            deployers.append(
                Deployer(
                    deploy_mode=dep["deploy_mode"],
                    dest_path=dep["dest_path"],
                    enable_unsafe_sorting=dep["enable_unsafe_sorting"],
                    name=dep["name"],
                    source_path=dep["source_path"],
                    type=dep["type"],
                    profiles=profiles,
                )
            )

        # Parse installed_mods
        installed_mods = [
            InstalledMod(**mod)
            for mod in data.get("installed_mods", [])
        ]

        return LmmMods(
            auto_tags=auto_tags,
            command=data.get("command", ""),
            deployers=deployers,
            installed_mods=installed_mods,
        )

    def get_enabled_loadorder(self) -> List[LoadOrderEntry]:
        unique = {}
        for dep in self.deployers:
            if dep.profiles:
                for profile in dep.profiles:
                    for entry in profile.loadorder:
                        if entry.id not in unique and entry.enabled:
                            unique[entry.id] = self.find_mod_by_id(entry.id)
        return list(unique.values())

    def find_mod_by_id(self, mod_id: int) -> Optional[InstalledMod]:
        for mod in self.installed_mods:
            if mod.id == mod_id:
                return mod
        return None

    def to_json(self, path: Path) -> None:
        def encode(obj):
            if hasattr(obj, "__dict__"):
                return obj.__dict__
            if isinstance(obj, list):
                return [encode(o) for o in obj]
            return obj

        with path.open("w", encoding="utf-8") as f:
            json.dump(encode(self), f, indent=4, ensure_ascii=False)
