import os

from vkbottle import Keyboard, KeyboardButtonColor, Text

IS_DORM = int(os.getenv('DEBUG'))

main_menu_keyboard_builder = Keyboard(one_time=False, inline=False)
main_menu_keyboard_builder.add(Text('FAQ'), color=KeyboardButtonColor.NEGATIVE)
if IS_DORM:
    main_menu_keyboard_builder.row()
    main_menu_keyboard_builder.add(Text('Найти соседей'), color=KeyboardButtonColor.SECONDARY)
main_menu_keyboard = main_menu_keyboard_builder.get_json()