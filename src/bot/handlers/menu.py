from vkbottle.bot import BotLabeler, rules, Message

from src.bot import bot, fsm
from src.bot.keyboards import main_menu_keyboard

bl = BotLabeler()
bl.auto_rules = [rules.PeerRule(from_chat=False)]


@bl.message(text=('Начать', 'Start'))
def start_message(message: Message):
    bot.state_dispenser.set(message.peer_id, fsm.Menu.MAIN)

    return message.answer('Привет, епта', keyboard=main_menu_keyboard)
