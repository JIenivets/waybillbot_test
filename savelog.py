import datetime
from datetime import timedelta


def alllog(type, message, answer=None):
    time = (datetime.datetime.now() + timedelta(hours=3)).strftime("%d-%m-%Y %H:%M")
    with open('allprintlog.txt', 'a', encoding="utf8") as allfile:
        print(time, f"{type}:", f"{message}", file=allfile)

    if "message" in type:
        dialog(type, time, message, answer)
    elif "forsaveindb" in type:
        forsaveindblog(type, time, message)
    elif "new_row" in type:
        newrowlog(type, time, message)


def dialog(type, time, message, answer):
    with open('dialog.txt', 'a', encoding="utf8") as dialogfile:
        if "user" in type:
            print(time,
                  f"Пользователь {message.from_user.first_name} ({message.from_user.id}) написал: {message.text}", file=dialogfile)
        elif "bot" in type:
            print(time,
                  f"Бот ответил {answer[0]} ({answer[1]}): {message}", file=dialogfile)


def forsaveindblog(type, time, message):
    with open('forsaveindblog.txt', 'a', encoding="utf8") as forsaveindbfile:
        print(time,
              f"{type}: {message}", file=forsaveindbfile)


def newrowlog(type, time, message):
    with open('/newrowlog.txt', 'a', encoding="utf8") as newrowfile:
        print(time,
              f"{type}: {message}", file=newrowfile)