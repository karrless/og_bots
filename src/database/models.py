from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class User(Base):
    __tablename__ = 'users'
    peer_id: Mapped[int] = mapped_column(primary_key=True)
    screen_name: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    faculty: Mapped[str] = mapped_column(nullable=True)
    group: Mapped[str] = mapped_column(nullable=True)
    room = relationship('Room', backref='users')
    room_id: Mapped[int] = mapped_column(ForeignKey('rooms.id'), nullable=True)
    comfort = relationship('Comfort', backref='users')
    comfort_name: Mapped[int] = mapped_column(ForeignKey('comforts.name'), nullable=True)


class Comfort(Base):
    __tablename__ = 'comforts'
    name: Mapped[str] = mapped_column(primary_key=True)
    first: Mapped[int] = mapped_column(nullable=False)
    second: Mapped[int] = mapped_column(nullable=False)
    third: Mapped[int] = mapped_column(nullable=True)
    rooms = relationship('Room', backref='comfort')


class Room(Base):
    __tablename__ = 'rooms'
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(unique=False)
    comfort_name: Mapped[str] = mapped_column(ForeignKey('comforts.name'), nullable=True)

