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
