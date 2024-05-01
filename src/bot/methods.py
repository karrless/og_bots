from sqlalchemy.orm import Session

from src.database import User


def get_user(session: Session, peer_id: int) -> User | None:
    return session.query(User).where(User.peer_id == peer_id).first()
