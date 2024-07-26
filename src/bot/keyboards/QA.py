import os

from vkbottle import Keyboard, KeyboardButtonColor, Text, Callback

from src.database import s_factory
from src.QA.methods import get_topics


def get_topics_keyboard(is_dorm=True, admin=False):
    with s_factory() as session:
        arr = get_topics(session)
    keyboard = Keyboard(one_time=False, inline=False)
    counter = 0
    for topic in arr:
        counter += 1
        if counter % 2 == 0:
            keyboard.row()
        keyboard.add(Text(str(topic)), color=KeyboardButtonColor.PRIMARY)

    if is_dorm:
        keyboard.row()
        keyboard.add(Text('Обратно в меню'))
    elif admin:
        keyboard.row()
        keyboard.add(Text('Включить-поиск_соседей:)'), color=KeyboardButtonColor.POSITIVE)
        keyboard.row()
        if bool(os.getenv('MODER_CHAT')):
            keyboard.add(Text('Выключить-перессылку_в-чат:)'), color=KeyboardButtonColor.NEGATIVE)
        else:
            keyboard.add(Text('Включить-перессылку_в-чат:)'), color=KeyboardButtonColor.POSITIVE)
    return keyboard.get_json()


def get_subtopics_keyboard(subtopics: list):
    keyboard = Keyboard(one_time=False, inline=False)
    counter = 0
    for subtopic in subtopics:
        counter += 1
        if counter % 2 == 1:
            keyboard.row()
        keyboard.add(Text(str(subtopic)), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text('Свой вопрос'), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Text('Назад'), color=KeyboardButtonColor.SECONDARY)
    keyboard.add(Text('Обратно в меню'), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()


def get_answer_keyboard():
    keyboard = Keyboard(one_time=False, inline=False)
    keyboard.add(Text('Свой вопрос'), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Text('Назад'), color=KeyboardButtonColor.SECONDARY)
    keyboard.add(Text('Обратно в меню'), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()
