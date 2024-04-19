import logging
import os
from dotenv import load_dotenv

load_dotenv()

import src.database as db

logging.basicConfig(level=logging.DEBUG, filename='log.log', filemode='w',
                    format='%(asctime)s: %(levelname)s — %(message)s')

DEBUG = int(os.getenv('DEBUG'))


if __name__ == '__main__':
    if DEBUG:
        # db.drop_all()
        db.create()
    db.connect()
