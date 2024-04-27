from math import ceil

from vkbottle import Keyboard, KeyboardButtonColor, Text, Callback

from src.database import s_factory
from src.database.models import Room
from src.dormitory.methods import get_first_comfort_number

dorm_menu_keyboard_builder = Keyboard(one_time=False, inline=False)

dorm_menu_keyboard = dorm_menu_keyboard_builder.get_json()

start_dorm_keyboard_builder = Keyboard(one_time=False, inline=False)
start_dorm_keyboard_builder.add(Text('Указать жильё'), color=KeyboardButtonColor.POSITIVE)
start_dorm_keyboard_builder.row()
start_dorm_keyboard_builder.add(Text('Обратно в меню'))
start_dorm_keyboard = start_dorm_keyboard_builder.get_json()


def get_numbers_keyboard(arr: list, back:bool = True) -> str:
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
    def __init__(self, rooms: list[str], columns=2, rows=2):
        self.columns = columns
        self.rows = rows
        self.buttons = self.columns*self.rows
        self.pages = ceil(len(rooms)/self.buttons)
        self.rooms = rooms

    def get_keyboard(self, page):
        keyboard = Keyboard(one_time=True, inline=False)
        if self.rooms:
            for row in range(self.rows):
                i = -1
                for col in range(self.columns):
                    keyboard.row()
                    i = page * self.buttons + row * self.columns + col
                    if i >= len(self.rooms):
                        i = -1
                        break
                    keyboard.add(Text(self.rooms[i]), color=KeyboardButtonColor.PRIMARY)
                if i < 0:
                    break
            if self.pages > 1:
                keyboard.add(Callback('⬅️', {'rooms_page': 'back'}))
                keyboard.add(Callback(f'{page + 1}/{self.pages}', {'cmd': 'joke'}))
                keyboard.add(Callback('➡️', {'rooms_page': 'next'}))
                keyboard.row()

        keyboard.add(Text('Назад'))
        keyboard.add(Text('Обратно в меню'))
        return keyboard.get_json()
