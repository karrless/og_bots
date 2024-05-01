import os

from vkbottle import Keyboard, KeyboardButtonColor, Text

IS_DORM = int(os.getenv('DEBUG'))


def get_main_menu_keyboard():
    keyboard = Keyboard(one_time=False, inline=False)
    keyboard.add(Text('FAQ'))
    if IS_DORM:
        keyboard.row()
        keyboard.add(Text('Найти соседей'), color=KeyboardButtonColor.POSITIVE)
    return keyboard.get_json()
