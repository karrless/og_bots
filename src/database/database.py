from sqlalchemy import create_engine

from sqlalchemy.orm import DeclarativeBase, sessionmaker
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
