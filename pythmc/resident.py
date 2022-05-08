from __future__ import annotations
from typing import Dict, Set, Tuple
from shapely.geometry import Polygon

from . import get
from .nova import Nation, Town, Resident
from .aurora import Nation, Town, Resident


class BaseResident:
    name: str
    online: bool
    position: Tuple[int, int, int]
    hidden: bool
    town: Town
    nation: Nation
    npc: bool

    def __init__(self, name: str, *, data: Tuple[dict, dict] = None):
        if data is None:
            data = self.get_data()
        res_data = next((person for person in data[1]["players"] if person["account"] == name), None)
        self.name = name
        if res_data is not None:
            self.online = True
            self.position = (res_data["x"], res_data["y"], res_data["z"])
            self.hidden = self.position == (0, 64, 0)
        else:
            self.online = False
            self.position = None
            self.hidden = True
        if not hasattr(self, "town"):
            self.town = next((Town(town_name, data=data) for town_name in data[0] if name in data[0][town_name]["desc"][4]), None)
        if self.town is None:
            self.nation = None
        else:
            self.nation = self.town.nation
        self.npc = self.name.startswith("NPC") and self.name[3:].isdigit()

    @classmethod
    def _with_town(cls, name, data, town):
        resident = cls.__new__(cls)
        resident.town = town
        resident.__init__(name, data=data)
        return resident

    @classmethod
    def all_online(self, cls, *, data: Tuple[dict, dict] = None) -> Set[Resident]:
        if data is None:
            data = self.get_data()
        return {cls(resident["account"], data=data) for resident in data[1]["players"]}

    @classmethod
    def all(self, cls, *, data: Tuple[dict, dict] = None) -> Set[Resident]:
        if data is None:
            data = self.get_data()
        return {resident for town in Town.all(data=data) for resident in town.residents}

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return (
            f"=== {self.name} ===\n"
            f"Online: {self.online}\n"
            f"Position: {self.position}\n"
            f"Hidden: {self.hidden}\n"
            f"Town: {self.town}\n"
            f"Nation: {self.nation}"
        )

    def get_data(self):
        get.get_data()
