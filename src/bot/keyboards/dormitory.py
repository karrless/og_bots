from vkbottle import Keyboard, KeyboardButtonColor, Text

from src.dormitory.methods import get_first_comfort_number

dorm_menu_keyboard_builder = Keyboard(one_time=False, inline=False)

dorm_menu_keyboard = dorm_menu_keyboard_builder.get_json()

start_dorm_keyboard_builder = Keyboard(one_time=False, inline=False)
start_dorm_keyboard_builder.add(Text('Указать жильё'), color=KeyboardButtonColor.POSITIVE)
start_dorm_keyboard_builder.row()
start_dorm_keyboard_builder.add(Text('Обратно в меню'))
start_dorm_keyboard = start_dorm_keyboard_builder.get_json()


def get_numbers_keyboard(arr: list, back: str = 'Назад') -> str:
    keyboard = Keyboard(one_time=False, inline=False)
    counter = 0
    for number in arr:
        counter += 1
        if counter % 5 == 1:
            keyboard.row()
        keyboard.add(Text(str(number)), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text(back))
    return keyboard.get_json()


first_comfort_number_keyboard = get_numbers_keyboard(get_first_comfort_number(), 'Обратно в меню')

