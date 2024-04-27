
from vkbottle.bot import BotLabeler, rules, Message, MessageEvent
from vkbottle import GroupEventType

from src.bot import bot, fsm
from src.bot.keyboards import main_menu_keyboard, dorm_menu_keyboard, start_dorm_keyboard
from src.bot.methods import get_user, create_user
from src.database import s_factory
from src.database.models import User
from src.dormitory.methods import get_neighbours

bl = BotLabeler()
bl.auto_rules = [rules.PeerRule(from_chat=False)]


@bl.message(text=('Начать', 'Start', 'Обратно в меню'))
async def start_message(message: Message):
    await bot.state_dispenser.set(message.peer_id, fsm.Menu.MAIN)
    with s_factory() as session:
        if not get_user(session, message.peer_id):
            user = (await bot.api.users.get(message.peer_id, fields=['screen_name']))[0]
            create_user(message.peer_id, user.screen_name, user.first_name, user.last_name)
    return await message.answer(f'Привет, чмоня!', keyboard=main_menu_keyboard)


@bl.message(text='Найти соседей')
async def neighbour_menu(message: Message):
    text = ''
    with s_factory() as session:
        user: User = get_user(session, message.peer_id)
        if user.room_id:
            await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.MENU)
            keyboard = dorm_menu_keyboard
            neighbours: list[User] = user.room.users
            if len(neighbours) > 1:
                text += f'{user.room.comfort_name}: {user.comfort.title}, комната {user.room.number}\n\n'
                text += 'Твои соседи:\n\n'
                for neighbour in neighbours:
                    if neighbour.peer_id != user.peer_id:
                        text += f'{neighbour.name} {neighbour.surname} @{neighbour.screen_name}\n'
                text += '\n'
            else:
                text = 'Пока соседей нет.\n\n'
            text += 'Возможно не все ещё зарегистрировались. Если появятся новые соседи - тебе придет сообщение'
        else:
            await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.NEW)
            keyboard = start_dorm_keyboard
            text = ('Я пока не знаю, какое у тебя общежитие.\n\n'
                    'Напиши "Указать жильё" или нажми соответсвующую кнопку.')
    return await message.answer(text, keyboard=keyboard)


@bl.raw_event(GroupEventType.MESSAGE_EVENT,
              MessageEvent,
              rules.PayloadRule({'cmd': 'joke'}))
async def joke_button(event: MessageEvent):
    await event.show_snackbar('Ты зачем это нажал? Не нажимай больше!')

# @bl.message(text='test')
# async def test(message: Message):
#     from vkbottle import Keyboard
#     main_menu_keyboard_builder = Keyboard(one_time=False, inline=False)
#     from vkbottle import Text
#     from vkbottle import KeyboardButtonColor
#     main_menu_keyboard_builder.add(Text('1'), color=KeyboardButtonColor.NEGATIVE)
#     main_menu_keyboard_builder.add(Text('2'))
#     print('сейчас строки')
#     main_menu_keyboard_builder.row()
#     # main_menu_keyboard_builder.row()
#     # main_menu_keyboard_builder.row()
#     main_menu_keyboard_builder.add(Text('3'))
#     k = main_menu_keyboard_builder.get_json()
#     await message.answer('123', keyboard=k)
