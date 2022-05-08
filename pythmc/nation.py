from __future__ import annotations
from typing import Set, Tuple

from . import get
from .nova import Nation, Town, Resident
from .aurora import Nation, Town, Resident


class BaseNation:
    name: str
    towns: Set[Town]
    capital: Town
    leader: Resident
    colour: str
    citizens: Set[Resident]
    area: int

    def __init__(self, name: str, *, data: Tuple[dict, dict] = None):
        if data is None:
            data = self.get_data()
        towns = [town for town in data[0] if data[0][town]["desc"][0][:-1].split(" (")[-1] == name]
        if len(towns) <= 0 or name == "":
            raise NationNotFoundException(f"The nation {name} was not found")
        self.name = name
        self.towns = {Town._with_nation(town, data, self) for town in towns}
        self.capital = next(town for town in self.towns if town.flags["capital"])
        self.leader = self.capital.mayor
        self.colour = self.capital.colour
        self.citizens = {citizen for town in self.towns for citizen in town.residents}
        self.area = sum(town.area for town in self.towns)

    @classmethod
    def all(self, cls, *, data: Tuple[dict, dict] = None) -> Set[Nation]:
        if data is None:
            data = self.get_data()
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

    def get_data(self):
        get.get_data()

class NationNotFoundException(Exception):
    pass