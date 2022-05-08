from typing import Tuple, Any, Literal
from re import split
from collections import namedtuple
from requests import get


Bounds = namedtuple("Bounds", ("min_x", "min_y", "max_x", "max_y"))

def map_link(server: Literal["nova", "aurora"], position: Tuple[float, Any, float], zoom: int = 6) -> str:
    return (f"https://earthmc.net/map/{server}/?zoom={zoom}&x={position[0]}&z={position[-1]}")


def get_data(server: Literal["nova", "aurora"]) -> Tuple[dict, dict]:
    resp_town = get(f"https://earthmc.net/map/{server}/tiles/_markers_/marker_earth.json")
    resp_town.raise_for_status()
    resp_player = get(f"https://earthmc.net/map/{server}/up/world/earth/")
    resp_player.raise_for_status()
    town_data = resp_town.json()["sets"]["townyPlugin.markerset"]["areas"]
    towns = {name[:-3].lower(): town[1] for name, town in zip(town_data, town_data.items()) if name.endswith("__0")}
    for town in towns:
        towns[town]["desc"] = [desc for desc in split(r"<[^<>]*>", towns[town]["desc"]) if desc != ""]
    return towns, resp_player.json()
