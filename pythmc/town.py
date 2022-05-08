from __future__ import annotations
from typing import Dict, Set, Tuple
from shapely.geometry import Polygon

from . import get
from .nova import Nation, Town, Resident
from .aurora import Nation, Town, Resident


class BaseTown:
    name: str
    nation: Nation
    colour: str
    mayor: Resident
    residents: list[Resident]
    flags: Dict[str, bool]
    area: int
    position: Tuple[int, int]
    bounds: get.Bounds
    ruins: bool

    def __init__(self, name: str, *, data: Tuple[dict, dict] = None):
        if data is None:
            data = get.get_data()
        name = name.lower()
        if name not in data[0]:
            raise TownNotFoundException(f"The town {name} could not be found")
        self.name = data[0][name]["label"]
        if not hasattr(self, "nation"):
            nation = data[0][name]["desc"][0][:-1].split("(")[-1]
            if nation == "":
                self.nation = None
            else:
                self.nation = Nation(nation, data=data)
        self.colour = data[0][name]["fillcolor"]
        self.mayor = Resident._with_town(data[0][name]["desc"][2], data, self)
        self.residents = [Resident._with_town(person, data, self) for person in data[0][name]["desc"][4].split(", ")]
        self.flags = {
            "pvp": data[0][name]["desc"][7] == "pvp: true",
            "mobs": data[0][name]["desc"][8] == "mobs: true",
            "explosions": data[0][name]["desc"][10] == "explosion: true",
            "fire": data[0][name]["desc"][11] == "fire: true",
            "capital": data[0][name]["desc"][12] == "capital: true"
        }
        polygon = Polygon(zip(data[0][name]["x"], data[0][name]["z"]))
        self.area = int(polygon.area // 256)
        self.bounds = get.Bounds(*map(int, polygon.bounds))
        self.position = ((self.bounds.max_x+self.bounds.min_x) // 2, (self.bounds.max_y+self.bounds.min_y) // 2)
        self.ruins = len(self.residents) == 1 and self.mayor.npc and self.flags == {
            "pvp": True,
            "mobs": True,
            "explosions": True,
            "fire": True,
            "capital": False
        }

    @classmethod
    def _with_nation(cls, name, data, nation):
        town = cls.__new__(cls)
        town.nation = nation
        town.__init__(name, data=data)
        return town

    @classmethod
    def all(cls, *, data: Tuple[dict, dict] = None) -> Set[Town]:
        if data is None:
            data = get.get_data()
        return {cls(town, data=data) for town in data[0]}

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return (
            f"=== {self.name} ===\n"
            f"colour: {self.colour}\n"
            f"mayor: {self.mayor.name}\n"
            f"residents: {','.join([person.name for person in self.residents])}\n"
            f"nation: {self.nation.name}\n"
            f"Area: {self.area}\n"
            f"Position: {self.position}\n"
            f"Bounds: ({self.bounds.min_x}-{self.bounds.max_x}, {self.bounds.min_y}-{self.bounds.max_y})\n"
            f"--- flags ---\n"
            f"pvp: {self.flags['pvp']}\n"
            f"mobs: {self.flags['mobs']}\n"
            f"explosions: {self.flags['explosions']}\n"
            f"fire: {self.flags['fire']}\n"
            f"capital: {self.flags['capital']}"
        )

    def get_data(self):
        get.get_data()

class TownNotFoundException(Exception):
    pass
