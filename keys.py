import json
from pprint import pprint

db = {}


# Функция для открытия json файла и записи его в db
def db_open():
    global db
    with open('keys.json') as f:
        db = json.load(f)


# Функция для открытия json файла и записи db в его
def db_close():
    global db
    with open('keys.json', 'w') as file:
        json.dump(db, file)


def return_keys(user_tg_id):
    global db
    user_tg_id = str(user_tg_id)
    db_open()
    return db.get(user_tg_id)


def new_user(user_tg_id):
    global db
    user_tg_id = str(user_tg_id)
    db_open()
    db[user_tg_id] = {'key': None, 'type': [], 'cooldown': None, 'permissions': []}
    pprint(db)
    db_close()


def set_key(user_tg_id, key, type=None):
    global db
    user_tg_id = str(user_tg_id)
    db_open()
    if key == "end":
        db[user_tg_id]['key'] = None
    else:
        if type is not None:
            db[user_tg_id]['type'] = type
        db[user_tg_id]['key'] = key
    pprint(db)
    db_close()


def set_cd(user_tg_id, time):
    global db
    user_tg_id = str(user_tg_id)
    db_open()
    db[user_tg_id]['cooldown'] = time
    db_close()


def set_parametr(user_tg_id, parametr, value):
    global db
    user_tg_id = str(user_tg_id)
    db_open()
    db[user_tg_id][parametr] = value
    db_close()
