from sqlalchemy.orm import Session

from src.database import Answer


def get_topics(session: Session):
    query = session.query(Answer.topic).order_by(Answer.id).all()
    arr = []
    for i in query:
        if i[0] not in arr:
            arr.append(i[0])
    return arr


def get_subtopics(session: Session, topic: str):
    query = session.query(Answer.subtopic).where(Answer.topic == topic).all()
    return [x[0] for x in query]


def get_answer(session: Session, topic: str, subtopic: str = None):
    if subtopic:
        return session.query(Answer).where(Answer.topic == topic, Answer.subtopic == subtopic).first()
    else:
        return session.query(Answer).where(Answer.topic == topic).first()
