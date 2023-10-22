from typing import Literal

from utils.ship import SHIPS


class Ship:
    count: int
    ship_type: Literal['']
    
    def __init__(self, ship_type: str) -> None:
        self.ship_type = ship_type
        self.count = SHIPS[ship_type]['count']

    def pick(self) -> 'Ship':
        self.count -= 1


class GameBoard:
    def __init__(self) -> None:
        ...