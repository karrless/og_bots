from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from . import Base, write


class Comfort(Base):
    __tablename__ = 'comforts'
    name: Mapped[str] = mapped_column(unique=True, nullable=False, primary_key=True)
    first: Mapped[str] = mapped_column(nullable=False)
    second: Mapped[int] = mapped_column(nullable=True)
    third: Mapped[int] = mapped_column(nullable=True)


class Room(Base):
    __tablename__ = 'rooms'
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(unique=False)
    comfort_name: Mapped[str] = mapped_column(ForeignKey('comforts.name'), nullable=True)
    comfort = relationship('Comfort', backref='rooms')


class User(Base):
    __tablename__ = 'users'
    # id: Mapped[int] = mapped_column(primary_key=True)
    peer_id: Mapped[int] = mapped_column(unique=True, primary_key=True)
    screen_name: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    faculty: Mapped[str] = mapped_column(nullable=True)
    group: Mapped[str] = mapped_column(nullable=True)
    room = relationship('Room', backref='users')
    room_id: Mapped[int] = mapped_column(ForeignKey('rooms.id'), nullable=True)
    comfort = relationship('Comfort', cascade="all,delete")
    comfort_name: Mapped[str] = mapped_column(ForeignKey('comforts.name'), nullable=True)

    def set_comfort(self, comfort: Comfort) -> bool:
        self.comfort = comfort
        return write(self)

    def set_room(self, room: Room) -> bool:
        self.room = room
        return write(self)

    def set_faculty(self, faculty: str) -> bool:
        self.faculty = faculty
        return write(self)

    def set_group(self, group: str) -> bool:
        self.group = group
        return write(self)
