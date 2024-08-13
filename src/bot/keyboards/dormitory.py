import random
from math import ceil

from vkbottle import Keyboard, KeyboardButtonColor, Text, Callback

from src.database import s_factory
from src.dormitory.methods import get_first_comfort_number


def get_dorm_menu_keyboard(is_dorm_exist: bool = True) -> str:
    keyboard = Keyboard(one_time=False, inline=False)
    if is_dorm_exist:
        keyboard.add(Text('Изменить общежитие'), color=KeyboardButtonColor.PRIMARY)
        keyboard.add(Text('Изменить комнату'), color=KeyboardButtonColor.PRIMARY)
        keyboard.row()
        keyboard.add(Text('Удалить запись'), color=KeyboardButtonColor.NEGATIVE)
    else:
        keyboard.add(Text('Указать жильё'), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Text('Обратно в меню'))
    return keyboard.get_json()


def get_numbers_keyboard(arr: list, back: bool = True) -> str:
    keyboard = Keyboard(one_time=False, inline=False)
    counter = 0
    for number in arr:
        counter += 1
        if counter % 5 == 1:
            keyboard.row()
        keyboard.add(Text(str(number)), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    if back:
        keyboard.add(Text('Назад'))
    keyboard.add(Text('Обратно в меню'))
    return keyboard.get_json()


def get_first_comfort_number_keyboard():
    with s_factory() as session:
        return get_numbers_keyboard(get_first_comfort_number(session), False)


class RoomsKeyboard:
    def __init__(self, rooms: list[str], payload: dict, columns=3, rows=4):
        self.columns = columns
        self.rows = rows
        self.buttons = self.columns * self.rows
        self.pages = ceil(len(rooms) / self.buttons)
        self.rooms = rooms
        self.payload = payload

    def get_keyboard(self, page):
        keyboard = Keyboard(one_time=True, inline=False)
        if self.rooms:
            for row in range(self.rows):
                i = -1
                for col in range(self.columns):
                    i = page * self.buttons + row * self.columns + col
                    if i >= len(self.rooms):
                        i = -1
                        break
                    keyboard.add(Text(self.rooms[i]), color=KeyboardButtonColor.PRIMARY)
                if i < 0:
                    if len(self.rooms) % self.columns != 0:
                        keyboard.row()
                    break
                keyboard.row()

            if self.pages > 1:
                keyboard.add(Text('⬅️', payload=self.payload))
                keyboard.add(Callback(f'{page + 1}/{self.pages}', {'cmd': 'joke'}))
                keyboard.add(Text('➡️', payload=self.payload))
                keyboard.row()

        keyboard.add(Text('Назад'))
        keyboard.add(Text('Обратно в меню'))
        return keyboard.get_json()
