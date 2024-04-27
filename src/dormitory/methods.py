from sqlalchemy.orm import Session

from ..database import with_connection, write
from ..database.models import Room, Comfort, User


# @with_connection
def get_comfort(session: Session, first: str, second: int = None, third: int = None) -> Comfort | None:
    return session.query(Comfort).where(Comfort.first == first,
                                        Comfort.second == second, Comfort.third == third).first()


# @with_connection
def get_first_comfort_number(session: Session) -> list[str]:
    sets = sorted(set(session.query(Comfort.first).all()))
    numbers = [x[0] for x in sets]
    msg = numbers[-1:]
    result = sorted(list(map(int, numbers[:-1]))) + msg
    return list(map(str, result))


# @with_connection
def get_second_comfort_number(session: Session, first: str) -> list[int]:
    query = sorted(set(session.query(Comfort.second).where(Comfort.first == first).all()))
    return [x[0] for x in query]


# @with_connection
def get_third_comfort_number(session: Session, first: str, second: int) -> list[int]:
    query = session.query(Comfort.third).where(Comfort.first == first, Comfort.second == second).all()
    return sorted([x[0] for x in query])


# @with_connection
def get_room(session: Session, comfort: Comfort, number: str) -> Room | None:
    return session.query(Room).where(Room.comfort == comfort,
                                     Room.number == number).first()


# @with_connection
def get_rooms(session: Session, comfort: Comfort) -> list[Room] | list[None]:
    query = session.query(Comfort.rooms).where(Comfort.name == comfort.name).first()
    return sorted([x[0] for x in query])


# @with_connection
def get_neighbours(session: Session, room: Room) -> list[User] | None:
    return session.query(Room.users).where(Room.id == room.id).first()


def create_room(comfort: Comfort, number: str) -> Room | None:
    room = Room(number=number, comfort=comfort)
    if write(room):
        return room
    else:
        return None

