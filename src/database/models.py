from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from . import Base, write


class User(Base):
    __tablename__ = 'users'
    # id: Mapped[int] = mapped_column(primary_key=True)
    peer_id: Mapped[int] = mapped_column(unique=True, primary_key=True)
    screen_name: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey('rooms.id'), nullable=True)
    comfort_name: Mapped[str] = mapped_column(ForeignKey('comforts.name'), nullable=True)

    def set_comfort(self, comfort) -> bool:
        self.comfort = comfort
        return write(self)

    def set_room(self, room) -> bool:
        self.room = room
        return write(self)


class Comfort(Base):
    __tablename__ = 'comforts'
    name: Mapped[str] = mapped_column(unique=True, nullable=False, primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    first: Mapped[str] = mapped_column(nullable=False)
    second: Mapped[int] = mapped_column(nullable=True)
    third: Mapped[int] = mapped_column(nullable=True)
    users = relationship('User', backref='comfort')
    rooms = relationship('Room', backref='comfort')


class Room(Base):
    __tablename__ = 'rooms'
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(unique=False)
    comfort_name: Mapped[str] = mapped_column(ForeignKey('comforts.name'), nullable=True)
    users = relationship('User', backref='room')


