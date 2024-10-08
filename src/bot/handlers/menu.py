import os
import random

from dotenv import set_key
from vkbottle import GroupEventType
from vkbottle.bot import BotLabeler, rules, Message, MessageEvent


from src.bot import bot, fsm
from src.bot.keyboards import get_main_menu_keyboard, get_dorm_menu_keyboard, get_topics_keyboard, get_back_keyboard
from src.bot.methods import get_user
from src.database import s_factory
from src.database.models import User, Question

bl = BotLabeler()
bl.auto_rules = [rules.PeerRule(from_chat=False)]
bl.vbml_ignore_case = True
bl_help = BotLabeler()
bl_help.auto_rules = [rules.PeerRule(from_chat=False)]


@bl.message(text=('Начать', 'Start', 'Обратно в меню'))
@bl_help.message()
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
    text = (f'Окей, Горный!\n'
            f'Я могу тебе помочь ответить на интересующие тебя вопросы'
            f'{"." if not os.getenv("IS_DORM") else ", а также найти твоих соседей по общежитию."}\n\n'
            f'Выберите категорию вопроса из списка ниже. Если не нашли нужный ответ, нажмите "Свой вопрос".')
    return await message.answer(text, keyboard=get_main_menu_keyboard(admin))


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


@bl.message(text='Отправить_всем-общажникам:)')
async def msg_all_dorm(message: Message):
    await bot.state_dispenser.set(message.peer_id, fsm.Admin.SEND_DORM)
    return await message.answer(message="Напиши, что ты хочешь всем отправить",
                                keyboard=get_back_keyboard())


@bl.message(state=fsm.Admin.SEND_DORM)
async def msg_all_dorm_send(message: Message):
    if message.text.lower() in ['назад', 'обратно в меню']:
        return await start_message(message)
    await start_message(message)
    with s_factory() as session:
        users: list[User] = session.query(User).where(User.room_id != None).all()
    for user in users:
        await bot.api.messages.send(peer_id=user.peer_id,
                                    message=message.text,
                                    random_id=random.randint(1, user.peer_id))



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
