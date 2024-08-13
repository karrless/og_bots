from sqlalchemy.orm import Session

from src.database import Room, Comfort


def get_comfort(session: Session, first: str, second: int = None, third: int = None) -> Comfort | None:
    return session.query(Comfort).where(Comfort.first == first,
                                        Comfort.second == second, Comfort.third == third).first()


def get_room(session: Session, comfort: Comfort, number: str) -> Room | None:
    return session.query(Room).where(Room.comfort_name == comfort.name,
                                     Room.number == number).first()


def get_first_comfort_number(session: Session) -> list[str]:
    sets = sorted(set(session.query(Comfort.first).all()))
    numbers = [x[0] for x in sets]
    msg = numbers[-2:]
    result = sorted(list(map(int, numbers[:-2]))) + msg
    return list(map(str, result))


def get_second_comfort_number(session: Session, first: str) -> list[int]:
    query = sorted(set(session.query(Comfort.second).where(Comfort.first == first).all()))
    return [x[0] for x in query]


def get_third_comfort_number(session: Session, first: str, second: int) -> list[int]:
    query = session.query(Comfort.third).where(Comfort.first == first, Comfort.second == second).all()
    return sorted([x[0] for x in query])
