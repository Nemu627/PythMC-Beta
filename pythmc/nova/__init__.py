from __future__ import annotations
from typing import Dict, Set, Tuple
from shapely.geometry import Polygon
import get

class Nation:
    name: str
    towns: Set[Town]
    capital: Town
    leader: Resident
    colour: str
    citizens: Set[Resident]
    area: int

    def __init__(self, name: str, *, data: Tuple[dict, dict] = None):
        if data is None:
            data = get.get_data()
        towns = [town for town in data[0] if data[0][town]["desc"][0][:-1].split(" (")[-1] == name]
        if len(towns) <= 0 or name == "":
            raise NationNotFoundException(f"The nation {name} was not found")
        self.name = name
        self.towns = {town.Town._with_nation(town, data, self) for town in towns}
        self.capital = next(town for town in self.towns if town.flags["capital"])
        self.leader = self.capital.mayor
        self.colour = self.capital.colour
        self.citizens = {citizen for town in self.towns for citizen in town.residents}
        self.area = sum(town.area for town in self.towns)

    @classmethod
    def all(cls, *, data: Tuple[dict, dict] = None) -> Set[Nation]:
        if data is None:
            data = get.get_data()
        return {cls(nation, data=data) for nation in {data[0][town]["desc"][0][:-1].split(" (")[-1] for town in data[0]} if nation != ""}

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return (
            f"=== {self.name} ===\n"
            f"Towns: {', '.join([town.name for town in self.towns])}\n"
            f"Capital: {self.capital.name}\n"
            f"Leader: {self.leader.name}\n"
            f"Colour: {self.colour}\n"
            f"Citizens: {','.join([citizen.name for citizen in self.citizens])}\n"
            f"Area: {self.area}\n"
        )

class NationNotFoundException(Exception):
    pass

class Town:
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

class TownNotFoundException(Exception):
    pass


class Resident:
    name: str
    online: bool
    position: Tuple[int, int, int]
    hidden: bool
    town: Town
    nation: Nation
    npc: bool

    def __init__(self, name: str, *, data: Tuple[dict, dict] = None):
        if data is None:
            data = get.get_data()
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
    def all_online(cls, *, data: Tuple[dict, dict] = None) -> Set[Resident]:
        if data is None:
            data = get.get_data()
        return {cls(resident["account"], data=data) for resident in data[1]["players"]}

    @classmethod
    def all(cls, *, data: Tuple[dict, dict] = None) -> Set[Resident]:
        if data is None:
            data = get.get_data()
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