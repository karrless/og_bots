from vkbottle import Keyboard, KeyboardButtonColor, Text

main_menu_keyboard_builder = Keyboard(one_time=False, inline=False)
main_menu_keyboard_builder.add(Text('FAQ'), color=KeyboardButtonColor.NEGATIVE)
main_menu_keyboard_builder.row()
main_menu_keyboard_builder.add(Text('Найти соседей'), color=KeyboardButtonColor.SECONDARY)
main_menu_keyboard = main_menu_keyboard_builder.get_json()