from vkbottle.bot import BotLabeler, rules, Message

from src.bot import bot, fsm
from src.bot.keyboards import main_menu_keyboard, dorm_menu_keyboard, start_dorm_keyboard
from src.bot.methods import get_user, create_user
from src.database.models import User
from src.dormitory.methods import get_neighbours

bl = BotLabeler()
bl.auto_rules = [rules.PeerRule(from_chat=False)]


@bl.message(text=('Начать', 'Start', 'Обратно в меню'))
async def start_message(message: Message):
    await bot.state_dispenser.set(message.peer_id, fsm.Menu.MAIN)
    if not get_user(message.peer_id):
        user = (await bot.api.users.get(message.peer_id, fields=['screen_name']))[0]
        create_user(message.peer_id, user.screen_name, user.first_name, user.last_name)
    return await message.answer(f'Привет, чмоня!', keyboard=main_menu_keyboard)


@bl.message(text='Найти соседей')
async def neighbour_menu(message: Message):
    user: User = get_user(message.peer_id)
    text = ''
    if user.room_id:
        await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.MENU)
        keyboard = dorm_menu_keyboard
        neighbours: list[User] = get_neighbours(user.room)
        if len(neighbours) > 1:
            text += f'{user.room.comfort_name}: {user.comfort.title}, комната {user.room.number}\n'
            text += 'Твои соседи:\n\n'
            for neighbour in neighbours:
                if neighbour.peer_id != user.peer_id:
                    add_info = '' if not neighbour.group else f'({neighbour.faculty} - {neighbour.group})'
                    text += f'{neighbour.surname} {neighbour.name} {add_info} @{neighbour.screen_name}\n'
            text += '\n'
        else:
            text = 'Пока соседей нет.\n\n'
        text += 'Возможно не все ещё зарегистрировались. Если появятся соседи - тебе придет сообщение'
    else:
        await bot.state_dispenser.set(message.peer_id, fsm.Dormitory.NEW)
        keyboard = start_dorm_keyboard
        text = ('Я пока не знаю, какое у тебя общежитие.\n\n'
                'Напиши "Указать жильё" или нажми соответсвующую кнопку.')
    return await message.answer(text, keyboard=keyboard)
