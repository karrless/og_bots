import os
import random

import requests
from vkbottle import StatePeer
from vkbottle.bot import BotLabeler, rules, Message

from src.QA.methods import get_subtopics, get_topics, get_answer
from src.bot import bot, fsm
from src.bot.handlers.menu import faq_keys
from src.bot.keyboards import get_topics_keyboard, get_back_keyboard
from src.bot.keyboards.QA import get_subtopics_keyboard, get_answer_keyboard
from src.database import s_factory, Answer
from .menu import bl

bl_chat = BotLabeler()
bl_chat.auto_rules = [rules.PeerRule(from_chat=True)]
bl_QA = BotLabeler()
bl_QA.auto_rules = [rules.PeerRule(from_chat=False), rules.StateGroupRule(fsm.QA)]


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
            f'Чтоб задать вопрос по этой теме, нажми на соответсвующую кнопку или напиши "Свой вопрос"')
    return await message.answer(text, keyboard=keyboard)


@bl_QA.message(state=fsm.QA.TOPIC)
async def get_answer_handler(message: Message, is_no_subtopic=False):
    if message.text.lower() == 'назад':
        return await faq_keys(message)
    state: StatePeer = await bot.state_dispenser.get(message.peer_id)
    topic = state.payload.get('topic')
    if message.text.lower() == 'свой вопрос':
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
    if message.text.lower() != 'свой вопрос':
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
    text = (f'Поступил новый вопрос от @{user.screen_name} ({user.first_name} {user.last_name}) по теме "{topic}":\n\n'
            f'{message.text}')
    if os.getenv('MODER_CHAT'):
        await bot.api.messages.send(peer_id=os.getenv('MODER_CHAT_ID'), message=text, attachment=message.attachments,
                                    random_id=random.randint(1, message.peer_id))
    requests.post('https://api.vk.com/method/messages.sendReaction',
                  data={'peer_id': message.peer_id,
                        'cmid': message.conversation_message_id,
                        'reaction_id': 39,
                        'access_token': os.getenv('VK_API1'),
                        'v': '5.199'})


@bl_chat.message(command='test')
async def test(message: Message):
    return await message.answer(message=message.peer_id)
