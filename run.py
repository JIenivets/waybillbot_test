from pprint import pprint
from time import sleep
import httplib2
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.credentials import Credentials


# Файл, полученный в Google Developer Console
CREDENTIALS_FILE = 'creds.json'
# ID Google Sheets документа (можно взять из его URL)
spreadsheet_id_list = {
    "truck": '1TAQv8Q--Fzl5yBTItljsDlvwn2_Haxq3dj49neCGlWc',
    "car": '1P90jc_CEYtcyhE1_VKgJLA0YVAVTSgcnq1dPZwB1mbI'
}
# Авторизуемся и получаем service — экземпляр доступа к API
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = googleapiclient.discovery.build('sheets', 'v4', http=httpAuth)
service2 = googleapiclient.discovery.build('drive', 'v3', http=httpAuth)


def gettable(majorDimension, range, type='truck'):
    # Пример чтения файла
    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id_list[type],
        range=range,
        majorDimension=majorDimension
    ).execute()
    return values["values"]
# gettable('ROWS', '(Test) Вывод базы данных!A2:L')


def parsing_sheet_fron_googlesheets(range):
    # Пример чтения файла
    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range,
        majorDimension='COLUMNS'
    ).execute()
    # print('parsing_sheet_fron_googlesheets:')
    # pprint(values)
    return values


def load_db_in_sheets(past, type='truck'):
    # Пример записи в файл
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id_list[type],
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [past]
        }
    ).execute()


def insert_rows(startindex, count):
    global spreadsheet_id
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            'requests': {
                'insertDimension': {
                    'range': {
                        'sheetId': '1039072018',
                        'dimension': 'ROWS',
                        'startIndex': startindex,
                        'endIndex': startindex + count
                    }
                }
            }
        }
    ).execute()


def delete_rows(count):
    global spreadsheet_id
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            'requests': [
                {
                    "deleteDimension": {
                        "range": {
                            "sheetId": '1039072018',
                            "dimension": "ROWS",
                            "startIndex": 2,
                            "endIndex": count
                        }
                    }
                }
            ]
        }
    ).execute()


def upload_files():
    # file = service2.files().create(
    #     body={
    #         'name': 'zk.jpg',
    #         'perents': '1LAKtS-ghip8IRaf4741XJTfzIp7v1UqP'
    #     },
    #     media_body= MediaFileUpload(f'D:/zk.jpg', mimetype='image/jpg'),
    #     fields='id'
    # ).execute()
    results = service2.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    return results


def aaa(past):
    # Пример записи в файл
    service.spreadsheets().values().batchUpdate(
        spreadsheetId='1vWjXuTeGrnsTkLoClg8YC30F3ilyRWifkJ-orE0Ug3s',
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [past]
        }
    ).execute()


from sys import stdin
# a = [x.replace(' : ', ':').split() for x in input().split('\n')]

empty_form = {
    "range": "Ларькова Оксана  26.11.21-24.02.22!A2:U",
    "majorDimension": "ROWS",
    "values": [[]]
  }

a=[]
for x in stdin:
    a.append(x.replace(' : ', ':').split())
print(a)
empty_form['values'] = a
aaa(empty_form)