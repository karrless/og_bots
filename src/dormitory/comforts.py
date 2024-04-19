from src.database.models import Comfort
import src.database as db

arr = [
    '1-1', '1-2-1', '1-2-2', '1-3-1', '1-3-2', '1-4', '1-5', '1-6', '1-7', '1-8-1', '1-8-2', '1-9-1',
    '1-9-2',
    '1-10-1',
    '1-10-2',
    '1-11-1',
    '1-11-2',
    '1-12-1',
    '1-12-2',
    '2-1',
    '2-2',
    '2-3',
    '2-4',
    '2-5',
    '3-1',
    '3-2',
    '3-3',
    '3-4-1',
    '3-4-2',
    '3-5-1',
    '3-5-2',
    '3-5-3',
    '3-7',
    '4-1-1',
    '4-1-2',
    '5-1',
    '5-2',
    '5-3',
    '5-4',
    '8-1',
    '8-2',
    '8-3',
    '10-1',
    '10-2',
    '10-3',
    'МСГ']


def add_comforts():
    for c in arr:
        if c == 'МСГ':
            db.write(Comfort(name=c, first=c))
            continue
        comforts = list(map(int, c.split('-')))
        comfort = 0
        if len(comforts) == 2:
            comfort = Comfort(name=c, first=str(comforts[0]), second=comforts[1])
        elif len(comforts) == 3:
            comfort = Comfort(name=c, first=str(comforts[0]), second=comforts[1], third=comforts[2])
        db.write(comfort)
