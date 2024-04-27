from sqlalchemy.orm import Session

from src.database import with_connection, write
from src.database.models import User, Room


# @with_connection
def get_user(session: Session, peer_id: int) -> User | None:
    return session.query(User).where(User.peer_id == peer_id).first()


# @with_connection
def get_users(session: Session, room: Room) -> list[User] | None:
    return session.query(Room.users).where(Room.id == room.id).first()


def create_user(peer_id: int, screen_name: str, name: str, surname: str) -> bool:
    user = User(peer_id=peer_id,
                screen_name=screen_name,
                name=name,
                surname=surname)
    return write(user)
