from dotenv import load_dotenv


load_dotenv()


if __name__ == '__main__':
    import os
    import src.database as db
    from src.bot import bot
    from loguru import logger

    logger.remove()

    DEBUG = int(os.getenv('DEBUG'))

    if DEBUG:
        # db.drop_all()
        # db.create()
        db.connect()
        # from src.dormitory.comforts import add_comforts
        # add_comforts()
        logger.add('log.log', level="DEBUG")
    else:
        db.connect()
        logger.add('log.log', level="INFO")
    bot.run_forever()

