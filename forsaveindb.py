import json
from pprint import pprint
import work_with_db
from datetime import timedelta
from random import randint
import savelog
import statistics
db = {}


# Функция для открытия json файла и записи его в db
def db_open():
    global db
    with open('forsaveindb.json') as f:
        db = json.load(f)


# Функция для открытия json файла и записи db в его
def db_close():
    global db
    print("forsaveindb:", db)
    savelog.alllog("forsaveindb", db)
    with open('forsaveindb.json', 'w') as file:
        json.dump(db, file)


def db_clear(user_tg_id):
    global db
    del db[user_tg_id]
    db_close()


def return_value_from_json(user_tg_id, cell):
    global db
    db_open()
    user_tg_id = str(user_tg_id)
    return db[user_tg_id][cell]


def timing(tg_date):
    # tg_date += timedelta(hours=3)
    checkout_time = tg_date - timedelta(minutes=randint(10, 20))
    ot_time = checkout_time - timedelta(minutes=randint(10, 20))
    med_time = ot_time - timedelta(minutes=randint(27, 35))
    return str(tg_date.date()), str(tg_date.time()), str(checkout_time.time()), str(ot_time.time()), str(med_time.time())


def first_button(user_tg_id, name, type):
    global db
    db_open()
    name = work_with_db.name(user_tg_id, name)
    user_tg_id = str(user_tg_id)
    db[user_tg_id] = {"number": '',
                      "tg_id": user_tg_id,
                      "name": name[0],
                      "tabel_number": name[1],
                      "controller": 'Коротченко Владимир Александрович',
                      "time": '',
                      "date": '',
                      "brand": '',
                      "model": '',
                      "gos_number": '',
                      "garage_number": '',
                      "city": '',
                      "count_mileage": '',
                      "check_out_time": '',
                      "medical_examination_time": '',
                      "technical_inspection_time": '',
                      "checked": 'Исправен',
                      "type": type
                      }
    db_close()


def thethird_gos(user_tg_id, gosnumber):
    global db
    db_open()
    user_tg_id = str(user_tg_id)
    data = work_with_db.gos(gosnumber)
    db[user_tg_id]["brand"] = data[0]
    db[user_tg_id]["model"] = data[1]
    db[user_tg_id]["gos_number"] = data[2]
    db[user_tg_id]["garage_number"] = data[3]
    db_close()


def fourth_mileage(user_tg_id, mileage):
    global db
    db_open()
    user_tg_id = str(user_tg_id)
    db[user_tg_id]["count_mileage"] = mileage
    db_close()


def second_city(user_tg_id, city):
    global db
    db_open()
    user_tg_id = str(user_tg_id)
    db[user_tg_id]["city"] = city
    # db[user_tg_id]["type"] = type
    # work_with_db.load_in_db(db[user_tg_id])
    db_close()


def fiveth_number(user_tg_id, tg_date):
    global db
    db_open()
    user_tg_id = str(user_tg_id)
    number = work_with_db.generate(db[user_tg_id]["type"])
    db[user_tg_id]["number"] = number

    date, time, checkout_time, ot_time, med_time = timing(tg_date)
    db[user_tg_id]["date"] = date
    db[user_tg_id]["time"] = time
    db[user_tg_id]["check_out_time"] = checkout_time
    db[user_tg_id]["technical_inspection_time"] = ot_time
    db[user_tg_id]["medical_examination_time"] = med_time

    statistics.statistics(db[user_tg_id]["type"], number, f'{db[user_tg_id]["date"]} {db[user_tg_id]["time"]}', db[user_tg_id]["name"])

    db_close()
    return number, db[user_tg_id]["check_out_time"], db[user_tg_id]["technical_inspection_time"], db[user_tg_id]["medical_examination_time"], work_with_db.load_in_db(db[user_tg_id])
