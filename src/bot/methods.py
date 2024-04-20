from sqlalchemy.orm import Session

from ..database import with_connection
from ..database.models import User, Room


@with_connection
def get_user(session: Session, peer_id: int) -> User | None:
    return session.query(User).where(User.peer_id == peer_id).first()


@with_connection
def get_users(session: Session, room: Room) -> list[User] | None:
    return session.query(Room.users).where(Room.id == room.id).first()
