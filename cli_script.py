import json
import argparse
import requests
from requests.exceptions import ConnectionError

DEFAULT_API_ROOT = 'http://127.0.0.1:5000/api'


def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('command',
                        help='Метод, который необходимо вызвать. Поддерживаемые команды: create, edit, delete, get, get_all',
                        nargs='?')
    parser.add_argument('-f', '--file', help='Текстовый json файл с входными данными')
    parser.add_argument('-a', '--api_root', default=DEFAULT_API_ROOT, help='Корневой адрес API')
    parser.add_argument('-i', '--id',
                        help='Идентификатор встречи. Обязателен для методов изменения/удаления/получения (edit, delete, get)')
    parser.add_argument('-p', '--page',
                        help='Номер страницы. По умолчанию равен 0', default=0)
    parser.add_argument('-s', '--page_size',
                        help='Размер страницы. По умолчанию равен 50', default=50)
    return parser


def get_all_meetings(page, page_size, api_root=DEFAULT_API_ROOT):
    try:
        r = requests.get(f'{api_root}/meetings/get?page={page}&page_size={page_size}')
    except ConnectionError:
        print('Connection error')
        return
    print(r.json())


def edit_meeting(meeting_id, filename, api_root=DEFAULT_API_ROOT):
    data_json = json.load(open(filename, 'r'))
    try:
        r = requests.patch(f'{api_root}/meeting/edit/{meeting_id}',
                           json=data_json)
    except ConnectionError:
        print('Connection error')
        return
    print(r.json())


def create_meeting(filename, api_root=DEFAULT_API_ROOT):
    data_json = json.load(open(filename, 'r'))
    try:
        r = requests.post(f'{api_root}/meeting/create',
                          json=data_json)
    except ConnectionError:
        print('Connection error')
        return
    print(r.json())


def delete_meeting(meeting_id, api_root=DEFAULT_API_ROOT):
    try:
        r = requests.delete(f'{api_root}/meeting/delete/{meeting_id}')
    except ConnectionError:
        print('Connection error')
        return
    print(r.json())


def get_meeting(meeting_id, api_root=DEFAULT_API_ROOT):
    try:
        r = requests.get(f'{api_root}/meeting/get/{meeting_id}')
    except ConnectionError:
        print('Connection error')
        return
    print(r.json())


if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args()

    api_root = namespace.api_root if namespace.api_root else DEFAULT_API_ROOT
    if namespace.command == 'create':
        if not namespace.file:
            print('Параметр -f не указан')
        else:
            create_meeting(namespace.file, api_root)

    elif namespace.command == 'edit':
        if not namespace.id:
            print('Параметр -i не указан')
        elif not namespace.file:
            print('Параметр -f не указан')
        else:
            edit_meeting(namespace.id, namespace.file, api_root)

    elif namespace.command == 'delete':
        if not namespace.id:
            print('Параметр -i не указан')
        else:
            delete_meeting(namespace.id)

    elif namespace.command == 'get':
        if not namespace.id:
            print('Параметр -i не указан')
        else:
            get_meeting(namespace.id)

    elif namespace.command == 'get_all':
        page = namespace.page if namespace.page else 0
        page_size = namespace.page_size if namespace.page_size else 50

        get_all_meetings(page, page_size, namespace.api_root)

    else:
        print('Команда не поддерживается. Список доступных команд: -h')
