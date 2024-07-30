import os
import random
from typing import Optional

from sqlalchemy import desc
# import requests
from vkbottle import StatePeer, EMPTY_KEYBOARD
from vkbottle.bot import BotLabeler, rules, Message, MessageEvent
from vkbottle_types.events import GroupEventType

from src.QA.methods import get_subtopics, get_topics, get_answer
from src.bot import bot, fsm
from src.bot.handlers.menu import faq_keys, start_message
from src.bot.keyboards import get_topics_keyboard, get_back_keyboard, get_main_menu_keyboard
from src.bot.keyboards.QA import get_subtopics_keyboard, get_answer_keyboard, get_question_keyboard, get_quit_keyboard
from src.database import s_factory, Answer
from src.database.models import Question

# from .menu import bl

bl_moder = BotLabeler()
bl_moder.auto_rules = [rules.PeerRule(from_chat=True)]
bl_moder.vbml_ignore_case = True

bl_QA = BotLabeler()
bl_QA.vbml_ignore_case = True
bl_QA.auto_rules = [rules.PeerRule(from_chat=False), rules.StateGroupRule(fsm.QA)]

bl_chat = BotLabeler()
bl_chat.vbml_ignore_case = True
bl_chat.auto_rules = [rules.PeerRule(from_chat=False), rules.StateRule(fsm.QA.CHAT), rules.StateRule(fsm.QA.CHAT)]


@bl_QA.message(state=fsm.QA.MENU)
async def subtopics_handler(message: Message):
    topic = message.text
    with s_factory() as session:
        if topic not in get_topics(session):
            return await message.answer('К сожалению, я тебя не понимаю.\nЕсли нет клавиатуры, напиши "Начать"',
                                        keyboard=get_topics_keyboard(os.getenv('IS_DORM')))
        subtopics = get_subtopics(session, topic)
        if not subtopics[0]:
            session.close()
            await bot.state_dispenser.set(message.peer_id, fsm.QA.ANSWER, topic=topic)
            return await get_answer_handler(message, is_no_subtopic=True)
    await bot.state_dispenser.set(message.peer_id, fsm.QA.TOPIC, topic=topic)
    keyboard = get_subtopics_keyboard(subtopics)
    text = (f'Вот ответы на распространённые вопросы по теме "{topic}".\n'
            f'Чтоб задать вопрос по этой теме, нажми на соответсвующую кнопку или напиши "Задать свой вопрос"')
    return await message.answer(text, keyboard=keyboard)


@bl_QA.message(state=fsm.QA.TOPIC)
async def get_answer_handler(message: Message, is_no_subtopic=False):
    if message.text.lower() == 'назад':
        return await faq_keys(message)
    state: StatePeer = await bot.state_dispenser.get(message.peer_id)
    topic = state.payload.get('topic')
    if message.text.lower() == 'задать свой вопрос':
        await bot.state_dispenser.set(message.peer_id, fsm.QA.QUESTION, topic=topic)
        return await get_question(message)
    subtopic = message.text
    with s_factory() as session:
        if not is_no_subtopic:
            if subtopic not in get_subtopics(session, topic):
                return await message.answer('К сожалению, я тебя не понимаю.\nЕсли нет клавиатуры, напиши "Начать"',
                                            keyboard=get_topics_keyboard(os.getenv('IS_DORM')))
        else:
            subtopic = None
        answer: Answer = get_answer(session, topic, subtopic)
    await bot.state_dispenser.set(message.peer_id, fsm.QA.ANSWER, topic=topic, subtopic=subtopic)
    text = answer.answer
    attachment = answer.attachment
    keyboard = get_answer_keyboard()
    return await message.answer(text, keyboard=keyboard, attachment=attachment)


@bl_QA.message(state=fsm.QA.ANSWER)
async def get_question(message: Message):
    state: StatePeer = await bot.state_dispenser.get(message.peer_id)
    topic = state.payload.get('topic')
    if message.text.lower() == 'назад':
        if not state.payload.get('subtopic'):
            return await faq_keys(message)
        message.text = topic
        return await subtopics_handler(message)
    if message.text.lower() != 'задать свой вопрос':
        return await message.answer('К сожалению, я тебя не понимаю.\nЕсли нет клавиатуры, напиши "Начать"',
                                    keyboard=get_answer_keyboard())
    await bot.state_dispenser.set(message.peer_id, fsm.QA.QUESTION, topic=topic)
    text = (f'Задай свой вопрос, и тебе ответят в ближайшее время.\n'
            f'Для того, чтоб вернуться нажми соответсвующую кнопку или напиши "Назад"')
    keyboard = get_back_keyboard()
    return await message.answer(text, keyboard=keyboard)


@bl_QA.message(state=fsm.QA.QUESTION)
async def write_question(message: Message):
    if message.text.lower() == 'назад':
        return await faq_keys(message)
    state: StatePeer = await bot.state_dispenser.get(message.peer_id)
    topic = state.payload.get('topic')
    user = (await bot.api.users.get(message.peer_id, fields=['screen_name']))[0]
    with s_factory() as session:
        session.add(Question(topic=topic,
                             peer_id=message.peer_id,
                             name=user.first_name,
                             surname=user.last_name,
                             question=message.text))
        session.commit()
        question = session.query(Question).where(Question.topic == topic,
                                                 Question.peer_id == message.peer_id,
                                                 Question.close == False).order_by(desc(Question.id)).first()

    text = f'Новый вопрос #{question.id} от @{user.screen_name} ({user.first_name} {user.last_name}) по теме "{topic}":'

    if os.getenv('MODER_CHAT'):
        await bot.api.messages.send(peer_id=os.getenv('MODER_CHAT_ID'), message=text,
                                    forward='{' + f'"peer_id":{message.peer_id},'
                                                  f'"conversation_message_ids":'
                                                  f'[{message.conversation_message_id}]' + '}',
                                    random_id=random.randint(1, message.peer_id),
                                    keyboard=get_question_keyboard(question.id))

    await bot.state_dispenser.set(message.peer_id, fsm.QA.CHAT, question_id=question.id)
    text = 'Мы приняли твой вопрос и в скором времени ответим!'
    await message.answer(text, keyboard=get_back_keyboard(back=False))
    text = ('Режим чата.\n\n'
            'В этом режиме ты сможешь вести диалог с модератором.\n'
            'Работают только команды "Начать" и "Обратно в меню", которые отключат этот режим и вопрос будет закрыт')
    await message.answer(text, keyboard=get_back_keyboard(back=False))
    # requests.post('https://api.vk.com/method/messages.sendReaction',
    #               data={'peer_id': message.peer_id,
    #                     'cmid': message.conversation_message_id,
    #                     'reaction_id': 10,
    #                     'access_token': os.getenv('VK_API1'),
    #                     'v': '5.199'})


@bl_moder.message(command='test')
async def test(message: Message):
    return await message.answer(message=message.peer_id)


@bl_moder.message(rules.VBMLRule('Закрыть <question_id>'))
@bl_moder.message(rules.VBMLRule('закрыть <question_id>'))
async def close_question(message: Message, question_id, mod_msg=True):
    with s_factory() as session:
        if not str(question_id).isdigit():
            return await message.answer(f'{question_id} не число')
        question: Optional[Question] = session.query(Question).where(Question.id == question_id).one()
        text = f'Вопрос #{question_id} закрыт!'
        if question:
            if question.close:
                return
            question.close = True
            session.add(question)
            session.commit()
            await bot.api.messages.send(peer_id=question.peer_id,
                                        message=f'Твой вопрос был закрыт модератором. Режим чата выключен.',
                                        random_id=random.randint(1, message.peer_id),
                                        keyboard=get_main_menu_keyboard())
            if os.getenv('IS_DORM'):
                await bot.state_dispenser.set(question.peer_id, fsm.Menu.MAIN)
            else:
                await bot.state_dispenser.set(question.peer_id, fsm.QA.MENU)
        else:
            text = f'Вопроса с номером #{question_id} не существует'
        if mod_msg:
            return await message.answer(text)


@bl_moder.raw_event(GroupEventType.MESSAGE_EVENT,
                    MessageEvent)
async def joke_button(event: MessageEvent):
    message = await bot.api.messages.get_by_conversation_message_id(event.peer_id,
                                                                    event.conversation_message_id)
    message = message.items[0]
    cmd = event.payload.get('cmd')
    question_id = event.payload.get('question_id')
    if cmd == 'close':
        text = f'Вопрос #{question_id} закрыт'
        text1 = text + ':'
        keyboard = EMPTY_KEYBOARD
    else:
        mod = (await bot.api.users.get(event.object.user_id, fields=['screen_name', 'sex']))[0]
        text = (f'Вопрос #{question_id} {"взял" if mod.sex == 2 else "взяла"} '
                f'@{mod.screen_name} ({mod.first_name} {mod.last_name})')
        text1 = text + ":"
        keyboard = get_question_keyboard(question_id)
    await bot.api.messages.edit(event.object.peer_id,
                                keep_forward_messages=1,
                                conversation_message_id=event.conversation_message_id,
                                message=text1,
                                keyboard=keyboard, random_id=random.randint(1, event.peer_id)
                                )
    await bot.api.messages.send(peer_id=event.peer_id, reply_to=message.id,
                                message=text,
                                random_id=random.randint(1, event.peer_id))
    if cmd == 'close':
        return await close_question(message, question_id, mod_msg=False)


@bl_chat.message(state=fsm.QA.CHAT)
async def ask_for_chat_off(message: Message):
    if message.text.lower() in ['обратно в меню', 'начать']:
        state = await bot.state_dispenser.get(message.peer_id)
        await bot.state_dispenser.set(message.peer_id, fsm.QA.QUIT, question_id=state.payload.get('question_id'))
        return await message.answer('Ты правда хочешь выйти из режима чата? В таком случае твой вопрос будет закрыт\n\n'
                                    'Если да, нажми соответствующую кнопку или напиши '
                                    '"Да, я хочу закрыть вопрос", в противном случае ответь что-угодно другое',
                                    keyboard=get_quit_keyboard())


@bl_chat.message(state=fsm.QA.QUIT)
async def chat_off(message: Message):
    state = await bot.state_dispenser.get(message.peer_id)
    question_id = state.payload.get('question_id')
    if message.text.lower() != 'да, я хочу закрыть вопрос':
        await bot.state_dispenser.set(message.peer_id, fsm.QA.CHAT, question_id=question_id)
        return await message.answer('Хорошо, в ближайшее время ты получишь ответ на свой вопрос',
                                    keyboard=get_back_keyboard(back=False))

    with s_factory() as session:
        question = session.query(Question).where(Question.id == question_id).one()
        question.close = True
        session.add(question)
        session.commit()
        if os.getenv('MODER_CHAT'):
            await bot.api.messages.send(peer_id=os.getenv('MODER_CHAT_ID'),
                                        message=f'Вопрос #{question.id} закрыт!',
                                        random_id=random.randint(1, message.peer_id))
        await message.answer('Твой вопрос закрыт. Режим чата выключен')
    return await start_message(message)

