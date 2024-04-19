from dotenv import load_dotenv

load_dotenv()


if __name__ == '__main__':
    import logging
    import os
    import src.database as db

    logging.basicConfig(level=logging.DEBUG, filename='log.log', filemode='w',
                        format='%(asctime)s: %(levelname)s — %(message)s')

    DEBUG = int(os.getenv('DEBUG'))

    if DEBUG:
        # db.drop_all()
        db.create()
        db.connect()
        # from src.dormitory.comforts import add_comforts
        # add_comforts()
    else:
        db.connect()
