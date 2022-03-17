import sqlite3
import sys

import forsaveindb
import preparationforloadinginGoogleSheets
import run


def db():
    con = sqlite3.connect("waybillnumbers_db.db")
    return con, con.cursor()


def generate(type):
    con, cur = db()
    # Выполнение запроса и получение всех результатов
    result = cur.execute(f"""SELECT number FROM {type}""").fetchall()[-1]
    con.close()
    return int(result[0]) + 1


def addmileage(user_tg_id, mileage, type):
    con, cur = db()
    result = cur.execute(f"""SELECT count_mileage FROM {forsaveindb.return_value_from_json(user_tg_id, 'type')}
                    WHERE gos_number = '{forsaveindb.return_value_from_json(user_tg_id, "gos_number")}' """).fetchall()
    print("result:", result)
    if len(result) == 0:
        forsaveindb.fourth_mileage(user_tg_id, mileage)
        return True
    else:
        if result[-1][0] < int(mileage):
            forsaveindb.fourth_mileage(user_tg_id, mileage)
            return True
        else:
            return False


def load_in_db(json):
    if json["tg_id"] != "574802415":
        con, cur = db()

        cur.execute(f"""INSERT INTO {json["type"]} (number, tg_id, name, time, date, gos_number, city, count_mileage, check_out_time,
                        technical_inspection_time, medical_examination_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (json["number"], json["tg_id"], json["name"], json["time"], json["date"], f'{json["brand"]} {json["model"]} {json["gos_number"]}',
                     json["city"], json["count_mileage"], json["check_out_time"], json["technical_inspection_time"],
                     json["medical_examination_time"]))
        con.commit()
    preparationforloadinginGoogleSheets.display_new_row_in_googlesheelts(json)
    forsaveindb.db_clear(json["tg_id"])


def get_value(table_name, column_name, where):
    con, cur = db()
    # Выполнение запроса и получение всех результатов
    result = cur.execute(f"""SELECT {column_name} FROM {table_name} WHERE {where}""").fetchall()[-1]
    con.close()
    return result

def remove_from_db(command):
    con, cur = db()
    command = command.split()
    if 'last' in command:
        cur.execute("""DELETE FROM main WHERE  tbl_id = (SELECT Max(tbl_id) FROM main) """)
        con.commit()
        return "BloodTrail"
    else:
        if len(command) == 3:
            cur.execute(f"""DELETE FROM main 
                            WHERE tbl_id = (SELECT Max(tbl_id) FROM main WHERE  {command[1]} = {command[2]} )""")
            con.commit()
            return "BloodTrail"
        else:
            return "Не указан объект удаления❌"


def update_db(command):
    con, cur = db()
    command = command.split()
    print(command)
    print(command[2:-1])
    if len(command) > 1:
        try:
            cur.execute(f"""UPDATE main 
                            SET {command[1]} = '{' '.join(command[2:-1])}'
                            WHERE number = {command[-1]}""")
            con.commit()
            return "Данные обновлены✅"
        except:
            print('update_db.' + str(sys.exc_info()[0]) + ':', sys.exc_info()[1])
            return "Не достаточно данных❌"
    else:
        return "Не достаточно данных❌"


def parsing_caranddrivers_list():
    con, cur = db()
    cur.execute("DELETE FROM cars")
    cur.execute("DELETE FROM drivers")
    con.commit()
    for table in ['cars', 'drivers']:
        if table == 'cars':
            json = run.gettable('COLUMNS', 'Список автомобилей!A2:E')
            print(json)
            for row_index in range(len(json[0])):
                short_number = json[0][row_index]
                brand = json[1][row_index]
                model = json[2][row_index]
                number = json[3][row_index]
                garage_number = json[4][row_index]
                cur.execute(f"""INSERT INTO {table} (short_number, brand, model, number, garage_number)
                            VALUES (?, ?, ?, ?, ?)""",
                            (short_number, brand, model, number, garage_number))
                con.commit()
                print(short_number, brand, model, number, garage_number, end=" | ")
        elif table == 'drivers':
            json = run.gettable('COLUMNS', 'Список водителей!A2:C')
            for row_index in range(len(json[0])):
                tg_id = json[0][row_index]
                full_name = json[1][row_index]
                tabel_number = json[2][row_index]
                cur.execute(f"""INSERT INTO {table} (tg_id, full_name, tabel_number)
                            VALUES (?, ?, ?)""",
                            (tg_id, full_name, tabel_number))
                con.commit()
                print(tg_id, full_name, tabel_number, end=" | ")


def name(tg_id, name):
    try:
        con, cur = db()
        return cur.execute(f"""SELECT full_name, tabel_number FROM drivers WHERE tg_id == {tg_id}""").fetchall()[0]
    except IndexError:
        return name + " (no data)", "(tabel_number no data)"


def gos(short_number):
    try:
        con, cur = db()
        return cur.execute(f"""SELECT brand, model, number, garage_number FROM cars WHERE short_number == {short_number}""").fetchall()[0]
    except IndexError:
        return "(brand no data)", "(model no data)", str(short_number), "(garage_number no data)"


def new_name(tg_id, name):
    con, cur = db()
    cur.execute(f"""INSERT INTO drivers (tg_id, full_name)
                    VALUES (?, ?)""", (tg_id, name))
    con.commit()
