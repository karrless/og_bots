from vkbottle.bot import BotLabeler, rules, Message

bl = BotLabeler()
bl.auto_rules = [rules.PeerRule(from_chat=False)]


@bl.message(text=('Начать', 'Start'))
def start_message(message: Message):
    return message.answer('Привет, епта')
