from pythmc.nation import BaseNation
from pythmc import get

from typing import Tuple


class Nation(BaseNation):
    def __init__(self, name: str, *, data: Tuple[dict, dict] = None):
        super().__init__(name, data)
        self.get_data = get.get_data("aurora")
