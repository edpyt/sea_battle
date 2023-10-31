from typing import Optional

from utils.ship import SHIPS


class ShipCountsOver(Exception):
    ...


class Ship:
    count: int

    def __init__(self, ship_type: str) -> None:
        self.count = SHIPS[ship_type]['count']

    async def pick(self) -> None:
        if not self.count > 0:
            raise ShipCountsOver
        self.count -= 1


class GameBoard:
    ship_types = dict(
        one_cell=Ship('one_cell'),
        two_cell=Ship('two_cell'),
        three_cell=Ship('three_cell'),
        fourth_cell=Ship('fourth_cell')
    )

    async def set_cell_into_game_board(self, ship_type: str) -> None:
        ship: Optional[Ship] = self.ship_types.get(ship_type)
        await ship.pick()


async def place_ship_to_board(game_board: GameBoard, ship_type: str) -> str:
    message: str = 'Ok!'
    try:
        await game_board.set_cell_into_game_board(ship_type)
    except ShipCountsOver:
        message = 'Ships over!'
    except TypeError:
        message = f'Not found ship with type: {ship_type}'
    return message
