from dotenv import load_dotenv


load_dotenv()


if __name__ == '__main__':
    import src.database as db
    from src.bot import bot
    from loguru import logger

    logger.remove()
    logger.add('log/{time}.log', level="INFO", rotation='12:00')
    db.create()
    db.connect()
    bot.run_forever()

