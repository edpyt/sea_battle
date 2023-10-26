from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .user import User


class Game(Base):
    __tablename__ = 'games'
    
    id: Mapped[int] = mapped_column(
        'id', autoincrement=True, nullable=False, unique=True, primary_key=True
    )
    player_1_id: Mapped[int] = mapped_column(
        'player_1_id', ForeignKey('users.id'), nullable=False
    )
    player_2_id: Mapped[int] = mapped_column(
        'player_2_id', ForeignKey('users.id'), nullable=False
    )


class GameEnds(Base):
    __tablename__ = 'gamesends'

    id: Mapped[int] = mapped_column(
        'id', autoincrement=True, nullable=False, unique=True, primary_key=True
    )
    game_id: Mapped[int] = mapped_column(
        'game_id', ForeignKey('games.id'), nullable=False
    )

    winner: Mapped[int] = mapped_column(
        'winner', ForeignKey('users.id'), nullable=False
    )
    looser: Mapped[int] = mapped_column(
        'looser', ForeignKey('users.id'), nullable=False
    )