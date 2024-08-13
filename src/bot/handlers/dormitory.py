import random
import re

import sqlalchemy
from vkbottle.bot import BotLabeler, rules, Message, MessageEvent
from vkbottle import GroupEventType

from src.bot import bot, fsm
from src.bot.handlers.menu import neighbour_menu, start_message
from src.bot.keyboards import get_numbers_keyboard, RoomsKeyboard, get_first_comfort_number_keyboard, \
    get_main_menu_keyboard
from src.bot.methods import get_user
from src.database import s_factory
from src.database.models import User, Comfort, Room
from src.dormitory.methods import get_first_comfort_number, get_second_comfort_number, get_third_comfort_number, \
    get_comfort, get_room

bl = BotLabeler()
bl.vbml_ignore_case = True
bl.auto_rules = [rules.StateGroupRule(fsm.Dormitory), rules.PeerRule(from_chat=False)]


@bl.message(text=('Указать жильё', 'Указать жилье', 'Изменить общежитие'))
async def start_get_comfort(message: Message, _re: bool = False):
    state = await bot.state_dispenser.get(message.peer_id)
    _re = state.payload.get('_re')
    await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.FIRST_NUMBER)
    text = ('Напиши первую цифру в комфортности или нажми соответсвующую кнопку:\n\n'
            'В случае МСГ или МСГ-12 нажми МСГ или МСГ-12 соответственно')
    text = text if not _re else 'Ты ошибся.\n' + text
    keyboard = get_first_comfort_number_keyboard()
    return await message.answer(text, keyboard=keyboard)


@bl.message(text='Изменить комнату')
async def change_room(message: Message):
    with s_factory() as session:
        user: User = get_user(session, message.peer_id)
        comfort: Comfort = user.comfort

    await bot.state_dispenser.set(user.peer_id, fsm.Dormitory.SELECT_ROOM, first=comfort.first,
                                  second=comfort.second, third=comfort.third, page=0, edit=True)
    return await get_room_number(message)


@bl.message(text='Удалить запись')
async def change_room(message: Message):
    with s_factory() as session:
        user: User = get_user(session, message.peer_id)
        comfort: Comfort = user.comfort
        pre_room = user.room

        user.comfort = None
        user.comfort_name = None
        user.room = None
        session.add(user)
        if pre_room:
            if len(pre_room.users) < 1:
                session.delete(pre_room)
        session.commit()

    await message.answer('Ваша запись была успешно удалена!')

    return await start_message(message)


@bl.message(state=fsm.Dormitory.FIRST_NUMBER)
async def get_second_comfort(message: Message):
    state = await bot.state_dispenser.get(message.peer_id)
    state_name = state.state.split(':')[1]
    _re = state.payload.get('_re')
    if state_name == 'first number':
        first = message.text.upper()
        with s_factory() as session:
            if first not in get_first_comfort_number(session):
                await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.FIRST_NUMBER, _re=True)
                return await start_get_comfort(message)
            if first in ['МСГ', 'МСГ-12']:
                await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.SELECT_ROOM,
                                              first=first, second=None, third=None, page=0)
                return await get_room_number(message)
    else:
        first = state.payload.get('first')
    await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.SECOND_NUMBER, first=first)
    with s_factory() as session:
        numbers = get_second_comfort_number(session, first)

    keyboard = get_numbers_keyboard(numbers)
    text = 'Напиши вторую цифру в комфортности или нажми соответствующую кнопку:'
    text = text if not _re else 'Ты ошибся.\n' + text
    return await message.answer(text, keyboard=keyboard)


@bl.message(state=fsm.Dormitory.SECOND_NUMBER)
async def get_last_comfort(message: Message):
    state = await bot.state_dispenser.get(message.peer_id)
    state_name = state.state.split(':')[1]
    _re = state.payload.get('_re')
    first = state.payload.get('first')

    if state_name == 'second number':
        second = message.text.upper()
        if second == 'НАЗАД':
            return await start_get_comfort(message)
        with s_factory() as session:
            if second not in list(map(str, get_second_comfort_number(session, first))):
                await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.SECOND_NUMBER, first=first, _re=True)
                return await get_second_comfort(message)
    else:
        second = state.payload.get('second')
    with s_factory() as session:
        numbers = get_third_comfort_number(session, first, second)
    if not numbers[0]:
        await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.SELECT_ROOM,
                                      first=first, second=second, third=None, page=0)
        return await get_room_number(message)
    await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.LAST_NUMBER, first=first, second=second)
    keyboard = get_numbers_keyboard(numbers)
    text = 'Напиши третью цифру в комфортности или нажми соответствующую кнопку:'
    text = text if not _re else 'Ты ошибся.\n' + text
    return await message.answer(text, keyboard=keyboard)


@bl.message(state=fsm.Dormitory.LAST_NUMBER)
async def get_room_number(message: Message):
    state = await bot.state_dispenser.get(message.peer_id)
    state_name = state.state.split(':')[1]
    first = state.payload.get('first')
    second = state.payload.get('second')
    _re = state.payload.get('_re')
    edit = state.payload.get('edit')

    if state_name == 'last number':
        third = message.text.upper()
        if third == 'НАЗАД':
            return await get_second_comfort(message)
        with s_factory() as session:
            if third not in list(map(str, get_third_comfort_number(session, first, second))):
                await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.LAST_NUMBER, first=first,
                                              second=second, _re=True)
                return await get_last_comfort(message)
        page = 0
    else:
        page = state.payload.get('page')
        third = state.payload.get('third')

    await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.SELECT_ROOM,
                                  first=first, second=second, third=third, page=page, edit=edit)

    with s_factory() as session:
        user: User = get_user(session, message.peer_id)
        comfort: Comfort = get_comfort(session, first, second, third)
        user.comfort = comfort
        session.add(user)
        session.commit()
        rooms = sorted([x.number for x in comfort.rooms])

    keyboard = RoomsKeyboard(rooms, state.payload)

    text = (f'Отлично, твоя комфортность {comfort.name} сохранена!\n'
            f'Теперь напиши номер своей комнаты или выбери уже из имеющихся\n\n'
            f'Если у тебя буква в номере комнаты, используй латиницу, т.е. "a" или "b".')
    text = text if not _re else 'Ты ошибся.\n' + text
    await message.answer(text, keyboard=keyboard.get_keyboard(page))


@bl.message(state=fsm.Dormitory.SELECT_ROOM)
async def set_room(message: Message):
    if message.text in ['⬅️', '➡️']:
        return await change_rooms_page(message)
    state = await bot.state_dispenser.get(message.peer_id)
    first = state.payload.get('first')
    second = state.payload.get('second')
    third = state.payload.get('third')
    edit = state.payload.get('edit')

    room_number = message.text.upper()
    regexp = r'\d{1,5}(-[A-B])?'
    if room_number == 'НАЗАД':
        if edit:
            return await neighbour_menu(message)
        if not third:
            return await start_get_comfort(message)
        elif not second:
            return await get_second_comfort(message)
        return await get_last_comfort(message)
    if not re.match(regexp, room_number):
        await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.SELECT_ROOM, first=first,
                                      second=second, third=third, _re=True)
        return await get_room_number(message)

    with s_factory() as session:
        user: User = get_user(session, message.peer_id)
        comfort = user.comfort
        pre_room = user.room

        input_room = get_room(session, comfort, room_number)
        if not input_room:
            new_room = Room(comfort=comfort, number=room_number)
            session.add(new_room)
        else:
            new_room = input_room

        user.room = new_room
        session.add(user)

        if pre_room:
            if len(pre_room.users) < 1:
                session.delete(pre_room)
        session.commit()
        neighbours = new_room.users
    for neighbour in neighbours:
        if neighbour.peer_id != user.peer_id:
            try:
                await bot.api.messages.send(neighbour.peer_id,
                                            message=f'У тебя новый сосед:\n'
                                                    f'{user.name} {user.surname} @{user.screen_name}',
                                            random_id=random.randint(1, user.peer_id),
                                            keyboard=get_main_menu_keyboard())
            except Exception:
                continue

    return await neighbour_menu(message)


async def change_rooms_page(message: Message):
    first = message.state_peer.payload.get('first')
    second = message.state_peer.payload['second']
    third = message.state_peer.payload['third']
    page = message.state_peer.payload['page']

    cmd = message.text
    with s_factory() as session:
        user: User = get_user(session, message.peer_id)
        rooms = sorted([x.number for x in user.comfort.rooms])

    keyboard = RoomsKeyboard(rooms, message.state_peer.payload)

    if cmd == '⬅️':
        page = page - 1 if page > 0 else keyboard.pages - 1
        text = f'Страница {page+1}'
    else:
        page = page + 1 if page < keyboard.pages - 1 else 0
        text = f'Страница {page+1}'

    await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.SELECT_ROOM,
                                  first=first, second=second, third=third, page=page)
    keyboard.payload['page'] = page
    bot_msg = await bot.api.messages.send(message=text, user_id=message.peer_id,
                                          keyboard=keyboard.get_keyboard(page),
                                          random_id=random.randint(1, message.peer_id))
    await bot.api.messages.delete(message_ids=[bot_msg], delete_for_all=1, peer_id=message.peer_id)

