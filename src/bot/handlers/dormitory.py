import random
import re

from vkbottle.bot import BotLabeler, rules, Message, MessageEvent
from vkbottle import GroupEventType

from src.bot import fsm, bot
from src.bot.handlers.menu import neighbour_menu
from src.bot.keyboards import get_first_comfort_number_keyboard, get_numbers_keyboard, RoomsKeyboard, \
    get_main_menu_keyboard, get_dorm_menu_keyboard
from src.bot.methods import get_user
from src.database import s_factory, User, Room
from src.dormitory.methods import get_first_comfort_number, get_second_comfort_number, get_third_comfort_number, \
    get_comfort, get_room

bl = BotLabeler()
bl.auto_rules = [rules.StateGroupRule(fsm.Dormitory), rules.PeerRule(from_chat=False)]


@bl.message(text='Изменить комнату')
async def change_room(message: Message):
    with s_factory() as session:
        user = get_user(session, message.peer_id)
        if not user.room:
            return await message.answer('Ты зачем балуешься!\n', keyboard=get_dorm_menu_keyboard(False))
        comfort = user.comfort

    return await get_room_number(message, comfort=comfort)



@bl.message(text=('Указать жильё', 'Указать жилье', 'Изменить общежитие'))
async def get_first_number(message: Message, _re: bool = False):
    await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.FIRST_NUMBER)
    text = 'Напиши первую цифру в комфортности или нажми соответствующую кнопку:\n'
    text = text if not _re else 'Вы ошиблись.\n' + text
    keyboard = get_first_comfort_number_keyboard()
    return await message.answer(text, keyboard=keyboard)


@bl.message(state=fsm.Dormitory.FIRST_NUMBER)
async def get_second_number(message: Message, _re: bool = False):
    state = await bot.state_dispenser.get(message.peer_id)
    state_name = state.state.split(':')[1]

    if state_name == 'first number':
        first = message.text.upper()
        with s_factory() as session:
            if first not in get_first_comfort_number(session):
                return await get_first_number(message, True)
            if first == 'МСГ':
                await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.SELECT_ROOM,
                                              first=first, second=None, third=None, page=0, from_='МСГ')
                return await get_room_number(message)

        await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.SECOND_NUMBER, first=first)
    else:
        first = state.payload['first']

    with s_factory() as session:
        numbers = get_second_comfort_number(session, first)

    keyboard = get_numbers_keyboard(numbers)
    text = 'Напиши вторую цифру в комфортности или нажми соответствующую кнопку:'
    text = text if not _re else 'Вы ошиблись.\n' + text
    return await message.answer(text, keyboard=keyboard)


@bl.message(state=fsm.Dormitory.SECOND_NUMBER)
async def get_third_number(message: Message, _re: bool = False, back: bool = False):
    if message.text.upper() == 'НАЗАД' and not back:
        return await get_first_number(message)
    state = await bot.state_dispenser.get(message.peer_id)
    first = state.payload['first']
    state_name = state.state.split(':')[1]
    if state_name == 'second number':
        second = message.text.upper()
        with s_factory() as session:
            if second not in list(map(str, get_second_comfort_number(session, first))):
                return await get_second_number(message, True)
        await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.LAST_NUMBER,
                                      first=first, second=second)
    else:
        second = state.payload['second']

    with s_factory() as session:
        numbers = get_third_comfort_number(session, first, second)

    if not numbers[0]:
        await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.SELECT_ROOM,
                                      first=first, second=int(second), third=None, page=0, from_='second')
        return await get_room_number(message)

    keyboard = get_numbers_keyboard(numbers)
    text = 'Напиши третью цифру в комфортности или нажми соответствующую кнопку:'
    text = text if not _re else 'Вы ошиблись.\n' + text
    return await message.answer(text, keyboard=keyboard)


@bl.message(state=fsm.Dormitory.LAST_NUMBER)
async def get_room_number(message: Message, _re: bool = False, back: bool = False, comfort=None):
    if not comfort:
        state = await bot.state_dispenser.get(message.peer_id)
        first = state.payload['first']
        second = state.payload.get('second')
        state_name = state.state.split(':')[1]
        if message.text.upper() == 'НАЗАД' and not back:
            await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.SECOND_NUMBER, first=first)
            return await get_second_number(message)

        if state_name == 'last number':
            third = message.text.upper()

            with s_factory() as session:
                if third not in list(map(str, get_third_comfort_number(session, first, second))):
                    return await get_third_number(message, True)
            page = 0
        else:
            page = state.payload['page']
            third = state.payload['third']
        from_ = 'third' if not state.payload.get('from_') else state.payload.get('from_')
    else:
        first = comfort.first
        second = comfort.second
        third = comfort.third
        page = 0
        from_ = 'menu'

    await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.SELECT_ROOM,
                                  first=first, second=second, third=third, page=page, from_=from_)

    with s_factory() as session:
        user: User = get_user(session, message.peer_id)
        comfort = comfort if comfort else get_comfort(session, first, second, third)
        user.comfort = comfort
        session.add(user)
        session.commit()
        rooms = []
        for x in comfort.rooms:
            if x.id != user.room_id:
                rooms.append(x)

    keyboard = RoomsKeyboard(rooms)
    text = (f'Теперь напиши свой номер комнаты {"или выбери из предложенных" if rooms else ""}\n\n'
            f'Если у тебя буква в номере комнаты, используй латиницу, т.е. "a" или "b".')
    text = text if not _re else 'Вы ошиблись.\n' + text
    await message.answer(text, keyboard=keyboard.get_keyboard(page))


@bl.message(state=fsm.Dormitory.SELECT_ROOM)
async def set_room(message: Message):
    state = await bot.state_dispenser.get(message.peer_id)
    first = state.payload['first']
    second = state.payload['second']
    third = state.payload['third']
    from_ = state.payload['from_']
    state_name = state.state.split(':')[1]

    room_number = message.text.upper()
    regexp = r'\d{1,5}(-[A-B])?'
    if room_number == 'НАЗАД':
        if from_ == 'МСГ':
            return await get_first_number(message)
        elif from_ == 'second':
            await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.SECOND_NUMBER, first=first)
            return await get_second_number(message, back = True)
        elif from_ == 'third':
            await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.LAST_NUMBER, first=first, second=second)
            return await get_third_number(message, back = True)
        elif from_ == 'menu':
            return await neighbour_menu(message)
    if not re.match(regexp, room_number):
        return await get_room_number(message, True)

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

        if pre_room and pre_room != new_room:
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
    from_ = state.payload['from_']

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
                                  first=first, second=second, third=third, page=page, from_=from_)
    # await bot.api.messages.send(user_id=event.peer_id, keyboard=keyboard.get_keyboard(page), random_id=42)
    await event.edit_message(keyboard=keyboard.get_keyboard(page))
