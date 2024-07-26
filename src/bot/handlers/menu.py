import os
from dotenv import set_key, find_dotenv

from vkbottle.bot import BotLabeler, rules, Message, MessageEvent
from vkbottle import GroupEventType

from src.bot import bot, fsm
from src.bot.keyboards import get_main_menu_keyboard, get_dorm_menu_keyboard, get_topics_keyboard
from src.bot.methods import get_user
from src.database import s_factory
from src.database.models import User


bl = BotLabeler()
bl.auto_rules = [rules.PeerRule(from_chat=False)]


@bl.message(text=('Начать', 'Start', 'Обратно в меню', 'начать'))
async def start_message(message: Message):
    if os.getenv('IS_DORM'):
        await bot.state_dispenser.set(message.peer_id, fsm.Menu.MAIN)
    else:
        await bot.state_dispenser.set(message.peer_id, fsm.QA.MENU)
    with s_factory() as session:
        if not get_user(session, message.peer_id):
            user = (await bot.api.users.get(message.peer_id, fields=['screen_name']))[0]
            session.add(
                User(peer_id=message.peer_id,
                     screen_name=user.screen_name,
                     name=user.first_name,
                     surname=user.last_name)
            )
            session.commit()
    admin = str(message.peer_id) in [os.getenv('POLLY_ID'), os.getenv('KARRLESS_ID')]
    return await message.answer(f'Привет, чмоня!', keyboard=get_main_menu_keyboard(admin))


@bl.message(text='Найти соседей')
async def neighbour_menu(message: Message):
    if not os.getenv('IS_DORM'):
        await bot.state_dispenser.set(message.peer_id, fsm.QA.MENU)
        return await message.answer(f'Сюда пока нельзя!', keyboard=get_main_menu_keyboard())
    text = ''
    with s_factory() as session:
        user: User = get_user(session, message.peer_id)
        if user.room_id:
            await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.MENU)
            keyboard = get_dorm_menu_keyboard()
            neighbours: list[User] = user.room.users
            text += f'{user.room.comfort_name}: {user.comfort.title}, комната {user.room.number}\n\n'
            if len(neighbours) > 1:
                text += 'Твои соседи:\n\n'
                for neighbour in neighbours:
                    if neighbour.peer_id != user.peer_id:
                        text += f'{neighbour.name} {neighbour.surname} @{neighbour.screen_name}\n'
                text += '\n'
            else:
                text += 'Пока соседей нет.\n\n'
            text += 'Возможно не все ещё зарегистрировались. Если появятся новые соседи - тебе придет сообщение'
        else:
            await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.NEW)
            keyboard = get_dorm_menu_keyboard(False)
            text = ('Я пока не знаю, какое у тебя общежитие.\n\n'
                    'Напиши "Указать жильё" или нажми соответсвующую кнопку.')
    return await message.answer(text, keyboard=keyboard)


@bl.message(text=('Вопросы и ответы', 'Вопросы и ответы'))
async def faq_keys(message: Message):
    await bot.state_dispenser.set(message.peer_id, fsm.QA.MENU)
    keyboard = get_topics_keyboard()
    text = 'Выбери тему, которая тебе интересна:\n\nЕсли клавиатуры нет, отправь "Начать" или "Вопросы и ответы"'
    return await message.answer(message=text,
                                keyboard=keyboard)


@bl.message(text=('Включить-поиск_соседей:)', 'Выключить-поиск_соседей:)'))
async def dorm_on(message: Message):
    if os.environ['IS_DORM']:
        os.environ['IS_DORM'] = ''
        set_key(os.path.abspath('.env'), 'IS_DORM', '')
    else:
        os.environ['IS_DORM'] = '1'
        set_key(os.path.abspath('.env'), 'IS_DORM', '1')
    return await message.answer(message=f'Общаги {"включена" if os.environ["IS_DORM"] else "выключена"}',
                                keyboard=get_main_menu_keyboard(True))


@bl.message(text=('Включить-перессылку_в-чат:)', 'Выключить-перессылку_в-чат:)'))
async def dorm_on(message: Message):
    if os.environ['MODER_CHAT']:
        os.environ['MODER_CHAT'] = ''
        set_key(os.path.abspath('.env'), 'MODER_CHAT', '')
    else:
        os.environ['MODER_CHAT'] = '1'
        set_key(os.path.abspath('.env'), 'MODER_CHAT', '1')
    return await message.answer(message=f'Перессылка в чат {"включена" if os.environ["MODER_CHAT"] else "выключена"}',
                                keyboard=get_main_menu_keyboard(True))


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
