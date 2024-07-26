from vkbottle import BaseStateGroup


class Menu(BaseStateGroup):
    MAIN = 0


class Dormitory(BaseStateGroup):
    MENU = 'menu'
    NEW = 'new'

    FIRST_NUMBER = 'first number'

    SECOND_NUMBER = 'second number'

    LAST_NUMBER = 'last number'

    SELECT_ROOM = 'select room'

    GET_NEW_ROOM = 'get new room'

    SET_NEW_ROOM = 'set new room'


class QA(BaseStateGroup):
    MENU = 'menu'

    TOPIC = 'topic'

    ANSWER = 'answer'

    QUESTION = 'question'
