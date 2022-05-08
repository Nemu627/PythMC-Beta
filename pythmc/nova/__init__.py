from pythmc.nation import BaseNation
from pythmc.town import BaseTown
from pythmc.resident import BaseResident
from .. import get

from typing import Tuple


class Nation(BaseNation):
    def __init__(self, name: str, *, data: Tuple[dict, dict] = None):
        super().__init__(name, data)

    def get_data(self):
        get.get_data("nova")

class Town(BaseTown):
    def __init__(self, name: str, *, data: Tuple[dict, dict] = None):
        super().__init__(name, data)

    def get_data(self):
        get.get_data("nova")

class Resident(BaseResident):
    def __init__(self, name: str, *, data: Tuple[dict, dict] = None):
        super().__init__(name, data)

    def get_data(self):
        get.get_data("nova")
