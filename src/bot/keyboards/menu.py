import os

from vkbottle import Keyboard, KeyboardButtonColor, Text

from src.bot.keyboards.QA import get_topics_keyboard


def get_main_menu_keyboard(admin: bool = False):
    is_dorm = bool(os.getenv('IS_DORM'))
    keyboard = Keyboard(one_time=False, inline=False)
    if is_dorm:
        keyboard.add(Text('Вопросы и ответы'), color=KeyboardButtonColor.PRIMARY)
        keyboard.row()
        keyboard.add(Text('Найти соседей'), color=KeyboardButtonColor.POSITIVE)
        if admin:
            keyboard.row()
            keyboard.add(Text('Выключить-поиск_соседей:)'), color=KeyboardButtonColor.NEGATIVE)
            keyboard.row()
            if bool(os.getenv('MODER_CHAT')):
                keyboard.add(Text('Выключить-перессылку_в-чат:)'), color=KeyboardButtonColor.NEGATIVE)
            else:
                keyboard.add(Text('Включить-перессылку_в-чат:)'), color=KeyboardButtonColor.POSITIVE)
        return keyboard.get_json()
    else:
        return get_topics_keyboard(is_dorm, admin)
