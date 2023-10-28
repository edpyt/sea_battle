from typing import Optional
from utils.ship import SHIPS


class ShipCountsOver(Exception):
    ...


class Ship:
    count: int
    
    def __init__(self, ship_type: str) -> None:
        self.count = SHIPS[ship_type]['count']

    async def pick(self) -> bool:
        if not self.count > 0:
            raise ShipCountsOver
        self.count -= 1


class GameBoard:
    ship_types = dict(
        one_cell=Ship('one_cell'),
        two_cell=Ship('two_cell'),
        three_cell=Ship('three_cell'),
        fourth_cell = Ship('fourth_cell')
    )

    async def set_cell_into_game_board(self, ship_type: str) -> str:
        ship: Optional[Ship] = self.ship_types.get(ship_type)
        await ship.pick()
