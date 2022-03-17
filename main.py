import logging
from aiogram import Bot, types, executor, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

import keys, run, savelog, preparationforloadinginGoogleSheets, work_with_db, forsaveindb, statistics
from datetime import timedelta, datetime

import asyncio, aioschedule

logging.basicConfig(level=logging.INFO)
bot = Bot(token="1857693188:AAELRZ00g2A_lQaX5jx8ugw8W7FDA16-l7Y")
dp = Dispatcher(bot)

date_send_mileage = 20
cd_time = 1200
send_mileage_user_list = {}
button_names = {
    "get_number": 'Получить номер',
    "truck": 'Для грузового',
    "car": 'Для легкового',
    "send_mileage": 'Отправить пробег',
    "back": '<< Назад'
}

button_back = KeyboardButton(button_names['back'])
backKB = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
backKB.add(button_back)


# inline_btn_1 = InlineKeyboardButton('Принять', callback_data='accept')
# inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)


class LenError(Exception):
    pass


# команда /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):

    if str(message['from']["id"]) not in run.gettable("COLUMNS", "Список водителей!A2:A")[0]:   # проверяем есть ли пользователь в гугл таблице
        keys.new_user(message['from']["id"])  # добавляем нового ползователя в keys.json
        # если нет, то приветствуем и запрашиваем ФИО
        answer_text = 'Здравствуйте\nВведите своё  ФИО'
        await message.answer(answer_text)
        savelog.alllog("bot_message", answer_text,  # сохраняем лог
                       answer=(message.from_user.first_name, message.from_user.id))
        keys.set_key(message['from']["id"], "reg")  # устанавливаем ключ "регистрация"
    else:
        await message.answer(f'{message.from_user.full_name}, с возвращением', reply_markup=await keybord_generetion(message.from_user.id))


@dp.message_handler(commands=['mailing'])
async def mailing(message: types.Message):
    users = ["574802415", "54436582"]
    for us in users:
        await bot.send_message(us, 'Какой-то текст для теста рассылки👀')


@dp.message_handler(commands=['newuser'])
async def mailing(message: types.Message):
    settigs = message.text.split()
    # await message.answer(f'У пользователя {settigs[1]} параметр {settigs[2]} изменён с {keys.return_keys(settigs[1])[settigs[2]]} на {settigs[3:]} ✅')
    # keys.set_parametr(settigs[1], settigs[2], settigs[3:])
    await bot.send_message(settigs[1], 'Ваша заявка обратобана', reply_markup=await keybord_generetion(settigs[1]))


@dp.message_handler(commands=['status'])
async def status(message: types.Message):
    await message.answer(f"""===========  Статус  ===========\n
Количество новых сообщений: {statistics.stat['cout_new_messages']}\n
    Грузовых: {statistics.stat['truck']['number_of_new_messages']}
    Легковых: {statistics.stat['car']['number_of_new_messages']}\n
—————————————————————\n
Последнее:\n
    Грузовые:\n
        Номер: {statistics.stat['truck']['last_number']}
        Время получения: 
        {statistics.stat['truck']['time_last_message']}
        Имя: {statistics.stat['truck']['last_recipients_name']}\n
    Легковые:\n
        Номер: {statistics.stat['car']['last_number']}
        Время получения: 
        {statistics.stat['car']['time_last_message']}
        Имя: {statistics.stat['car']['last_recipients_name']}""")
    statistics.stat['cout_new_messages'] = 0


@dp.message_handler(commands=['test'])
async def test(message: types.Message):
    await bot.send_photo(message.from_user.id, 'asd')


# @dp.callback_query_handler(func=lambda c: c.data == 'accept')
# async def process_callback_button1(callback_query: types.CallbackQuery):
#     await bot.send_message(callback_query.from_user.id, 'Нажата первая кнопка!')


async def send_message(text_message=None, recipient='574802415', photo=None, keyboard=None):
    if photo is not None:
        await bot.send_photo(recipient, photo=open(f'photo/{photo}', 'rb'))

    if text_message is not None:
        await bot.send_message(recipient, text_message, reply_markup=keyboard)


async def keybord_generetion(tg_id, type="permissions", back_button=False):
    permission = keys.return_keys(tg_id)[type]
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for per in permission:
        kb.add(KeyboardButton(button_names[per]))
    if back_button:
        kb.add(KeyboardButton(button_names['back']))
    return kb


# основная функция, в которой проверяем наличие ключа и нажатие на кнопки клавиатуры
@dp.message_handler()
async def echo(message: types.Message):
    savelog.alllog("user_message", message)

    tg_id = message.from_user.id
    message_text = message.text
    message_datetime = message.date + timedelta(hours=3)
    user_key = keys.return_keys(tg_id)['key']

    if message_text in button_names.values():
        await keyboard_manager(message, tg_id, message_text, message_datetime)

    elif user_key is not None:
        await get_number(message, tg_id, user_key, message_text, message_datetime)

    else:
        await message.answer('Неизвестная команда🤷‍♂ ‍\nВыберите действие', reply_markup=await keybord_generetion(message.from_user.id))


# функция для работы с клавиатурой (смена, отслеживание)
async def keyboard_manager(message, tg_id, message_text, message_datetime):

    if message_text == button_names['get_number']:
        cooldown = await check_cd_for_number(keys.return_keys(tg_id)["cooldown"], message_datetime.time())
        if cooldown[0]:
            # await message.answer('Выберите для какого транспорта вы хотите получить номер', reply_markup=get_numberKB)
            number_types = keys.return_keys(tg_id)["type"]
            print(number_types)
            if len(number_types) > 1:
                await message.answer('Выберите для какого транспорта вы хотите получить номер', reply_markup=await keybord_generetion(tg_id, "type", True))
                keys.set_key(tg_id, 'waitmunbertype')
            else:
                await message.answer('Введите город', reply_markup=backKB)
                savelog.alllog("bot_message", 'Введите город', answer=(message.from_user.first_name, tg_id))
                forsaveindb.first_button(tg_id, message.from_user.full_name, number_types[0])
                keys.set_key(tg_id, 'city')
        else:
            await message.answer(f"Вы сможите получить номер через: {await seconds_to_cooldown_time(cooldown[1])}⏳",
                                 reply_markup=await keybord_generetion(tg_id))

    elif message_text in [button_names['truck'], button_names['car']]:
        await message.answer('Введите город', reply_markup=backKB)
        savelog.alllog("bot_message", 'Введите город', answer=(message.from_user.first_name, tg_id))

        if message_text == button_names['truck']:
            forsaveindb.first_button(tg_id, message.from_user.full_name, 'truck')
        elif message_text == button_names['car']:
            forsaveindb.first_button(tg_id, message.from_user.full_name, 'car')
        keys.set_key(tg_id, 'city')

    elif message_text == button_names['send_mileage']:
        if await check_date_2for_send_mileage(message_datetime.date(), tg_id):
            await message.answer('Отправьте фото пробега', reply_markup=backKB)
            keys.set_key(tg_id, "photo")
        else:
            await message.answer('Дождитесь 25ое число🗓', reply_markup=await keybord_generetion(tg_id))

    elif message_text == button_names['back']:
        await message.answer('Вы вывернулись в меню', reply_markup=await keybord_generetion(tg_id))
        keys.set_key(tg_id, "end")


# функция получения номера
async def get_number(message, tg_id, user_key, message_text, message_datetime):

    if user_key == "reg":  # если ключ "регистрация", то
        preparationforloadinginGoogleSheets.registration(tg_id, message.text)  # добавляем данные в таблицу Google
        work_with_db.new_name(tg_id, message_text)
        keys.set_key(tg_id, "end")  # сбрасываем ключ
        answer_text = 'Ваша заявка отвравлена. Как только её обработают, вам прдёт уведомление'
        await message.answer(answer_text)  # даём ответ
        await send_message(f'Новый пользователь!\nID: {tg_id}\nИмя: {message.text}\nДата: {message_datetime}')
        savelog.alllog("bot_message", answer_text,  # сохраняем лог
                       answer=(message.from_user.first_name, message.from_user.id))
        savelog.alllog("bot_message", f'Новый пользователь!\nID: {tg_id}\nИмя: {message.text}\nДата: {message_datetime}')  # сохраняем лог


# ----------------------------------------------------------------------------------------------------------------------

    # ПЕРВЫЙ ШАГ
    elif user_key == "city":    # если ключ "город", то
        forsaveindb.second_city(tg_id, message.text)  # сохраняем данные
        await message.answer('Город сохранён✅')     # отвечаем пользователю
        savelog.alllog("bot_message", 'Город сохранён✅',    # сохраняем лог
                       answer=(message.from_user.first_name, message.from_user.id))
        await message.answer('Введите только цифры гос.номера')     # запрашиваем гос.номер
        savelog.alllog("bot_message", 'Введите только цифры гос.номера',    # сохраняем лог
                       answer=(message.from_user.full_name, message.from_user.id))
        keys.set_key(tg_id, "gos")      # меняем ключ
        keys.set_cd(tg_id, str(message_datetime.time()))


    # ВТОРОЙ ШАГ
    elif user_key == "gos":     # если ключ "гос.номер", то
        try:
            if len(message.text) == 3:
                gosnumber = int(message.text)
                forsaveindb.thethird_gos(tg_id, gosnumber)    # сохраняем данные
                await message.answer('Номер добавлен✅')     # отвечаем пользователю
                savelog.alllog("bot_message", 'Номер добавлен✅',    # сохраняем лог
                               answer=(message.from_user.first_name, message.from_user.id))
                await message.answer('Отправьте текущий пробег автомобтля')     # отвечаем пользователю
                savelog.alllog("bot_message", 'Отправьте текущий пробег автомобтля',    # сохраняем лог
                               answer=(message.from_user.first_name, message.from_user.id))
                keys.set_key(tg_id, "taxotrof")     # меняем ключ
            else:
                raise LenError
        except ValueError:
            # отвечаем пользователю
            await message.answer('Не верный формат ввода❌\nВведите только цифры гос.номера\nПопроуйте ещё раз')
            savelog.alllog("bot_message",   # сохраняем лог
                           'Не верный формат ввода❌\nВведите только цифры гос.номера\nПопроуйте ещё раз',
                           answer=(message.from_user.first_name, message.from_user.id))
        except LenError:
            # отвечаем пользователю
            await message.answer('Не верный формат ввода❌\nНеобходимо ввести все 3 цифры гос.номера\nПопроуйте ещё раз')
            savelog.alllog("bot_message",   # сохраняем лог
                           'Не верный формат ввода❌\nНеобходимо ввести все 3 цифры гос.номера\nПопроуйте ещё раз',
                           answer=(message.from_user.first_name, message.from_user.id))

    # ТРЕТИЙ ШАГ
    elif user_key == "taxotrof":
        if work_with_db.addmileage(tg_id, message.text, keys.return_keys(tg_id)["type"]):
            await message.answer('Пробег сохранён✅')
            savelog.alllog("bot_message", 'Пробег сохранён✅',
                           answer=(message.from_user.first_name, message.from_user.id))
            keys.set_key(tg_id, "end")
            da = forsaveindb.fiveth_number(tg_id, message_datetime)
            savelog.alllog("bot_message",
                           f'Номер путевого листа: {da[0]} ✅ Время выезда: {da[1][:-3]} Время техосмотра: {da[2][:-3]} Время медосмотра: {da[3][:-3]} \n-',
                           answer=(message.from_user.first_name, message.from_user.id))
            await message.answer(
                f'Номер путевого листа: {da[0]} ✅\nВремя выезда: {da[1][:-3]}\nВремя техосмотра: {da[2][:-3]}\nВремя медосмотра: {da[3][:-3]}',
                reply_markup=await keybord_generetion(tg_id))

        else:
            await message.answer('Не верный формат ввода❌\nУказанный пробег меньше внесенного ранее\nПопроуйте ещё раз')
            savelog.alllog("bot_message",
                           'Не верный формат ввода❌\nУказанный пробег меньше внесенного ранее\nПопроуйте ещё раз',
                           answer=(message.from_user.first_name, message.from_user.id))


async def check_cd_for_number(user_cooldown, message_datetime):
    if user_cooldown is not None:
        user_cooldown =datetime.strptime(user_cooldown, '%H:%M:%S')
        message_datetime = datetime.strptime(str(message_datetime), '%H:%M:%S')
        difference = message_datetime - user_cooldown
        print(f'{message_datetime} - {user_cooldown} = {difference} | {difference.seconds}')
        if difference.seconds > cd_time:
            return True, None
        else:
            return False, cd_time - difference.seconds
    else:
        return True, None


async def check_date_2for_send_mileage(date, tg_id=0):
    if date.day == date_send_mileage or tg_id == 574802415:
        print(date, date_send_mileage)

        return True
    else:
        return False


async def seconds_to_cooldown_time(cooldown_seconds):
    minutes = cooldown_seconds // 60
    seconds = cooldown_seconds % 60
    if minutes > 0:
        return f"{minutes} минут {seconds} секунд"
    else:
        return f"{seconds} секунд"


@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message: types.Message):
    global send_mileage_user_list
    tg_id = message.from_user.id
    tg_datetime = message.date + timedelta(hours=3)
    if keys.return_keys(tg_id)['key'] == 'photo':
        print(f'photo:{message.from_user.full_name} {tg_datetime.date()} {str(tg_datetime.time()).replace(":", ".")}')
        await message.photo[-1].download(f'photo/{message.from_user.full_name} {tg_datetime.date()} {str(tg_datetime.time()).replace(":", ".")}.jpg')
        await message.answer('Фото получено✅', reply_markup=await keybord_generetion(tg_id))
        await send_message(f'Новое фото!\nId: {tg_id}\nИмя: {work_with_db.get_value("drivers", "full_name", f"tg_id == {tg_id}")}\nДата: {tg_datetime}', photo=f'{message.from_user.full_name} {tg_datetime.date()} {str(tg_datetime.time()).replace(":", ".")}.jpg')
        send_mileage_user_list[str(tg_id)] = True
        keys.set_key(tg_id, 'end')


async def send_alert():
    print("It's noon!")
    a = {'574802415': False}
    for us_id in a:
        if not send_mileage_user_list[us_id]:
            await send_message(f'Отправьте фото пробега🖼', us_id)


async def stop_send_alert():
    aioschedule.clear('alert')
    print('alert end')


async def start_alerts():
    global send_mileage_user_list
    if await check_date_2for_send_mileage((datetime.now()+timedelta(hours=3)).date()):
        keys.db_open()
        db = keys.db
        send_mileage_user_list = {x: False for x in db.keys() if 'send_mileage' in db[x]["permissions"]}

        print(send_mileage_user_list)
        # aioschedule.every(2).hours.at('19:40').do(send_alert).tag('alert')
        aioschedule.every().day.at('09:01').do(send_alert).tag('alert')
        aioschedule.every().day.at('11:01').do(send_alert).tag('alert')
        aioschedule.every().day.at('13:01').do(send_alert).tag('alert')
        aioschedule.every().day.at('15:01').do(send_alert).tag('alert')
        aioschedule.every().day.at('17:01').do(send_alert).tag('alert')
        aioschedule.every().day.at('19:01').do(send_alert).tag('alert')
        aioschedule.every().day.at('19:10').do(stop_send_alert).tag('alert')


async def scheduler():
    aioschedule.every().days.at('00:00').do(start_alerts)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(5)


async def on_startup(_):
    asyncio.create_task(scheduler())


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
