import random
import re

from vkbottle.bot import BotLabeler, rules, Message, MessageEvent
from vkbottle import GroupEventType

from src.bot import bot, fsm
from src.bot.handlers.menu import neighbour_menu
from src.bot.keyboards import get_numbers_keyboard, RoomsKeyboard, get_first_comfort_number_keyboard, \
    get_main_menu_keyboard
from src.bot.methods import get_user
from src.database import s_factory
from src.database.models import User, Comfort, Room
from src.dormitory.methods import get_first_comfort_number, get_second_comfort_number, get_third_comfort_number, \
    get_comfort, get_room

bl = BotLabeler()
bl.auto_rules = [rules.StateGroupRule(fsm.Dormitory), rules.PeerRule(from_chat=False)]


@bl.message(text=('Указать жильё', 'Указать жилье'))
async def start_get_comfort(message: Message, _re: bool = False):
    await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.FIRST_NUMBER)
    text = 'Напиши первую цифру в комфортности или нажми соответсвующую кнопку:\n\nВ случае МСГ нажми МСГ'
    text = text if not _re else 'Вы ошиблись.\n' + text
    keyboard = get_first_comfort_number_keyboard()
    return await message.answer(text, keyboard=keyboard)


@bl.message(state=fsm.Dormitory.FIRST_NUMBER)
async def get_second_comfort(message: Message, _re: bool = False):
    state = await bot.state_dispenser.get(message.peer_id)
    state = state.state.split(':')[1]

    if state == 'first number':
        first = message.text.upper()
        with s_factory() as session:
            if first not in get_first_comfort_number(session):
                return await start_get_comfort(message, True)
            if first == 'МСГ':
                await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.SELECT_ROOM,
                                              first=first, second=None, third=None, page=0)
                return await get_room_number(message)
        await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.SECOND_NUMBER, first=first)
    else:
        first = message.state_peer.payload['first']

    with s_factory() as session:
        numbers = get_second_comfort_number(session, first)

    keyboard = get_numbers_keyboard(numbers)
    text = 'Напиши вторую цифру в комфортности или нажми соответствующую кнопку:'
    text = text if not _re else 'Вы ошиблись.\n' + text
    return await message.answer(text, keyboard=keyboard)


@bl.message(state=fsm.Dormitory.SECOND_NUMBER)
async def get_last_comfort(message: Message, _re: bool = False):
    state = await bot.state_dispenser.get(message.peer_id)
    state = state.state.split(':')[1]
    first = message.state_peer.payload['first']

    if state == 'second number':
        second = message.text.upper()
        if second == 'НАЗАД':
            return await start_get_comfort(message)
        with s_factory() as session:
            if second not in list(map(str, get_second_comfort_number(session, first))):
                return await get_second_comfort(message, True)
        await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.LAST_NUMBER, first=first, second=second)
    else:
        second = message.state_peer.payload['second']

    with s_factory() as session:
        numbers = get_third_comfort_number(session, first, second)
    if not numbers[0]:
        await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.SELECT_ROOM,
                                      first=first, second=second, third=None, page=0)
        return await get_room_number(message)

    keyboard = get_numbers_keyboard(numbers)
    text = 'Напиши третью цифру в комфортности или нажми соответствующую кнопку:'
    text = text if not _re else 'Вы ошиблись.\n' + text
    return await message.answer(text, keyboard=keyboard)


@bl.message(state=fsm.Dormitory.LAST_NUMBER)
async def get_room_number(message: Message, _re: bool = False):
    # TODO: продумать как потом изменять все это говно
    state = await bot.state_dispenser.get(message.peer_id)
    state = state.state.split(':')[1]
    first = message.state_peer.payload['first']
    second = message.state_peer.payload['second']

    if state == 'last number':
        third = message.text.upper()
        if third == 'НАЗАД':
            return await get_second_comfort(message)
        with s_factory() as session:
            if third not in list(map(str, get_third_comfort_number(session, first, second))):
                return await get_last_comfort(message, True)
        page = 0
    else:
        page = message.state_peer.payload['page']
        third = message.state_peer.payload['third']

    await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.SELECT_ROOM,
                                  first=first, second=second, third=third, page=page)
    with s_factory() as session:
        user: User = get_user(session, message.peer_id)
        comfort: Comfort = get_comfort(session, first, second, third)
        user.comfort = comfort
        session.add(user)
        session.commit()
        rooms = [x.number for x in comfort.rooms]

    keyboard = RoomsKeyboard(rooms)

    text = (f'Отлично, твоя комфортность сохранена!\n'
            f'Теперь напиши номер своей комнаты\n\n'
            f'Если у тебя буква в номере комнаты, используй латиницу, т.е. "a" или "b".')
    text = text if not _re else 'Вы ошиблись.\n' + text
    await message.answer(text, keyboard=keyboard.get_keyboard(page))


@bl.message(state=fsm.Dormitory.SELECT_ROOM)
async def set_room(message: Message):
    second = message.state_peer.payload['second']
    third = message.state_peer.payload['third']

    room_number = message.text.upper()
    regexp = r'\d{1,5}(-[A-B])?'
    if room_number == 'НАЗАД':
        if not third:
            return await start_get_comfort(message)
        elif not second:
            return await get_second_comfort(message)
        return await get_last_comfort(message)
    if not re.match(regexp, room_number):
        return await get_last_comfort(message, True)

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
            if len(pre_room.users) <= 1:
                session.delete(pre_room)
        session.commit()
        neighbours = new_room.users

    for neighbour in neighbours:
        if neighbour.peer_id != user.peer_id:
            await bot.api.messages.send(neighbour.peer_id,
                                        message=f'У тебя новый сосед:\n'
                                                f'{user.name} {user.surname} @{user.screen_name}',
                                        random_id=random.randint(1, user.peer_id),
                                        keyboard=get_main_menu_keyboard())

    return await neighbour_menu(message)


@bl.raw_event(GroupEventType.MESSAGE_EVENT,
              MessageEvent,
              rules.PayloadRule({'rooms_page': 'back'}))
@bl.raw_event(GroupEventType.MESSAGE_EVENT,
              MessageEvent,
              rules.PayloadRule({'rooms_page': 'next'}))
async def change_rooms_page(event: MessageEvent):
    state = await bot.state_dispenser.get(event.peer_id)

    first = state.payload['first']
    second = state.payload['second']
    third = state.payload['third']
    page = state.payload['page']

    cmd = event.payload['rooms_page']
    with s_factory() as session:
        user: User = get_user(session, event.peer_id)
        rooms = [x.number for x in user.comfort.rooms]

    keyboard = RoomsKeyboard(rooms)

    if cmd == 'back':
        page = page - 1 if page > 0 else keyboard.pages - 1
    else:
        page = page + 1 if page < keyboard.pages - 1 else 0

    await bot.state_dispenser.set(event.peer_id, fsm.Dormitory.SELECT_ROOM,
                                  first=first, second=second, third=third, page=page)
    # await bot.api.messages.send(user_id=event.peer_id, keyboard=keyboard.get_keyboard(page), random_id=42)
    await event.edit_message(keyboard=keyboard.get_keyboard(page))
