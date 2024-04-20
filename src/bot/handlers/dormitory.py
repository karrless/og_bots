from vkbottle.bot import BotLabeler, rules, Message

from src.bot import bot, fsm
from src.bot.keyboards import first_comfort_number_keyboard, get_numbers_keyboard
from src.bot.methods import get_user
from src.database.models import User, Comfort
from src.dormitory.methods import get_first_comfort_number, get_second_comfort_number, get_third_comfort_number, \
    get_comfort

bl = BotLabeler()
bl.auto_rules = [rules.StateGroupRule(fsm.Dormitory)]


@bl.message(text=('Указать жильё', 'Указать жилье'))
async def start_get_comfort(message: Message, _re: bool = False):
    await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.FIRST_NUMBER)
    text = 'Напиши первую цифру в комфортности или нажми соответсвующую кнопку:\n\nВ случае МСГ нажми МСГ'
    text = text if not _re else 'Вы ошиблись.\n' + text
    keyboard = first_comfort_number_keyboard
    return await message.answer(text, keyboard=keyboard)


@bl.message(state=fsm.Dormitory.FIRST_NUMBER)
async def get_second_comfort(message: Message, _re: bool = False):
    state = await bot.state_dispenser.get(message.peer_id)
    state = state.state.split(':')[1]
    if state == 'first number':
        first = message.text.upper()
        if first not in get_first_comfort_number():
            return await start_get_comfort(message, True)
        # TODO: МСГ сделать
        await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.SECOND_NUMBER, first=first)
    else:
        first = message.state_peer.payload['first']
    numbers = get_second_comfort_number(first)

    keyboard = get_numbers_keyboard(numbers)
    text = 'Напиши вторую цифру в комфортности или нажми соответствующую кнопку:'
    text = text if not _re else 'Вы ошиблись.\n'
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
        if second not in list(map(str, get_second_comfort_number(first))):
            return await get_second_comfort(message, True)
        await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.LAST_NUMBER, first=first, second=second)
    else:
        second = message.state_peer.payload['second']
    numbers = get_third_comfort_number(first, second)
    if not numbers:
        user: User = get_user(message.peer_id)
        comfort: Comfort = get_comfort(first, second)
        user.set_comfort(comfort)
        return await get_room(message)

    keyboard = get_numbers_keyboard(numbers)
    text = 'Напиши вторую цифру в комфортности или нажми соответствующую кнопку:'
    text = text if not _re else 'Вы ошиблись.\n'
    return await message.answer(text, keyboard=keyboard)


@bl.message(state=fsm.Dormitory.LAST_NUMBER)
async def get_room(message: Message, _re: bool= False):
    pass
