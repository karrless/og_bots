from sqlalchemy.orm import Session

from ..database import with_connection, write
from ..database.models import Room, Comfort, User


@with_connection
def get_comfort(session: Session, first: str, second: int = None, third: int = None) -> Comfort | None:
    comfort = session.query(Comfort).where(Comfort.first == first,
                                           Comfort.second == second, Comfort.third == third).first()
    return comfort


@with_connection
def get_first_comfort_number(session: Session) -> list:
    return session.query(Comfort.first).all()


@with_connection
def get_second_comfort_number(session: Session, first: str) -> list:
    return session.query(Comfort.second).where(Comfort.first == first).all()


@with_connection
def get_third_comfort_number(session: Session, first: str, second: int) -> list:
    return session.query(Comfort.third).where(Comfort.first == first, Comfort.second == second).all()


@with_connection
def get_room(session: Session, comfort: Comfort, number: str) -> Room | None:
    return session.query(Room).where(Room.comfort_name == comfort,
                                     Room.number == number).first()


@with_connection
def get_rooms(session: Session, comfort: Comfort) -> list[Room] | None:
    return session.query(Comfort.rooms).where(Comfort.name == comfort.name).first()


@with_connection
def get_neighbours(session: Session, room: Room) -> list[User] | None:
    return session.query(Room.users).where(Room.id == room.id).first()


def create_room(comfort: Comfort, number: str) -> Room | None:
    room = Room(number=number, comfort=comfort)
    if write(room):
        return room
    else:
        return None
