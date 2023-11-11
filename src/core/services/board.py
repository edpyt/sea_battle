import logging
from operator import itemgetter
from string import ascii_uppercase
from typing import Callable

logger = logging.getLogger(__name__)


class ShipAlreadyPlacedHere(Exception):
    ...


class ShipsOver(Exception):
    ...


class HaveBeenMoveHere(Exception):
    ...


class Cell:
    """Class cell for a game board"""
    value: bool = False
    cells: int = 0


class Ship:
    """
    Ship class

    Args:
        ship_type(str): Ship type from a SHIP_TYPES dict,
        vertical(bool): Is ship placed vertical for a Cell class.
    """
    ship_type: int
    number: int
    cells: int
    value: bool = True

    def __init__(self, ship_type: int, number: int, cells: int) -> None:
        self.ship_type = ship_type
        self.number = number
        self.cells = cells

    def __hash__(self) -> int:
        return hash(self.number)


class GameBoardConfig:
    GAME_LETTERS = 'ABCDEFGHIJ'
    GAME_CELLS_STR = '▒', '■'


class GameBoardPickShip(GameBoardConfig):
    def pick(self, ship_type: int) -> Ship:
        if self.ships[ship_type]['amount'] <= 0:  # type: ignore
            raise ShipsOver()
        cells = self.ships[ship_type]['cells']  # type: ignore

        return Ship(
            ship_type=ship_type,
            number=self.ship_counter[ship_type],  # type: ignore
            cells=cells
        )


class GameBoardSetShip(GameBoardPickShip):
    def set_ship_into_game_board(
        self, ship: int | Ship, x: str, y: int, vertical: bool = False
    ) -> bool:
        """
        Set ship on game board

        Args:
            ship_type(int | Ship): Ship type,
            vertical(bool): Is placed ship vertical or not.
        Returns:
            is_placed(bool): Is ship placed on board.
        """
        if isinstance(ship, int):
            ship = self.pick(ship)
        is_placed: bool = self.place_ship_if_available(ship, x, y, vertical)
        if is_placed:
            self.ships[ship.ship_type]['amount'] -= 1  # type: ignore
            self.ship_counter[ship.ship_type] += 1  # type: ignore
            self._ships_placed.append(ship)  # type: ignore
        return is_placed

    def place_ship_if_available(
        self, ship: Ship, x: str, y: int, vertical: bool
    ) -> bool:
        """
        Check if ship can be placed at coordinates

        Args:
            x(str): X coordinate,
            y(str): Y coordinate,
            vertical(bool): Is Ship vertical.
        Returns:
            is_placed(bool): Is ship placed on board.
        """
        res: bool = False
        try:
            self._check_if_cells_available(ship, x, y, vertical)
        except KeyError:
            logger.error(
                f'Error to get key from dictionary game board cords: {x}, {y}'
            )
        except IndexError:
            logger.error(f'Error get index from GAME_LETTERS cords: {x}, {y}')
        except ShipAlreadyPlacedHere:
            logger.error(f'Ship was already placed here! cords: {x}, {y}')
        else:
            res = True
            self._check_if_cells_available(ship, x, y, vertical, place=True)
        return res

    def _check_if_cells_available(
        self,
        ship: Ship,
        x: str,
        y: int,
        vertical: bool,
        place: bool = False
    ) -> None:
        place_func: Callable = (
            self._vertical_place if vertical else self._horizontal_place
        )
        place_func(ship, x, y, place)

    def _horizontal_place(
        self, ship: Ship, x: str, y: int, place: bool
    ) -> None:
        placing_start_idx: int = self.GAME_LETTERS.index(x)

        for cell_numb in range(ship.cells):
            placing_idx: str = self.GAME_LETTERS[placing_start_idx + cell_numb]
            if self.game_board[placing_idx][y].value:  # type: ignore
                raise ShipAlreadyPlacedHere()
            if place:
                self.game_board[placing_idx][y] = ship  # type: ignore

    def _vertical_place(
        self, ship: Ship, x: str, y: int, place: bool
    ) -> None:
        for cell_numb in range(ship.cells):
            placing_idx: int = y + cell_numb
            if self.game_board[x][placing_idx].value:  # type: ignore
                raise ShipAlreadyPlacedHere()
            if place:
                self.game_board[x][placing_idx] = ship  # type: ignore


class GameBoardPlayerMove(GameBoardSetShip):
    moves: dict[Cell | Ship, list[tuple[str, int]]] = {}

    def attack(self, x: str, y: int) -> bool:
        """
        Player movement method

        Args:
            x(str): X coordinate,
            y(str): Y coordinate.
        Returns:
            is_hited(bool): Is player hit the ship.
        """
        cell: Cell | Ship = self.game_board[x][y]  # type: ignore
        self.moves.setdefault(cell, [])

        if (x, y) in self.moves[cell]:
            raise HaveBeenMoveHere()

        is_hited: bool = cell.value

        if is_hited:
            self.moves[cell].append((x, y))
            self.check_is_drowned(cell)
        return is_hited

    def check_is_drowned(self, ship: Ship | Cell) -> bool:
        """
        Ship is drowned check

        Args:
            ship(Ship): Cell of the ship in game board
        """
        return len(self.moves[ship]) == ship.cells


class GameBoardGame(GameBoardPlayerMove):
    def _init_game_board(self, size: int = 10) -> None:
        """
        Main function for initialize default game board
        """
        self.GAME_LETTERS = ascii_uppercase[:size + 1]
        self.game_board = {
            letter: {numb: Cell() for numb in range(1, size + 1)}
            for letter in self.GAME_LETTERS
        }
        self.size = size
        self.ships: dict[int, dict[str, int]] = {
            1: {'amount': 4, 'cells': 1},
            2: {'amount': 3, 'cells': 2},
            3: {'amount': 2, 'cells': 3},
            4: {'amount': 1, 'cells': 4}
        }
        self._ships_placed: list[Ship] = []
        self.ship_counter: dict[str, int] = dict(
            zip(self.ships.keys(), iter(int, 1))  # type: ignore
        )

    @property
    def is_all_ships_placed_and_game_initialized(self) -> bool:
        ships_amounts = map(itemgetter('amount'), self.ships.values())
        res = (
            all(amount == 0 for amount in ships_amounts)
            and self.GAME_LETTERS == ''.join(self.game_board.keys())
        )
        print(res)
        return res

    @property
    def is_game_over(self) -> bool:
        return all(
            self.moves.get(ship) and self.check_is_drowned(ship)
            for ship in self._ships_placed
        )

    def print_board(self) -> None:
        print(' '.join(self.game_board))
        for i in range(1, self.size + 1):
            for game_x in self.GAME_LETTERS:
                game_cell: Cell | Ship = self.game_board[game_x][i]
                if (hits := self.moves.get(game_cell)) and (game_x, i) in hits:
                    print('X', end=' ')
                else:
                    print(game_cell.cells, end=' ')
            print()


class GameBoard(GameBoardGame):
    """The main class for the playing field of the game"""
    def __init__(self) -> None:
        self._init_game_board()
        self.is_turn = False


if __name__ == '__main__':
    mg1 = GameBoard()

    mg1.set_ship_into_game_board(1, 'D', 7, True)
    mg1.set_ship_into_game_board(1, 'D', 3, True)
    mg1.set_ship_into_game_board(1, 'D', 4, True)
    mg1.set_ship_into_game_board(1, 'D', 5, True)

    mg1.set_ship_into_game_board(2, 'D', 1, True)
    mg1.set_ship_into_game_board(2, 'E', 5)
    mg1.set_ship_into_game_board(2, 'F', 1, True)

    mg1.set_ship_into_game_board(3, 'J', 1, True)
    mg1.set_ship_into_game_board(3, 'C', 1, True)

    mg1.set_ship_into_game_board(4, 'B', 1, True)

    mg1.print_board()
    print(
        'Is board for user 1 initialized:',
        mg1.is_all_ships_placed_and_game_initialized
    )

    mg2 = GameBoard()

    mg2.set_ship_into_game_board(1, 'D', 7, False)
    mg2.set_ship_into_game_board(1, 'D', 3, False)
    mg2.set_ship_into_game_board(1, 'D', 4, False)
    mg2.set_ship_into_game_board(1, 'D', 5, False)

    mg2.set_ship_into_game_board(2, 'D', 1, False)
    mg2.set_ship_into_game_board(2, 'E', 5, False)
    mg2.set_ship_into_game_board(2, 'F', 1, False)

    mg2.set_ship_into_game_board(3, 'J', 1, True)
    mg2.set_ship_into_game_board(3, 'C', 1, True)

    mg2.set_ship_into_game_board(4, 'J', 4, True)

    mg2.print_board()
    print(
        'Is board for user 2 initialized:',
        mg2.is_all_ships_placed_and_game_initialized
    )

    if (
        not mg1.is_all_ships_placed_and_game_initialized
        or not mg2.is_all_ships_placed_and_game_initialized
    ):
        raise ValueError('The game is not initialized!')

    mg2.print_board()

    while not mg2.is_game_over:
        command = input()

        if 'board' in command.lower():
            mg2.print_board()
            continue

        x, y = list(command)

        x = x.upper()
        y = int(y)  # type: ignore

        mg2.attack(x, y)  # type: ignore
    print('Game Over!')
