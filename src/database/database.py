from loguru import logger

from typing import Union

from sqlalchemy import create_engine

from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session, MappedAsDataclass
import os

engine = create_engine(os.getenv('DB_URI'))

s_factory = sessionmaker(engine)


class Base(DeclarativeBase):
    pass


def connect():
    """
    Подключение к базе данных
    :return:
    """
    engine.connect()


def create():
    """
    Создание таблиц
    :return:
    """
    Base.metadata.create_all(engine)


def drop_all(tables: list = None):
    """
    Удаление таблицы
    :param tables: список таблиц
    :return:
    """
    if tables:
        Base.metadata.drop_all(engine, tables=tables)
    else:
        Base.metadata.drop_all(engine)


def with_connection(func):
    def wrapper(*args, **kwargs):
        with s_factory() as session:
            try:
                return func(session, *args, **kwargs)
            except Exception as e:
                logger.exception(e)
                # print(e)
                return 0
    return wrapper


@with_connection
def write(session: Session, objects: Union[list, Base]) -> bool:
    """
    Функция записи в базу данных
    """
    try:
        if not isinstance(objects, list):
            objects = [objects]
        for object_ in objects:
            session.add(object_)
        session.commit()
    except Exception as e:
        logger.exception(e)
        # print(e)
        return False
    return True
