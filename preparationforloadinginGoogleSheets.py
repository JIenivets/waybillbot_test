import json
import sqlite3
import run
import savelog
forms = {}
otvet = {}


def json_open():
    global forms
    with open('formsforinsertinsheet.json') as f:
        return json.load(f)


def preparation(parameter):
    forms = json_open()
    insert_type = forms[parameter]
    colums_name = insert_type["colums_name"]
    con = sqlite3.connect("waybillnumbers_db.db")
    cur = con.cursor()
    for count_colum_name in range(len(colums_name)):
        otvet = insert_type["form"][count_colum_name]
        for index_colum_name in range(len(colums_name[count_colum_name])):
            result = cur.execute(f"""SELECT {colums_name[count_colum_name][index_colum_name]} FROM main""").fetchall()[1:]
            for i in range(len(result)):
                otvet["values"][index_colum_name].append(str(result[i][0]))
        run.load_db_in_sheets(otvet)
    con.close()
    print(otvet)


def display_new_row_in_googlesheelts(data):
    settings = json_open()["addnewrows"]
    for settings_elem in settings:
        settings_elem = settings[settings_elem]
        form = json_open()["empty_form"]

        number_new_row = settings_elem["position"][1] + len(run.gettable("ROWS",
                                      settings_elem["sheel_name"]+settings_elem["position"][0]+str(settings_elem["position"][1])+settings_elem["position"][2], type=data["type"]))
        form["range"] = settings_elem["sheel_name"]+settings_elem["position"][0]+str(number_new_row)+settings_elem["position"][2]

        for colums_name in settings_elem["colums_name"]:
           form["values"][0].append(str(check_data(data, colums_name)))
        print(form)
        savelog.alllog("new_row", form)
        run.load_db_in_sheets(form, data["type"])


def check_data(data, colums_name):
    if colums_name == "car_fullname":
        return f'{data["brand"]} {data["model"]} {data["gos_number"]}'
    elif colums_name == "car_brandandmodel":
        return f'{data["brand"]} {data["model"]}'
    elif colums_name == "car_brandandgosnumber":
        return f'{data["brand"]} {data["gos_number"]}'
    elif colums_name == "datetime":
        return f'{data["date"]} {data["time"]}'
    elif colums_name == "datetextime":
        return f'{data["date"]} {data["technical_inspection_time"]}'
    elif colums_name == "datemedtime":
        return f'{data["date"]} {data["medical_examination_time"]}'
    elif colums_name == "dateouttime":
        return f'{data["date"]} {data["check_out_time"]}'
    else:
        return data[colums_name]


def registration(tg_id, name):
    data = [{
      "range": f"\u0421\u043F\u0438\u0441\u043E\u043A \u0432\u043E\u0434\u0438\u0442\u0435\u043B\u0435\u0439!A{len(run.gettable('ROWS', 'Список водителей!A2:B')) + 2}:B",
      "majorDimension": "ROWS",
      "values": [[tg_id, name]]
    }]
    run.load_db_in_sheets(data)

