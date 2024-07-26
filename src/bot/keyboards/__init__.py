from vkbottle import Keyboard, Text, KeyboardButtonColor

from .menu import get_main_menu_keyboard
from .dormitory import (get_dorm_menu_keyboard,
                        get_first_comfort_number_keyboard,
                        get_numbers_keyboard, RoomsKeyboard)
from .QA import get_topics_keyboard

__all__ = [get_main_menu_keyboard,
           get_dorm_menu_keyboard,
           get_first_comfort_number_keyboard,
           get_numbers_keyboard, RoomsKeyboard,
           get_topics_keyboard]


def get_back_keyboard():
    keyboard = Keyboard(one_time=False, inline=False)
    keyboard.add(Text('Назад'), color=KeyboardButtonColor.SECONDARY)
    keyboard.row()
    keyboard.add(Text('Обратно в меню'), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()
