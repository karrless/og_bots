from vkbottle import ConsistentTokenGenerator, Bot, API, BuiltinStateDispenser
import os

from .handlers import labelers

token_generator = ConsistentTokenGenerator([os.getenv('VK_API1'), os.getenv('VK_API2')])

api = API(token_generator)
state_dispenser = BuiltinStateDispenser()
bot = Bot(api=api, state_dispenser=state_dispenser)
for labeler in labelers:
    bot.labeler.load(labeler)
